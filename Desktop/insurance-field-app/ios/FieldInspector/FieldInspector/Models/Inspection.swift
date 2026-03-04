import Foundation
import GRDB

// MARK: - Inspection Status

enum InspectionStatus: String, Codable, CaseIterable, DatabaseValueConvertible {
    case notStarted = "not_started"
    case inProgress = "in_progress"
    case completed = "completed"
    
    var displayName: String {
        switch self {
        case .notStarted: return "Not Started"
        case .inProgress: return "In Progress"
        case .completed: return "Completed"
        }
    }
}

// MARK: - Field Value Type

enum FieldValueType: String, Codable, DatabaseValueConvertible {
    case text = "text"
    case number = "number"
    case dropdown = "dropdown"
    case toggle = "toggle"
    case date = "date"
    case signature = "signature"
    case photo = "photo"
}

// MARK: - Inspection Model

struct Inspection: Identifiable, Codable, Equatable, Hashable {
    var id: String
    var claimId: String
    var templateId: String
    var templateName: String?
    var status: InspectionStatus
    var startedAt: Date?
    var completedAt: Date?
    var createdAt: Date
    var updatedAt: Date
    var syncStatus: SyncStatus
    
    init(
        id: String = UUID().uuidString,
        claimId: String,
        templateId: String,
        templateName: String? = nil,
        status: InspectionStatus = .notStarted,
        startedAt: Date? = nil,
        completedAt: Date? = nil,
        createdAt: Date = Date(),
        updatedAt: Date = Date(),
        syncStatus: SyncStatus = .pending
    ) {
        self.id = id
        self.claimId = claimId
        self.templateId = templateId
        self.templateName = templateName
        self.status = status
        self.startedAt = startedAt
        self.completedAt = completedAt
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.syncStatus = syncStatus
    }
}

extension Inspection: FetchableRecord, PersistableRecord {
    static let databaseTableName = "inspections"
}

// MARK: - Inspection Field Model

struct InspectionField: Identifiable, Codable, Equatable {
    var id: String
    var inspectionId: String
    var sectionKey: String
    var fieldKey: String
    var value: String?
    var valueType: FieldValueType
    var required: Bool
    var displayOrder: Int
    var createdAt: Date
    var updatedAt: Date
    var syncStatus: SyncStatus
    
    init(
        id: String = UUID().uuidString,
        inspectionId: String,
        sectionKey: String,
        fieldKey: String,
        value: String? = nil,
        valueType: FieldValueType = .text,
        required: Bool = false,
        displayOrder: Int = 0,
        createdAt: Date = Date(),
        updatedAt: Date = Date(),
        syncStatus: SyncStatus = .pending
    ) {
        self.id = id
        self.inspectionId = inspectionId
        self.sectionKey = sectionKey
        self.fieldKey = fieldKey
        self.value = value
        self.valueType = valueType
        self.required = required
        self.displayOrder = displayOrder
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.syncStatus = syncStatus
    }
    
    var isComplete: Bool {
        if required {
            return value != nil && !value!.isEmpty
        }
        return true
    }
}

extension InspectionField: FetchableRecord, PersistableRecord {
    static let databaseTableName = "inspection_fields"
}
