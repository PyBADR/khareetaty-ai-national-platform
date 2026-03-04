import Foundation
import GRDB

/// Manages the SQLite database using GRDB
final class DatabaseManager {
    
    // MARK: - Singleton
    
    static let shared = DatabaseManager()
    
    // MARK: - Properties
    
    private var dbQueue: DatabaseQueue?
    
    var database: DatabaseQueue {
        guard let db = dbQueue else {
            fatalError("Database not initialized. Call setup() first.")
        }
        return db
    }
    
    // MARK: - Initialization
    
    private init() {}
    
    // MARK: - Setup
    
    func setup() throws {
        let fileManager = FileManager.default
        let documentsURL = try fileManager.url(
            for: .documentDirectory,
            in: .userDomainMask,
            appropriateFor: nil,
            create: true
        )
        let dbURL = documentsURL.appendingPathComponent("DeevoSentinel.sqlite")
        
        // Configure database
        var config = Configuration()
        config.prepareDatabase { db in
            // Enable foreign keys
            try db.execute(sql: "PRAGMA foreign_keys = ON")
        }
        
        dbQueue = try DatabaseQueue(path: dbURL.path, configuration: config)
        
        // Run migrations
        try migrate()
        
        print("📦 Database initialized at: \(dbURL.path)")
    }
    
    // MARK: - Migrations
    
    private func migrate() throws {
        var migrator = DatabaseMigrator()
        
        // Migration 1: Initial schema
        migrator.registerMigration("v1_initial") { db in
            // Users table
            try db.create(table: "users") { t in
                t.column("id", .text).primaryKey()
                t.column("email", .text).notNull()
                t.column("firstName", .text).notNull()
                t.column("lastName", .text).notNull()
                t.column("role", .text).notNull()
                t.column("isActive", .boolean).notNull().defaults(to: true)
                t.column("tenantId", .text).notNull()
                t.column("createdAt", .datetime).notNull()
            }
            
            // Unique email per tenant
            try db.create(
                index: "users_tenant_email_unique",
                on: "users",
                columns: ["tenantId", "email"],
                unique: true
            )
            
            // Claims table
            try db.create(table: "claims") { t in
                t.column("id", .text).primaryKey()
                t.column("claimNumber", .text).notNull()
                t.column("status", .text).notNull()
                t.column("priority", .text).notNull()
                t.column("customerName", .text).notNull()
                t.column("customerPhone", .text)
                t.column("customerEmail", .text)
                t.column("vehicleMake", .text)
                t.column("vehicleModel", .text)
                t.column("vehicleYear", .integer)
                t.column("vehicleVin", .text)
                t.column("vehiclePlate", .text)
                t.column("vehicleColor", .text)
                t.column("locationAddress", .text)
                t.column("locationCity", .text)
                t.column("locationState", .text)
                t.column("locationZip", .text)
                t.column("locationLat", .double)
                t.column("locationLng", .double)
                t.column("incidentDate", .datetime)
                t.column("incidentDescription", .text)
                t.column("estimatedDamage", .double)
                t.column("assignedToId", .text).references("users", onDelete: .setNull)
                t.column("assignedAt", .datetime)
                t.column("tenantId", .text).notNull()
                t.column("createdAt", .datetime).notNull()
                t.column("updatedAt", .datetime).notNull()
                t.column("syncStatus", .text).notNull().defaults(to: "pending")
                t.column("lastSyncedAt", .datetime)
            }
            
            // Unique claim number per tenant
            try db.create(
                index: "claims_tenant_claimNumber_unique",
                on: "claims",
                columns: ["tenantId", "claimNumber"],
                unique: true
            )
            
            try db.create(index: "claims_status", on: "claims", columns: ["status"])
            try db.create(index: "claims_priority", on: "claims", columns: ["priority"])
            try db.create(index: "claims_assignedToId", on: "claims", columns: ["assignedToId"])
            
            // Inspections table
            try db.create(table: "inspections") { t in
                t.column("id", .text).primaryKey()
                t.column("claimId", .text).notNull().references("claims", onDelete: .cascade)
                t.column("templateId", .text).notNull()
                t.column("status", .text).notNull()
                t.column("startedAt", .datetime)
                t.column("completedAt", .datetime)
                t.column("createdAt", .datetime).notNull()
                t.column("updatedAt", .datetime).notNull()
                t.column("syncStatus", .text).notNull().defaults(to: "pending")
            }
            
            try db.create(index: "inspections_claimId", on: "inspections", columns: ["claimId"])
            
            // Inspection Fields table
            try db.create(table: "inspection_fields") { t in
                t.column("id", .text).primaryKey()
                t.column("inspectionId", .text).notNull().references("inspections", onDelete: .cascade)
                t.column("sectionKey", .text).notNull()
                t.column("fieldKey", .text).notNull()
                t.column("value", .text)
                t.column("valueType", .text).notNull()
                t.column("required", .boolean).notNull().defaults(to: false)
                t.column("displayOrder", .integer).notNull().defaults(to: 0)
                t.column("createdAt", .datetime).notNull()
                t.column("updatedAt", .datetime).notNull()
                t.column("syncStatus", .text).notNull().defaults(to: "pending")
            }
            
            try db.create(index: "inspection_fields_inspectionId", on: "inspection_fields", columns: ["inspectionId"])
            try db.create(
                index: "inspection_fields_unique",
                on: "inspection_fields",
                columns: ["inspectionId", "sectionKey", "fieldKey"],
                unique: true
            )
            
            // Media Assets table
            try db.create(table: "media_assets") { t in
                t.column("id", .text).primaryKey()
                t.column("claimId", .text).notNull().references("claims", onDelete: .cascade)
                t.column("inspectionId", .text).references("inspections", onDelete: .setNull)
                t.column("type", .text).notNull()
                t.column("filename", .text).notNull()
                t.column("mimeType", .text).notNull()
                t.column("fileSize", .integer).notNull()
                t.column("localPath", .text)
                t.column("remoteUrl", .text)
                t.column("thumbnailPath", .text)
                t.column("tags", .text).notNull().defaults(to: "")
                t.column("caption", .text)
                t.column("latitude", .double)
                t.column("longitude", .double)
                t.column("capturedAt", .datetime)
                t.column("createdAt", .datetime).notNull()
                t.column("updatedAt", .datetime).notNull()
                t.column("syncStatus", .text).notNull().defaults(to: "pending")
                t.column("syncError", .text)
            }
            
            try db.create(index: "media_assets_claimId", on: "media_assets", columns: ["claimId"])
            try db.create(index: "media_assets_inspectionId", on: "media_assets", columns: ["inspectionId"])
            try db.create(index: "media_assets_syncStatus", on: "media_assets", columns: ["syncStatus"])
            
            // Sync Queue Items table
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
            
            try db.create(index: "sync_queue_items_processedAt", on: "sync_queue_items", columns: ["processedAt"])
            
            // Audit Events table
            try db.create(table: "audit_events") { t in
                t.column("id", .text).primaryKey()
                t.column("actorId", .text).notNull()
                t.column("claimId", .text).references("claims", onDelete: .setNull)
                t.column("eventType", .text).notNull()
                t.column("eventPayloadJson", .text).notNull()
                t.column("hashPrev", .text).notNull()
                t.column("hashThis", .text).notNull()
                t.column("createdAt", .datetime).notNull()
            }
            
            try db.create(index: "audit_events_claimId", on: "audit_events", columns: ["claimId"])
            try db.create(index: "audit_events_createdAt", on: "audit_events", columns: ["createdAt"])
        }
        
        // Migration 2: Add multi-tenancy support
        migrator.registerMigration("v2_multi_tenancy") { db in
            // Add tenantId to users table
            try db.alter(table: "users") { t in
                t.add(column: "tenantId", .text).notNull().defaults(to: "default")
            }
            
            // Add tenantId to claims table
            try db.alter(table: "claims") { t in
                t.add(column: "tenantId", .text).notNull().defaults(to: "default")
            }
            
            // Add tenantId to inspections table
            try db.alter(table: "inspections") { t in
                t.add(column: "tenantId", .text).notNull().defaults(to: "default")
            }
            
            // Add tenantId to media_assets table
            try db.alter(table: "media_assets") { t in
                t.add(column: "tenantId", .text).notNull().defaults(to: "default")
            }
            
            // Create indexes for tenant filtering
            try db.create(index: "users_tenantId", on: "users", columns: ["tenantId"])
            try db.create(index: "claims_tenantId", on: "claims", columns: ["tenantId"])
            try db.create(index: "inspections_tenantId", on: "inspections", columns: ["tenantId"])
            try db.create(index: "media_assets_tenantId", on: "media_assets", columns: ["tenantId"])
        }
        
        // Migration 3: Sync hardening - idempotency, conflicts, per-claim status
        migrator.registerMigration("v3_sync_hardening") { db in
            // Add idempotency key and retry fields to sync_queue_items
            try db.alter(table: "sync_queue_items") { t in
                t.add(column: "idempotencyKey", .text)
                t.add(column: "nextRetryAt", .datetime)
            }
            
            // Create idempotency records table
            try db.create(table: "idempotency_records") { t in
                t.column("id", .text).primaryKey()
                t.column("entityType", .text).notNull()
                t.column("entityId", .text).notNull()
                t.column("operation", .text).notNull()
                t.column("requestHash", .text).notNull()
                t.column("responseHash", .text)
                t.column("createdAt", .datetime).notNull()
                t.column("expiresAt", .datetime).notNull()
                t.column("processedAt", .datetime)
            }
            
            try db.create(index: "idempotency_records_expiresAt", on: "idempotency_records", columns: ["expiresAt"])
            
            // Create sync conflicts table
            try db.create(table: "sync_conflicts") { t in
                t.column("id", .text).primaryKey()
                t.column("entityType", .text).notNull()
                t.column("entityId", .text).notNull()
                t.column("field", .text).notNull()
                t.column("localValue", .text).notNull()
                t.column("serverValue", .text).notNull()
                t.column("localTimestamp", .datetime).notNull()
                t.column("serverTimestamp", .datetime).notNull()
                t.column("resolution", .text)
                t.column("resolvedAt", .datetime)
                t.column("resolvedBy", .text)
            }
            
            try db.create(index: "sync_conflicts_entityId", on: "sync_conflicts", columns: ["entityId"])
            try db.create(index: "sync_conflicts_resolvedAt", on: "sync_conflicts", columns: ["resolvedAt"])
            
            // Create per-claim sync status table
            try db.create(table: "claim_sync_status") { t in
                t.column("id", .text).primaryKey()  // claimId
                t.column("syncState", .text).notNull()
                t.column("pendingOperations", .integer).notNull().defaults(to: 0)
                t.column("lastAttempt", .datetime)
                t.column("lastSuccess", .datetime)
                t.column("lastError", .text)
                t.column("retryCount", .integer).notNull().defaults(to: 0)
                t.column("nextRetryAt", .datetime)
            }
        }
        
        try migrator.migrate(database)
    }
    
    // MARK: - Utility Methods
    
    func clearAllData() throws {
        try database.write { db in
            try db.execute(sql: "DELETE FROM audit_events")
            try db.execute(sql: "DELETE FROM sync_queue_items")
            try db.execute(sql: "DELETE FROM media_assets")
            try db.execute(sql: "DELETE FROM inspection_fields")
            try db.execute(sql: "DELETE FROM inspections")
            try db.execute(sql: "DELETE FROM claims")
            try db.execute(sql: "DELETE FROM users")
        }
    }
}
