import Foundation
import GRDB
import Network

// MARK: - Exponential Backoff Configuration

struct BackoffConfig {
    let initialDelay: TimeInterval
    let maxDelay: TimeInterval
    let multiplier: Double
    let jitterFactor: Double
    
    static let `default` = BackoffConfig(
        initialDelay: 1.0,      // 1 second
        maxDelay: 300.0,        // 5 minutes max
        multiplier: 2.0,        // Double each time
        jitterFactor: 0.1       // 10% jitter
    )
    
    func delay(forAttempt attempt: Int) -> TimeInterval {
        let exponentialDelay = initialDelay * pow(multiplier, Double(attempt))
        let cappedDelay = min(exponentialDelay, maxDelay)
        let jitter = cappedDelay * jitterFactor * Double.random(in: -1...1)
        return max(0, cappedDelay + jitter)
    }
}

// MARK: - Conflict Resolution Strategy

enum ConflictResolutionStrategy {
    case lastWriteWins          // Non-critical fields
    case serverWins             // Server is source of truth
    case clientWins             // Client changes take precedence
    case manualResolution       // Requires user intervention (decision overrides)
    
    static func strategy(for entityType: SyncEntityType, field: String? = nil) -> ConflictResolutionStrategy {
        switch entityType {
        case .claim:
            // Decision-related fields require manual resolution
            if let field = field, ["status", "aiDecision", "aiOverride"].contains(field) {
                return .manualResolution
            }
            return .lastWriteWins
        case .inspection, .inspectionField:
            return .lastWriteWins
        case .mediaAsset:
            return .clientWins  // Client has the actual file
        }
    }
}

// MARK: - Sync Conflict

struct SyncConflict: Identifiable, Codable {
    var id: String
    var entityType: SyncEntityType
    var entityId: String
    var field: String
    var localValue: String
    var serverValue: String
    var localTimestamp: Date
    var serverTimestamp: Date
    var resolution: ConflictResolution?
    var resolvedAt: Date?
    var resolvedBy: String?
    
    init(
        id: String = UUID().uuidString,
        entityType: SyncEntityType,
        entityId: String,
        field: String,
        localValue: String,
        serverValue: String,
        localTimestamp: Date,
        serverTimestamp: Date
    ) {
        self.id = id
        self.entityType = entityType
        self.entityId = entityId
        self.field = field
        self.localValue = localValue
        self.serverValue = serverValue
        self.localTimestamp = localTimestamp
        self.serverTimestamp = serverTimestamp
    }
}

enum ConflictResolution: String, Codable, DatabaseValueConvertible {
    case acceptLocal = "accept_local"
    case acceptServer = "accept_server"
    case merged = "merged"
}

extension SyncConflict: FetchableRecord, PersistableRecord {
    static let databaseTableName = "sync_conflicts"
}

// MARK: - Per-Claim Sync Status

struct ClaimSyncStatus: Identifiable, Codable {
    var id: String  // claimId
    var syncState: ClaimSyncState
    var pendingOperations: Int
    var lastAttempt: Date?
    var lastSuccess: Date?
    var lastError: String?
    var retryCount: Int
    var nextRetryAt: Date?
    
    init(claimId: String) {
        self.id = claimId
        self.syncState = .synced
        self.pendingOperations = 0
        self.retryCount = 0
    }
}

enum ClaimSyncState: String, Codable, DatabaseValueConvertible {
    case synced = "synced"
    case pending = "pending"
    case syncing = "syncing"
    case conflict = "conflict"
    case failed = "failed"
    
    var iconName: String {
        switch self {
        case .synced: return "checkmark.circle.fill"
        case .pending: return "clock.fill"
        case .syncing: return "arrow.triangle.2.circlepath"
        case .conflict: return "exclamationmark.triangle.fill"
        case .failed: return "xmark.circle.fill"
        }
    }
    
    var color: String {
        switch self {
        case .synced: return "green"
        case .pending: return "orange"
        case .syncing: return "blue"
        case .conflict: return "yellow"
        case .failed: return "red"
        }
    }
}

extension ClaimSyncStatus: FetchableRecord, PersistableRecord {
    static let databaseTableName = "claim_sync_status"
}

/// Service for managing offline-first sync with exponential backoff and conflict resolution
@MainActor
final class SyncService: ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = SyncService()
    
    // MARK: - Published Properties
    
    @Published private(set) var syncState = SyncState.initial
    @Published private(set) var isOnline = true
    @Published private(set) var claimSyncStatuses: [String: ClaimSyncStatus] = [:]
    @Published private(set) var pendingConflicts: [SyncConflict] = []
    
    // MARK: - Properties
    
    private let database: DatabaseManager
    private let api: APIService
    private let monitor: NWPathMonitor
    private let monitorQueue = DispatchQueue(label: "com.deevo.sentinel.networkmonitor")
    private var deviceId: String
    private let backoffConfig: BackoffConfig
    
    // Retry state
    private var globalRetryCount = 0
    private var isRetrying = false
    private var retryTask: Task<Void, Never>?
    
    // MARK: - Initialization
    
    private init() {
        self.database = DatabaseManager.shared
        self.api = APIService.shared
        self.monitor = NWPathMonitor()
        self.backoffConfig = .default
        
        // Get or create device ID
        if let savedId = UserDefaults.standard.string(forKey: "deviceId") {
            self.deviceId = savedId
        } else {
            let newId = UUID().uuidString
            UserDefaults.standard.set(newId, forKey: "deviceId")
            self.deviceId = newId
        }
        
        setupNetworkMonitoring()
        
        Task {
            await loadClaimSyncStatuses()
            await loadPendingConflicts()
        }
    }
    
    // MARK: - Network Monitoring
    
    private func setupNetworkMonitoring() {
        monitor.pathUpdateHandler = { [weak self] path in
            Task { @MainActor in
                guard let self = self else { return }
                let wasOffline = !self.isOnline
                self.isOnline = path.status == .satisfied
                
                // Auto-sync when coming online
                if path.status == .satisfied && wasOffline {
                    self.globalRetryCount = 0  // Reset retry count
                    await self.syncIfNeeded()
                }
            }
        }
        monitor.start(queue: monitorQueue)
    }
    
    // MARK: - Load Persisted State
    
    private func loadClaimSyncStatuses() async {
        do {
            let statuses = try await database.database.read { db in
                try ClaimSyncStatus.fetchAll(db)
            }
            await MainActor.run {
                claimSyncStatuses = Dictionary(uniqueKeysWithValues: statuses.map { ($0.id, $0) })
            }
        } catch {
            AppLogger.error("Error loading claim sync statuses", error: error, category: AppLogger.sync)
        }
    }
    
    private func loadPendingConflicts() async {
        do {
            let conflicts = try await database.database.read { db in
                try SyncConflict
                    .filter(Column("resolvedAt") == nil)
                    .fetchAll(db)
            }
            await MainActor.run {
                pendingConflicts = conflicts
            }
        } catch {
            AppLogger.error("Error loading pending conflicts", error: error, category: AppLogger.sync)
        }
    }
    
    // MARK: - Sync Queue Management
    
    /// Add an item to the sync queue
    func queueSync<T: Encodable>(
        entityType: SyncEntityType,
        entityId: String,
        operation: SyncOperation,
        payload: T
    ) async throws {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        let payloadData = try encoder.encode(payload)
        let payloadJson = String(data: payloadData, encoding: .utf8) ?? "{}"
        
        let item = SyncQueueItem(
            deviceId: deviceId,
            entityType: entityType,
            entityId: entityId,
            operation: operation,
            payloadJson: payloadJson
        )
        
        try await database.database.write { db in
            try item.insert(db)
        }
        
        await updateSyncState()
        
        // Try to sync immediately if online
        if isOnline {
            await syncIfNeeded()
        }
    }
    
    /// Get pending sync items
    func getPendingItems() async throws -> [SyncQueueItem] {
        try await database.database.read { db in
            try SyncQueueItem
                .filter(Column("processedAt") == nil)
                .order(Column("createdAt").asc)
                .fetchAll(db)
        }
    }
    
    /// Get failed sync items
    func getFailedItems() async throws -> [SyncQueueItem] {
        try await database.database.read { db in
            try SyncQueueItem
                .filter(Column("processedAt") == nil)
                .filter(Column("lastError") != nil)
                .order(Column("createdAt").asc)
                .fetchAll(db)
        }
    }
    
    // MARK: - Sync Operations
    
    /// Perform sync if there are pending items
    func syncIfNeeded() async {
        guard isOnline else { return }
        guard !syncState.isSyncing else { return }
        
        do {
            let pendingItems = try await getPendingItems()
            guard !pendingItems.isEmpty else { return }
            
            await performSync()
        } catch {
            AppLogger.error("Error checking pending items", error: error, category: AppLogger.sync)
        }
    }
    
    /// Force a full sync
    func forceSync() async {
        guard isOnline else {
            await MainActor.run {
                syncState.lastError = "No internet connection"
            }
            return
        }
        
        globalRetryCount = 0
        await performSync()
    }
    
    /// Perform the actual sync with exponential backoff
    private func performSync() async {
        await MainActor.run {
            syncState.isSyncing = true
            syncState.lastError = nil
        }
        
        do {
            // Push local changes
            try await pushChanges()
            
            // Pull remote changes
            try await pullChanges()
            
            // Reset retry count on success
            globalRetryCount = 0
            
            await MainActor.run {
                syncState.lastSyncTimestamp = Date()
                syncState.isSyncing = false
            }
            
            await updateSyncState()
            
        } catch {
            await handleSyncError(error)
        }
    }
    
    /// Handle sync error with exponential backoff
    private func handleSyncError(_ error: Error) async {
        await MainActor.run {
            syncState.isSyncing = false
            syncState.lastError = error.localizedDescription
        }
        
        // Check if we should retry
        guard globalRetryCount < 10 else {
            AppLogger.syncFailed(error: error, attempt: globalRetryCount + 1, nextRetryIn: nil)
            return
        }
        
        // Calculate backoff delay
        let delay = backoffConfig.delay(forAttempt: globalRetryCount)
        globalRetryCount += 1
        
        AppLogger.syncFailed(error: error, attempt: globalRetryCount, nextRetryIn: delay)
        
        // Schedule retry
        retryTask?.cancel()
        retryTask = Task {
            try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
            
            guard !Task.isCancelled else { return }
            guard isOnline else { return }
            
            await performSync()
        }
    }
    
    /// Push local changes to server
    private func pushChanges() async throws {
        let pendingItems = try await getPendingItems()
        guard !pendingItems.isEmpty else { return }
        
        let formatter = ISO8601DateFormatter()
        
        let syncItems = pendingItems.map { item in
            SyncItem(
                id: item.id,
                deviceId: item.deviceId,
                entityType: item.entityType.rawValue,
                entityId: item.entityId,
                operation: item.operation.rawValue,
                payload: [:], // Simplified for now
                clientTimestamp: formatter.string(from: item.createdAt)
            )
        }
        
        let request = SyncPushRequest(
            deviceId: deviceId,
            items: syncItems,
            lastSyncTimestamp: syncState.lastSyncTimestamp.map { formatter.string(from: $0) }
        )
        
        let response = try await api.pushSync(request: request)
        
        // Mark successful items as processed
        let failedIds = Set(response.failedItems.map { $0.id })
        
        try await database.database.write { db in
            for item in pendingItems {
                if failedIds.contains(item.id) {
                    // Update failed item
                    let failedItem = response.failedItems.first { $0.id == item.id }
                    try db.execute(
                        sql: "UPDATE sync_queue_items SET attempts = attempts + 1, lastError = ? WHERE id = ?",
                        arguments: [failedItem?.error, item.id]
                    )
                } else {
                    // Mark as processed
                    try db.execute(
                        sql: "UPDATE sync_queue_items SET processedAt = ? WHERE id = ?",
                        arguments: [Date(), item.id]
                    )
                }
            }
        }
    }
    
    /// Pull remote changes from server
    private func pullChanges() async throws {
        let formatter = ISO8601DateFormatter()
        
        let request = SyncPullRequest(
            deviceId: deviceId,
            lastSyncTimestamp: syncState.lastSyncTimestamp.map { formatter.string(from: $0) },
            entityTypes: nil
        )
        
        let response = try await api.pullSync(request: request)
        
        // Process pulled items
        for item in response.items {
            try await processPulledItem(item)
        }
        
        // If there are more items, continue pulling
        if response.hasMore {
            try await pullChanges()
        }
    }
    
    /// Process a single pulled item
    private func processPulledItem(_ item: SyncPullItem) async throws {
        // This would update local database based on the pulled item
        // Implementation depends on entity type and operation
        AppLogger.itemProcessed(entityType: item.entityType, entityId: item.entityId, operation: item.operation)
    }
    
    // MARK: - State Management
    
    private func updateSyncState() async {
        do {
            let pendingCount = try await database.database.read { db in
                try SyncQueueItem
                    .filter(Column("processedAt") == nil)
                    .fetchCount(db)
            }
            
            let failedCount = try await database.database.read { db in
                try SyncQueueItem
                    .filter(Column("processedAt") == nil)
                    .filter(Column("lastError") != nil)
                    .fetchCount(db)
            }
            
            await MainActor.run {
                syncState.pendingCount = pendingCount
                syncState.failedCount = failedCount
            }
        } catch {
            AppLogger.error("Error updating sync state", error: error, category: AppLogger.sync)
        }
    }
    
    /// Retry failed sync items
    func retryFailedItems() async {
        do {
            try await database.database.write { db in
                try db.execute(
                    sql: "UPDATE sync_queue_items SET lastError = NULL, attempts = 0 WHERE processedAt IS NULL AND lastError IS NOT NULL"
                )
            }
            
            await updateSyncState()
            await forceSync()
        } catch {
            AppLogger.error("Error retrying failed items", error: error, category: AppLogger.sync)
        }
    }
    
    /// Clear processed items older than specified days
    func clearOldProcessedItems(olderThanDays: Int = 7) async throws {
        let cutoffDate = Calendar.current.date(byAdding: .day, value: -olderThanDays, to: Date())!
        
        try await database.database.write { db in
            try db.execute(
                sql: "DELETE FROM sync_queue_items WHERE processedAt IS NOT NULL AND processedAt < ?",
                arguments: [cutoffDate]
            )
        }
    }
    
    /// Cancel any pending retry
    func cancelRetry() {
        retryTask?.cancel()
        retryTask = nil
        isRetrying = false
    }
    
    // MARK: - Per-Claim Sync Status
    
    /// Update sync status for a specific claim
    @MainActor
    func updateClaimSyncStatus(claimId: String, state: ClaimSyncState, error: String? = nil) async {
        var status = claimSyncStatuses[claimId] ?? ClaimSyncStatus(claimId: claimId)
        status.syncState = state
        status.lastAttempt = Date()
        status.lastError = error
        
        if state == .synced {
            status.lastSuccess = Date()
            status.retryCount = 0
        } else if state == .failed {
            status.retryCount += 1
            status.nextRetryAt = Date().addingTimeInterval(backoffConfig.delay(forAttempt: status.retryCount))
        }
        
        // Count pending operations
        do {
            let pendingCount = try await database.database.read { db in
                try SyncQueueItem
                    .filter(Column("entityId") == claimId)
                    .filter(Column("processedAt") == nil)
                    .fetchCount(db)
            }
            status.pendingOperations = pendingCount
        } catch {
            AppLogger.error("Error counting pending operations", error: error, category: AppLogger.sync)
        }
        
        claimSyncStatuses[claimId] = status
        
        // Persist to database
        let statusToSave = status
        do {
            try await database.database.write { db in
                try statusToSave.save(db)
            }
        } catch {
            AppLogger.error("Error saving claim sync status", error: error, category: AppLogger.sync)
        }
    }
    
    /// Get sync status for a specific claim
    func getSyncStatus(for claimId: String) -> ClaimSyncStatus {
        claimSyncStatuses[claimId] ?? ClaimSyncStatus(claimId: claimId)
    }
    
    // MARK: - Conflict Resolution
    
    /// Resolve a conflict manually
    func resolveConflict(_ conflict: SyncConflict, resolution: ConflictResolution, resolvedBy: String) async throws {
        var updatedConflict = conflict
        updatedConflict.resolution = resolution
        updatedConflict.resolvedAt = Date()
        updatedConflict.resolvedBy = resolvedBy
        
        let conflictToSave = updatedConflict
        try await database.database.write { db in
            try conflictToSave.update(db)
        }
        
        // Apply resolution
        switch resolution {
        case .acceptLocal:
            // Re-queue the local change
            AppLogger.sync.info("✅ Accepting local value for \(conflict.entityId, privacy: .public)")
            
        case .acceptServer:
            // Apply server value
            AppLogger.sync.info("✅ Accepting server value for \(conflict.entityId, privacy: .public)")
            
        case .merged:
            // Custom merge logic
            AppLogger.sync.info("✅ Merged values for \(conflict.entityId, privacy: .public)")
        }
        
        // Update claim sync status
        await updateClaimSyncStatus(claimId: conflict.entityId, state: .synced)
        await loadPendingConflicts()
    }
}
