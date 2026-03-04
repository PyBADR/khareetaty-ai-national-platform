import Foundation
import GRDB

// MARK: - Form Template Model

struct FormTemplate: Identifiable, Codable, Equatable {
    var id: String
    var name: String
    var version: String
    var category: String
    var schemaJson: String
    var isActive: Bool
    var createdAt: Date
    var updatedAt: Date
    
    init(
        id: String = UUID().uuidString,
        name: String,
        version: String = "1.0",
        category: String,
        schemaJson: String,
        isActive: Bool = true,
        createdAt: Date = Date(),
        updatedAt: Date = Date()
    ) {
        self.id = id
        self.name = name
        self.version = version
        self.category = category
        self.schemaJson = schemaJson
        self.isActive = isActive
        self.createdAt = createdAt
        self.updatedAt = updatedAt
    }
}

extension FormTemplate: FetchableRecord, PersistableRecord {
    static let databaseTableName = "form_templates"
}

// MARK: - Form Draft Model

struct FormDraft: Identifiable, Codable, Equatable {
    var id: String
    var templateId: String
    var claimId: String?
    var inspectionId: String?
    var dataJson: String
    var status: FormDraftStatus
    var lastSavedAt: Date
    var createdAt: Date
    var updatedAt: Date
    var syncStatus: SyncStatus
    
    init(
        id: String = UUID().uuidString,
        templateId: String,
        claimId: String? = nil,
        inspectionId: String? = nil,
        dataJson: String = "{}",
        status: FormDraftStatus = .draft,
        lastSavedAt: Date = Date(),
        createdAt: Date = Date(),
        updatedAt: Date = Date(),
        syncStatus: SyncStatus = .pending
    ) {
        self.id = id
        self.templateId = templateId
        self.claimId = claimId
        self.inspectionId = inspectionId
        self.dataJson = dataJson
        self.status = status
        self.lastSavedAt = lastSavedAt
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.syncStatus = syncStatus
    }
}

enum FormDraftStatus: String, Codable, DatabaseValueConvertible {
    case draft = "draft"
    case submitted = "submitted"
    case synced = "synced"
    case failed = "failed"
}

extension FormDraft: FetchableRecord, PersistableRecord {
    static let databaseTableName = "form_drafts"
}

// MARK: - Form Repository

/// Repository for Form Templates and Drafts - isolates Views from direct GRDB queries
@MainActor
final class FormRepository {
    
    // MARK: - Singleton
    
    static let shared = FormRepository()
    
    // MARK: - Properties
    
    private let database: DatabaseManager
    
    // MARK: - Initialization
    
    private init() {
        self.database = DatabaseManager.shared
    }
    
    // MARK: - Template Operations
    
    /// Fetch all active templates
    func fetchAllTemplates() async throws -> [FormTemplate] {
        try await database.database.read { db in
            try FormTemplate
                .filter(Column("isActive") == true)
                .order(Column("name").asc)
                .fetchAll(db)
        }
    }
    
    /// Fetch templates by category
    func fetchTemplates(category: String) async throws -> [FormTemplate] {
        try await database.database.read { db in
            try FormTemplate
                .filter(Column("isActive") == true)
                .filter(Column("category") == category)
                .order(Column("name").asc)
                .fetchAll(db)
        }
    }
    
    /// Fetch a single template by ID
    func fetchTemplate(id: String) async throws -> FormTemplate? {
        try await database.database.read { db in
            try FormTemplate.fetchOne(db, key: id)
        }
    }
    
    /// Insert or update a template
    func saveTemplate(_ template: FormTemplate) async throws {
        var mutableTemplate = template
        mutableTemplate.updatedAt = Date()
        
        try await database.database.write { db in
            try mutableTemplate.save(db)
        }
    }
    
    // MARK: - Draft Operations
    
    /// Fetch all drafts
    func fetchAllDrafts() async throws -> [FormDraft] {
        try await database.database.read { db in
            try FormDraft
                .order(Column("updatedAt").desc)
                .fetchAll(db)
        }
    }
    
    /// Fetch drafts for a claim
    func fetchDrafts(claimId: String) async throws -> [FormDraft] {
        try await database.database.read { db in
            try FormDraft
                .filter(Column("claimId") == claimId)
                .order(Column("updatedAt").desc)
                .fetchAll(db)
        }
    }
    
    /// Fetch drafts pending submission
    func fetchPendingDrafts() async throws -> [FormDraft] {
        try await database.database.read { db in
            try FormDraft
                .filter(Column("status") == FormDraftStatus.submitted.rawValue)
                .filter(Column("syncStatus") == SyncStatus.pending.rawValue)
                .order(Column("createdAt").asc)
                .fetchAll(db)
        }
    }
    
    /// Fetch a single draft by ID
    func fetchDraft(id: String) async throws -> FormDraft? {
        try await database.database.read { db in
            try FormDraft.fetchOne(db, key: id)
        }
    }
    
    /// Create a new draft
    func createDraft(templateId: String, claimId: String?, inspectionId: String? = nil) async throws -> FormDraft {
        let draft = FormDraft(
            templateId: templateId,
            claimId: claimId,
            inspectionId: inspectionId
        )
        
        try await database.database.write { db in
            try draft.insert(db)
        }
        
        return draft
    }
    
    /// Update draft data (autosave)
    func updateDraftData(id: String, dataJson: String) async throws {
        try await database.database.write { db in
            try db.execute(
                sql: "UPDATE form_drafts SET dataJson = ?, lastSavedAt = ?, updatedAt = ? WHERE id = ?",
                arguments: [dataJson, Date(), Date(), id]
            )
        }
    }
    
    /// Mark draft as submitted
    func markSubmitted(id: String) async throws {
        try await database.database.write { db in
            try db.execute(
                sql: "UPDATE form_drafts SET status = ?, syncStatus = ?, updatedAt = ? WHERE id = ?",
                arguments: [FormDraftStatus.submitted.rawValue, SyncStatus.pending.rawValue, Date(), id]
            )
        }
    }
    
    /// Mark draft as synced
    func markSynced(id: String) async throws {
        try await database.database.write { db in
            try db.execute(
                sql: "UPDATE form_drafts SET status = ?, syncStatus = ?, updatedAt = ? WHERE id = ?",
                arguments: [FormDraftStatus.synced.rawValue, SyncStatus.synced.rawValue, Date(), id]
            )
        }
    }
    
    /// Mark draft sync as failed
    func markSyncFailed(id: String) async throws {
        try await database.database.write { db in
            try db.execute(
                sql: "UPDATE form_drafts SET status = ?, syncStatus = ?, updatedAt = ? WHERE id = ?",
                arguments: [FormDraftStatus.failed.rawValue, SyncStatus.failed.rawValue, Date(), id]
            )
        }
    }
    
    /// Delete a draft
    func deleteDraft(id: String) async throws {
        try await database.database.write { db in
            _ = try FormDraft.deleteOne(db, key: id)
        }
    }
    
    // MARK: - Statistics
    
    /// Get count of drafts by status
    func draftCountByStatus() async throws -> [FormDraftStatus: Int] {
        try await database.database.read { db in
            var counts: [FormDraftStatus: Int] = [:]
            for status in [FormDraftStatus.draft, .submitted, .synced, .failed] {
                let count = try FormDraft
                    .filter(Column("status") == status.rawValue)
                    .fetchCount(db)
                counts[status] = count
            }
            return counts
        }
    }
}
