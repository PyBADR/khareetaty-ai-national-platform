import Foundation
import GRDB

// MARK: - Sync Status

enum SyncStatus: String, Codable, CaseIterable, DatabaseValueConvertible {
    case pending = "pending"
    case uploading = "uploading"
    case synced = "synced"
    case failed = "failed"
    
    var displayName: String {
        switch self {
        case .pending: return "Pending"
        case .uploading: return "Uploading"
        case .synced: return "Synced"
        case .failed: return "Failed"
        }
    }
    
    var iconName: String {
        switch self {
        case .pending: return "clock"
        case .uploading: return "arrow.up.circle"
        case .synced: return "checkmark.circle.fill"
        case .failed: return "exclamationmark.circle.fill"
        }
    }
}

// MARK: - Sync Operation

enum SyncOperation: String, Codable, DatabaseValueConvertible {
    case create = "create"
    case update = "update"
    case delete = "delete"
}

// MARK: - Sync Entity Type

enum SyncEntityType: String, Codable, DatabaseValueConvertible {
    case claim = "claim"
    case inspection = "inspection"
    case inspectionField = "inspection_field"
    case mediaAsset = "media_asset"
}

// MARK: - Sync Queue Item

struct SyncQueueItem: Identifiable, Codable, Equatable {
    var id: String
    var deviceId: String
    var entityType: SyncEntityType
    var entityId: String
    var operation: SyncOperation
    var payloadJson: String
    var attempts: Int
    var maxAttempts: Int
    var lastError: String?
    var createdAt: Date
    var processedAt: Date?
    var idempotencyKey: String?
    var nextRetryAt: Date?
    
    init(
        id: String = UUID().uuidString,
        deviceId: String,
        entityType: SyncEntityType,
        entityId: String,
        operation: SyncOperation,
        payloadJson: String,
        attempts: Int = 0,
        maxAttempts: Int = 10,
        lastError: String? = nil,
        createdAt: Date = Date(),
        processedAt: Date? = nil,
        idempotencyKey: String? = nil,
        nextRetryAt: Date? = nil
    ) {
        self.id = id
        self.deviceId = deviceId
        self.entityType = entityType
        self.entityId = entityId
        self.operation = operation
        self.payloadJson = payloadJson
        self.attempts = attempts
        self.maxAttempts = maxAttempts
        self.lastError = lastError
        self.createdAt = createdAt
        self.processedAt = processedAt
        self.idempotencyKey = idempotencyKey
        self.nextRetryAt = nextRetryAt
    }
    
    var canRetry: Bool {
        attempts < maxAttempts
    }
    
    var shouldRetryNow: Bool {
        guard canRetry else { return false }
        guard let nextRetry = nextRetryAt else { return true }
        return Date() >= nextRetry
    }
}

extension SyncQueueItem: FetchableRecord, PersistableRecord {
    static let databaseTableName = "sync_queue_items"
}

// MARK: - Idempotency Record

struct IdempotencyRecord: Identifiable, Codable {
    var id: String  // The idempotency key
    var entityType: SyncEntityType
    var entityId: String
    var operation: SyncOperation
    var requestHash: String
    var responseHash: String?
    var createdAt: Date
    var expiresAt: Date
    var processedAt: Date?
    
    init(
        entityType: SyncEntityType,
        entityId: String,
        operation: SyncOperation,
        requestPayload: String
    ) {
        // Generate deterministic idempotency key
        let keySource = "\(entityType.rawValue):\(entityId):\(operation.rawValue)"
        self.id = keySource.data(using: .utf8)?.base64EncodedString() ?? UUID().uuidString
        self.entityType = entityType
        self.entityId = entityId
        self.operation = operation
        self.requestHash = Self.hash(requestPayload)
        self.createdAt = Date()
        self.expiresAt = Date().addingTimeInterval(24 * 60 * 60) // 24 hours
    }
    
    static func hash(_ string: String) -> String {
        let data = Data(string.utf8)
        var hasher = 0
        for byte in data {
            hasher = hasher &* 31 &+ Int(byte)
        }
        return String(hasher, radix: 16)
    }
}

extension IdempotencyRecord: FetchableRecord, PersistableRecord {
    static let databaseTableName = "idempotency_records"
}

// MARK: - Sync State

struct SyncState {
    var lastSyncTimestamp: Date?
    var pendingCount: Int
    var failedCount: Int
    var isSyncing: Bool
    var lastError: String?
    
    var hasPendingItems: Bool {
        pendingCount > 0
    }
    
    var hasFailedItems: Bool {
        failedCount > 0
    }
    
    static let initial = SyncState(
        lastSyncTimestamp: nil,
        pendingCount: 0,
        failedCount: 0,
        isSyncing: false,
        lastError: nil
    )
}
