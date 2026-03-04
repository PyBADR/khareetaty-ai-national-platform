import Foundation
import GRDB

/// Repository for Claim data access - isolates Views from direct GRDB queries
@MainActor
final class ClaimRepository {
    
    // MARK: - Singleton
    
    static let shared = ClaimRepository()
    
    // MARK: - Properties
    
    private let database: DatabaseManager
    
    // MARK: - Initialization
    
    private init() {
        self.database = DatabaseManager.shared
    }
    
    // MARK: - CRUD Operations
    
    /// Fetch all claims for a tenant
    func fetchAll(tenantId: String) async throws -> [Claim] {
        try await database.database.read { db in
            try Claim
                .filter(Column("tenantId") == tenantId)
                .order(Column("updatedAt").desc)
                .fetchAll(db)
        }
    }
    
    /// Fetch a single claim by ID
    func fetch(id: String) async throws -> Claim? {
        try await database.database.read { db in
            try Claim.fetchOne(db, key: id)
        }
    }
    
    /// Fetch claims by status
    func fetchByStatus(_ status: ClaimStatus, tenantId: String) async throws -> [Claim] {
        try await database.database.read { db in
            try Claim
                .filter(Column("tenantId") == tenantId)
                .filter(Column("status") == status.rawValue)
                .order(Column("updatedAt").desc)
                .fetchAll(db)
        }
    }
    
    /// Fetch claims assigned to a user
    func fetchAssignedTo(userId: String, tenantId: String) async throws -> [Claim] {
        try await database.database.read { db in
            try Claim
                .filter(Column("tenantId") == tenantId)
                .filter(Column("assignedToId") == userId)
                .order(Column("updatedAt").desc)
                .fetchAll(db)
        }
    }
    
    /// Fetch claims with pending sync
    func fetchPendingSync(tenantId: String) async throws -> [Claim] {
        try await database.database.read { db in
            try Claim
                .filter(Column("tenantId") == tenantId)
                .filter(Column("syncStatus") == SyncStatus.pending.rawValue)
                .order(Column("createdAt").asc)
                .fetchAll(db)
        }
    }
    
    /// Insert a new claim
    func insert(_ claim: Claim) async throws {
        var mutableClaim = claim
        mutableClaim.createdAt = Date()
        mutableClaim.updatedAt = Date()
        mutableClaim.syncStatus = .pending
        
        try await database.database.write { db in
            try mutableClaim.insert(db)
        }
    }
    
    /// Update an existing claim
    func update(_ claim: Claim) async throws {
        var mutableClaim = claim
        mutableClaim.updatedAt = Date()
        mutableClaim.syncStatus = .pending
        
        try await database.database.write { db in
            try mutableClaim.update(db)
        }
    }
    
    /// Delete a claim
    func delete(id: String) async throws {
        try await database.database.write { db in
            _ = try Claim.deleteOne(db, key: id)
        }
    }
    
    /// Mark claim as synced
    func markSynced(id: String) async throws {
        try await database.database.write { db in
            try db.execute(
                sql: "UPDATE claims SET syncStatus = ?, lastSyncedAt = ? WHERE id = ?",
                arguments: [SyncStatus.synced.rawValue, Date(), id]
            )
        }
    }
    
    /// Mark claim sync as failed
    func markSyncFailed(id: String, error: String) async throws {
        try await database.database.write { db in
            try db.execute(
                sql: "UPDATE claims SET syncStatus = ? WHERE id = ?",
                arguments: [SyncStatus.failed.rawValue, id]
            )
        }
    }
    
    // MARK: - Search
    
    /// Search claims by claim number or customer name
    func search(query: String, tenantId: String) async throws -> [Claim] {
        let pattern = "%\(query)%"
        return try await database.database.read { db in
            try Claim
                .filter(Column("tenantId") == tenantId)
                .filter(
                    Column("claimNumber").like(pattern) ||
                    Column("customerName").like(pattern)
                )
                .order(Column("updatedAt").desc)
                .fetchAll(db)
        }
    }
    
    // MARK: - Statistics
    
    /// Get claim counts by status
    func countByStatus(tenantId: String) async throws -> [ClaimStatus: Int] {
        try await database.database.read { db in
            var counts: [ClaimStatus: Int] = [:]
            for status in ClaimStatus.allCases {
                let count = try Claim
                    .filter(Column("tenantId") == tenantId)
                    .filter(Column("status") == status.rawValue)
                    .fetchCount(db)
                counts[status] = count
            }
            return counts
        }
    }
    
    /// Get total pending sync count
    func pendingSyncCount(tenantId: String) async throws -> Int {
        try await database.database.read { db in
            try Claim
                .filter(Column("tenantId") == tenantId)
                .filter(Column("syncStatus") == SyncStatus.pending.rawValue)
                .fetchCount(db)
        }
    }
}
