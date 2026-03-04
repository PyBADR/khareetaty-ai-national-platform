import XCTest
import GRDB
@testable import DeevoSentinel

final class SyncQueueTests: XCTestCase {
    
    var database: DatabaseQueue!
    var syncService: SyncService!
    
    override func setUp() async throws {
        try await super.setUp()
        
        // Create in-memory database for testing
        database = DatabaseQueue()
        
        // Run migrations
        try database.write { db in
            try db.create(table: "sync_queue_items") { t in
                t.column("id", .text).primaryKey()
                t.column("deviceId", .text).notNull()
                t.column("entityType", .text).notNull()
                t.column("entityId", .text).notNull()
                t.column("operation", .text).notNull()
                t.column("payloadJson", .text).notNull()
                t.column("attempts", .integer).notNull().defaults(to: 0)
                t.column("maxAttempts", .integer).notNull().defaults(to: 3)
                t.column("lastError", .text)
                t.column("createdAt", .datetime).notNull()
                t.column("processedAt", .datetime)
            }
        }
    }
    
    override func tearDown() async throws {
        database = nil
        syncService = nil
        try await super.tearDown()
    }
    
    // MARK: - Test Cases
    
    func testQueueSyncItem() async throws {
        // Given
        let deviceId = "test-device-123"
        let entityType = SyncEntityType.claim
        let entityId = "claim-001"
        let operation = SyncOperation.create
        let payload = ["claimNumber": "CLM-001", "customerName": "John Doe"]
        
        // When
        let item = SyncQueueItem(
            deviceId: deviceId,
            entityType: entityType,
            entityId: entityId,
            operation: operation,
            payloadJson: try JSONSerialization.data(withJSONObject: payload).base64EncodedString()
        )
        
        try database.write { db in
            try item.insert(db)
        }
        
        // Then
        let retrieved = try database.read { db in
            try SyncQueueItem.fetchOne(db, key: item.id)
        }
        
        XCTAssertNotNil(retrieved)
        XCTAssertEqual(retrieved?.deviceId, deviceId)
        XCTAssertEqual(retrieved?.entityType, entityType)
        XCTAssertEqual(retrieved?.entityId, entityId)
        XCTAssertEqual(retrieved?.operation, operation)
        XCTAssertEqual(retrieved?.attempts, 0)
        XCTAssertNil(retrieved?.processedAt)
    }
    
    func testGetPendingItems() async throws {
        // Given - Insert 3 items, 2 pending and 1 processed
        let item1 = SyncQueueItem(
            deviceId: "device-1",
            entityType: .claim,
            entityId: "claim-1",
            operation: .create,
            payloadJson: "{}"
        )
        
        let item2 = SyncQueueItem(
            deviceId: "device-1",
            entityType: .claim,
            entityId: "claim-2",
            operation: .update,
            payloadJson: "{}"
        )
        
        var item3 = SyncQueueItem(
            deviceId: "device-1",
            entityType: .claim,
            entityId: "claim-3",
            operation: .create,
            payloadJson: "{}"
        )
        item3.processedAt = Date()
        
        try database.write { db in
            try item1.insert(db)
            try item2.insert(db)
            try item3.insert(db)
        }
        
        // When
        let pendingItems = try database.read { db in
            try SyncQueueItem
                .filter(Column("processedAt") == nil)
                .order(Column("createdAt").asc)
                .fetchAll(db)
        }
        
        // Then
        XCTAssertEqual(pendingItems.count, 2)
        XCTAssertTrue(pendingItems.contains { $0.id == item1.id })
        XCTAssertTrue(pendingItems.contains { $0.id == item2.id })
        XCTAssertFalse(pendingItems.contains { $0.id == item3.id })
    }
    
    func testGetFailedItems() async throws {
        // Given - Insert items with different states
        let item1 = SyncQueueItem(
            deviceId: "device-1",
            entityType: .claim,
            entityId: "claim-1",
            operation: .create,
            payloadJson: "{}"
        )
        
        var item2 = SyncQueueItem(
            deviceId: "device-1",
            entityType: .claim,
            entityId: "claim-2",
            operation: .update,
            payloadJson: "{}"
        )
        item2.lastError = "Network error"
        item2.attempts = 3
        
        var item3 = SyncQueueItem(
            deviceId: "device-1",
            entityType: .claim,
            entityId: "claim-3",
            operation: .create,
            payloadJson: "{}"
        )
        item3.processedAt = Date()
        
        try database.write { db in
            try item1.insert(db)
            try item2.insert(db)
            try item3.insert(db)
        }
        
        // When
        let failedItems = try database.read { db in
            try SyncQueueItem
                .filter(Column("processedAt") == nil)
                .filter(Column("lastError") != nil)
                .order(Column("createdAt").asc)
                .fetchAll(db)
        }
        
        // Then
        XCTAssertEqual(failedItems.count, 1)
        XCTAssertEqual(failedItems.first?.id, item2.id)
        XCTAssertEqual(failedItems.first?.lastError, "Network error")
    }
    
    func testMarkItemAsProcessed() async throws {
        // Given
        let item = SyncQueueItem(
            deviceId: "device-1",
            entityType: .claim,
            entityId: "claim-1",
            operation: .create,
            payloadJson: "{}"
        )
        
        try database.write { db in
            try item.insert(db)
        }
        
        // When
        let processedDate = Date()
        try database.write { db in
            try db.execute(
                sql: "UPDATE sync_queue_items SET processedAt = ? WHERE id = ?",
                arguments: [processedDate, item.id]
            )
        }
        
        // Then
        let updated = try database.read { db in
            try SyncQueueItem.fetchOne(db, key: item.id)
        }
        
        XCTAssertNotNil(updated?.processedAt)
        XCTAssertEqual(updated?.processedAt?.timeIntervalSince1970, processedDate.timeIntervalSince1970, accuracy: 1.0)
    }
    
    func testIncrementAttempts() async throws {
        // Given
        var item = SyncQueueItem(
            deviceId: "device-1",
            entityType: .claim,
            entityId: "claim-1",
            operation: .create,
            payloadJson: "{}"
        )
        
        try database.write { db in
            try item.insert(db)
        }
        
        // When - Increment attempts
        try database.write { db in
            try db.execute(
                sql: "UPDATE sync_queue_items SET attempts = attempts + 1, lastError = ? WHERE id = ?",
                arguments: ["Test error", item.id]
            )
        }
        
        // Then
        let updated = try database.read { db in
            try SyncQueueItem.fetchOne(db, key: item.id)
        }
        
        XCTAssertEqual(updated?.attempts, 1)
        XCTAssertEqual(updated?.lastError, "Test error")
    }
    
    func testSyncQueueOrdering() async throws {
        // Given - Insert items with different timestamps
        let now = Date()
        
        var item1 = SyncQueueItem(
            deviceId: "device-1",
            entityType: .claim,
            entityId: "claim-1",
            operation: .create,
            payloadJson: "{}"
        )
        item1.createdAt = now.addingTimeInterval(-100)
        
        var item2 = SyncQueueItem(
            deviceId: "device-1",
            entityType: .claim,
            entityId: "claim-2",
            operation: .create,
            payloadJson: "{}"
        )
        item2.createdAt = now.addingTimeInterval(-50)
        
        var item3 = SyncQueueItem(
            deviceId: "device-1",
            entityType: .claim,
            entityId: "claim-3",
            operation: .create,
            payloadJson: "{}"
        )
        item3.createdAt = now
        
        try database.write { db in
            try item1.insert(db)
            try item2.insert(db)
            try item3.insert(db)
        }
        
        // When - Fetch ordered by createdAt ascending
        let orderedItems = try database.read { db in
            try SyncQueueItem
                .order(Column("createdAt").asc)
                .fetchAll(db)
        }
        
        // Then - Should be in chronological order (oldest first)
        XCTAssertEqual(orderedItems.count, 3)
        XCTAssertEqual(orderedItems[0].id, item1.id)
        XCTAssertEqual(orderedItems[1].id, item2.id)
        XCTAssertEqual(orderedItems[2].id, item3.id)
    }
}
