import Foundation
import GRDB

// MARK: - Queued Operation Model

/// Represents an operation queued for offline-first processing
struct QueuedOperation: Identifiable, Codable, Equatable {
    var id: String
    var operationType: OperationType
    var entityType: String
    var entityId: String
    var payloadJson: String
    var idempotencyKey: String
    var status: OperationStatus
    var attempts: Int
    var maxAttempts: Int
    var lastError: String?
    var nextRetryAt: Date?
    var createdAt: Date
    var processedAt: Date?
    
    init(
        id: String = UUID().uuidString,
        operationType: OperationType,
        entityType: String,
        entityId: String,
        payloadJson: String,
        idempotencyKey: String? = nil,
        status: OperationStatus = .pending,
        attempts: Int = 0,
        maxAttempts: Int = 5,
        lastError: String? = nil,
        nextRetryAt: Date? = nil,
        createdAt: Date = Date(),
        processedAt: Date? = nil
    ) {
        self.id = id
        self.operationType = operationType
        self.entityType = entityType
        self.entityId = entityId
        self.payloadJson = payloadJson
        // Generate deterministic idempotency key if not provided
        self.idempotencyKey = idempotencyKey ?? Self.generateIdempotencyKey(
            operationType: operationType,
            entityType: entityType,
            entityId: entityId
        )
        self.status = status
        self.attempts = attempts
        self.maxAttempts = maxAttempts
        self.lastError = lastError
        self.nextRetryAt = nextRetryAt
        self.createdAt = createdAt
        self.processedAt = processedAt
    }
    
    /// Generate a deterministic idempotency key
    static func generateIdempotencyKey(
        operationType: OperationType,
        entityType: String,
        entityId: String
    ) -> String {
        let source = "\(operationType.rawValue):\(entityType):\(entityId):\(Date().timeIntervalSince1970)"
        return source.data(using: .utf8)?.base64EncodedString() ?? UUID().uuidString
    }
    
    var canRetry: Bool {
        attempts < maxAttempts && status != .completed
    }
    
    var shouldRetryNow: Bool {
        guard canRetry else { return false }
        guard status == .failed else { return status == .pending }
        guard let nextRetry = nextRetryAt else { return true }
        return Date() >= nextRetry
    }
}

enum OperationType: String, Codable, DatabaseValueConvertible {
    case submitForm = "submit_form"
    case uploadEvidence = "upload_evidence"
    case updateClaim = "update_claim"
    case createInspection = "create_inspection"
    case updateInspection = "update_inspection"
    case deleteMedia = "delete_media"
}

enum OperationStatus: String, Codable, DatabaseValueConvertible {
    case pending = "pending"
    case processing = "processing"
    case completed = "completed"
    case failed = "failed"
}

extension QueuedOperation: FetchableRecord, PersistableRecord {
    static let databaseTableName = "queued_operations"
}

// MARK: - Operation Repository

/// Repository for QueuedOperations - manages the offline operation queue
@MainActor
final class OperationRepository {
    
    // MARK: - Singleton
    
    static let shared = OperationRepository()
    
    // MARK: - Properties
    
    private let database: DatabaseManager
    
    // MARK: - Initialization
    
    private init() {
        self.database = DatabaseManager.shared
    }
    
    // MARK: - Queue Operations
    
    /// Enqueue a new operation
    func enqueue(_ operation: QueuedOperation) async throws {
        // Check for existing operation with same idempotency key
        let existing = try await database.database.read { db in
            try QueuedOperation
                .filter(Column("idempotencyKey") == operation.idempotencyKey)
                .filter(Column("status") != OperationStatus.completed.rawValue)
                .fetchOne(db)
        }
        
        // If operation already exists and not completed, don't duplicate
        if existing != nil {
            AppLogger.sync.info("Operation with idempotency key already exists, skipping: \(operation.idempotencyKey, privacy: .public)")
            return
        }
        
        try await database.database.write { db in
            try operation.insert(db)
        }
    }
    
    /// Fetch all pending operations (ready to process)
    func fetchPending() async throws -> [QueuedOperation] {
        try await database.database.read { db in
            try QueuedOperation
                .filter(Column("status") == OperationStatus.pending.rawValue)
                .order(Column("createdAt").asc)
                .fetchAll(db)
        }
    }
    
    /// Fetch operations ready for retry
    func fetchReadyForRetry() async throws -> [QueuedOperation] {
        let now = Date()
        return try await database.database.read { db in
            try QueuedOperation
                .filter(Column("status") == OperationStatus.failed.rawValue)
                .filter(Column("attempts") < Column("maxAttempts"))
                .filter(Column("nextRetryAt") == nil || Column("nextRetryAt") <= now)
                .order(Column("createdAt").asc)
                .fetchAll(db)
        }
    }
    
    /// Fetch all failed operations
    func fetchFailed() async throws -> [QueuedOperation] {
        try await database.database.read { db in
            try QueuedOperation
                .filter(Column("status") == OperationStatus.failed.rawValue)
                .order(Column("createdAt").desc)
                .fetchAll(db)
        }
    }
    
    /// Fetch all operations (for sync status display)
    func fetchAll() async throws -> [QueuedOperation] {
        try await database.database.read { db in
            try QueuedOperation
                .filter(Column("status") != OperationStatus.completed.rawValue)
                .order(Column("createdAt").desc)
                .fetchAll(db)
        }
    }
    
    /// Fetch operation by ID
    func fetch(id: String) async throws -> QueuedOperation? {
        try await database.database.read { db in
            try QueuedOperation.fetchOne(db, key: id)
        }
    }
    
    /// Mark operation as processing
    func markProcessing(id: String) async throws {
        try await database.database.write { db in
            try db.execute(
                sql: "UPDATE queued_operations SET status = ?, attempts = attempts + 1 WHERE id = ?",
                arguments: [OperationStatus.processing.rawValue, id]
            )
        }
    }
    
    /// Mark operation as completed
    func markCompleted(id: String) async throws {
        try await database.database.write { db in
            try db.execute(
                sql: "UPDATE queued_operations SET status = ?, processedAt = ? WHERE id = ?",
                arguments: [OperationStatus.completed.rawValue, Date(), id]
            )
        }
    }
    
    /// Mark operation as failed with retry scheduling
    func markFailed(id: String, error: String, nextRetryDelay: TimeInterval) async throws {
        let nextRetryAt = Date().addingTimeInterval(nextRetryDelay)
        try await database.database.write { db in
            try db.execute(
                sql: "UPDATE queued_operations SET status = ?, lastError = ?, nextRetryAt = ? WHERE id = ?",
                arguments: [OperationStatus.failed.rawValue, error, nextRetryAt, id]
            )
        }
    }
    
    /// Reset a failed operation for immediate retry
    func resetForRetry(id: String) async throws {
        try await database.database.write { db in
            try db.execute(
                sql: "UPDATE queued_operations SET status = ?, lastError = NULL, nextRetryAt = NULL WHERE id = ?",
                arguments: [OperationStatus.pending.rawValue, id]
            )
        }
    }
    
    /// Delete completed operations older than specified days
    func cleanupCompleted(olderThanDays: Int = 7) async throws {
        let cutoffDate = Calendar.current.date(byAdding: .day, value: -olderThanDays, to: Date())!
        try await database.database.write { db in
            try db.execute(
                sql: "DELETE FROM queued_operations WHERE status = ? AND processedAt < ?",
                arguments: [OperationStatus.completed.rawValue, cutoffDate]
            )
        }
    }
    
    // MARK: - Statistics
    
    /// Get operation counts by status
    func countByStatus() async throws -> [OperationStatus: Int] {
        try await database.database.read { db in
            var counts: [OperationStatus: Int] = [:]
            for status in [OperationStatus.pending, .processing, .completed, .failed] {
                let count = try QueuedOperation
                    .filter(Column("status") == status.rawValue)
                    .fetchCount(db)
                counts[status] = count
            }
            return counts
        }
    }
    
    /// Get total pending count
    func pendingCount() async throws -> Int {
        try await database.database.read { db in
            try QueuedOperation
                .filter(Column("status") == OperationStatus.pending.rawValue)
                .fetchCount(db)
        }
    }
    
    /// Get total failed count
    func failedCount() async throws -> Int {
        try await database.database.read { db in
            try QueuedOperation
                .filter(Column("status") == OperationStatus.failed.rawValue)
                .fetchCount(db)
        }
    }
}
