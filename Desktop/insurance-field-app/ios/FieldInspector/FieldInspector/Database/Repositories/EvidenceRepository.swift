import Foundation
import GRDB

/// Repository for MediaAsset (Evidence) data access - isolates Views from direct GRDB queries
@MainActor
final class EvidenceRepository {
    
    // MARK: - Singleton
    
    static let shared = EvidenceRepository()
    
    // MARK: - Properties
    
    private let database: DatabaseManager
    
    // MARK: - Initialization
    
    private init() {
        self.database = DatabaseManager.shared
    }
    
    // MARK: - CRUD Operations
    
    /// Fetch all media assets for a claim
    func fetchForClaim(claimId: String) async throws -> [MediaAsset] {
        try await database.database.read { db in
            try MediaAsset
                .filter(Column("claimId") == claimId)
                .order(Column("createdAt").desc)
                .fetchAll(db)
        }
    }
    
    /// Fetch all media assets for an inspection
    func fetchForInspection(inspectionId: String) async throws -> [MediaAsset] {
        try await database.database.read { db in
            try MediaAsset
                .filter(Column("inspectionId") == inspectionId)
                .order(Column("createdAt").desc)
                .fetchAll(db)
        }
    }
    
    /// Fetch a single media asset by ID
    func fetch(id: String) async throws -> MediaAsset? {
        try await database.database.read { db in
            try MediaAsset.fetchOne(db, key: id)
        }
    }
    
    /// Fetch media assets pending sync
    func fetchPendingSync() async throws -> [MediaAsset] {
        try await database.database.read { db in
            try MediaAsset
                .filter(Column("syncStatus") == SyncStatus.pending.rawValue)
                .order(Column("createdAt").asc)
                .fetchAll(db)
        }
    }
    
    /// Fetch failed sync media assets
    func fetchFailedSync() async throws -> [MediaAsset] {
        try await database.database.read { db in
            try MediaAsset
                .filter(Column("syncStatus") == SyncStatus.failed.rawValue)
                .order(Column("createdAt").asc)
                .fetchAll(db)
        }
    }
    
    /// Insert a new media asset
    func insert(_ asset: MediaAsset) async throws {
        var mutableAsset = asset
        mutableAsset.createdAt = Date()
        mutableAsset.updatedAt = Date()
        mutableAsset.syncStatus = .pending
        
        let assetToInsert = mutableAsset
        try await database.database.write { db in
            try assetToInsert.insert(db)
        }
    }
    
    /// Update an existing media asset
    func update(_ asset: MediaAsset) async throws {
        var mutableAsset = asset
        mutableAsset.updatedAt = Date()
        
        let assetToUpdate = mutableAsset
        try await database.database.write { db in
            try assetToUpdate.update(db)
        }
    }
    
    /// Delete a media asset
    func delete(id: String) async throws {
        try await database.database.write { db in
            _ = try MediaAsset.deleteOne(db, key: id)
        }
    }
    
    /// Mark asset as synced
    func markSynced(id: String, remoteUrl: String) async throws {
        try await database.database.write { db in
            try db.execute(
                sql: "UPDATE media_assets SET syncStatus = ?, remoteUrl = ?, updatedAt = ? WHERE id = ?",
                arguments: [SyncStatus.synced.rawValue, remoteUrl, Date(), id]
            )
        }
    }
    
    /// Mark asset sync as failed
    func markSyncFailed(id: String, error: String) async throws {
        try await database.database.write { db in
            try db.execute(
                sql: "UPDATE media_assets SET syncStatus = ?, syncError = ?, updatedAt = ? WHERE id = ?",
                arguments: [SyncStatus.failed.rawValue, error, Date(), id]
            )
        }
    }
    
    /// Mark asset as uploading
    func markUploading(id: String) async throws {
        try await database.database.write { db in
            try db.execute(
                sql: "UPDATE media_assets SET syncStatus = ?, updatedAt = ? WHERE id = ?",
                arguments: [SyncStatus.uploading.rawValue, Date(), id]
            )
        }
    }
    
    // MARK: - Statistics
    
    /// Get count of media assets for a claim
    func countForClaim(claimId: String) async throws -> Int {
        try await database.database.read { db in
            try MediaAsset
                .filter(Column("claimId") == claimId)
                .fetchCount(db)
        }
    }
    
    /// Get total size of media assets for a claim
    func totalSizeForClaim(claimId: String) async throws -> Int64 {
        try await database.database.read { db in
            let sum = try Int64.fetchOne(
                db,
                sql: "SELECT COALESCE(SUM(fileSize), 0) FROM media_assets WHERE claimId = ?",
                arguments: [claimId]
            )
            return sum ?? 0
        }
    }
    
    /// Get pending sync count
    func pendingSyncCount() async throws -> Int {
        try await database.database.read { db in
            try MediaAsset
                .filter(Column("syncStatus") == SyncStatus.pending.rawValue)
                .fetchCount(db)
        }
    }
}
