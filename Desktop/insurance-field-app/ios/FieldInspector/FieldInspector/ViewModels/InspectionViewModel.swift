import Foundation
import GRDB
import Combine

/// ViewModel for managing inspection forms and field updates
@MainActor
class InspectionViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var inspection: Inspection?
    @Published var template: InspectionTemplate?
    @Published var fields: [InspectionField] = []
    @Published var fieldValues: [String: String] = [:]
    @Published var isLoading = false
    @Published var isSaving = false
    @Published var errorMessage: String?
    @Published var currentSectionIndex = 0
    @Published var completionProgress: Double = 0.0
    
    // MARK: - Properties
    
    private let database: DatabaseManager
    private let api: APIService
    private let sync: SyncService
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(
        database: DatabaseManager = .shared,
        api: APIService = .shared,
        sync: SyncService = .shared
    ) {
        self.database = database
        self.api = api
        self.sync = sync
    }
    
    // MARK: - Public Methods
    
    /// Load inspection and template
    func loadInspection(id: String) async {
        isLoading = true
        errorMessage = nil
        
        do {
            // Load from local database first
            let localInspection = try await database.database.read { db in
                try Inspection.fetchOne(db, key: id)
            }
            
            if let localInspection = localInspection {
                inspection = localInspection
                
                // Load fields
                fields = try await database.database.read { db in
                    try InspectionField
                        .filter(Column("inspectionId") == id)
                        .fetchAll(db)
                }
                
                // Populate field values
                for field in fields {
                    let key = "\(field.sectionKey).\(field.fieldKey)"
                    fieldValues[key] = field.value ?? ""
                }
                
                // Load template
                await loadTemplate(templateId: localInspection.templateId)
                
                updateProgress()
            }
            
            // Try to fetch from server
            if sync.isOnline {
                let response = try await api.getInspection(id: id)
                inspection = response.inspection
                
                if let templateWrapper = response.template {
                    template = InspectionTemplate(
                        id: localInspection?.templateId ?? "motor-inspection-v1",
                        name: templateWrapper.name,
                        description: templateWrapper.description,
                        version: templateWrapper.version,
                        claimType: templateWrapper.claimType,
                        sections: templateWrapper.sections,
                        isActive: true
                    )
                }
            }
            
            isLoading = false
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            
            // Use default template as fallback
            template = InspectionTemplate.motorInspection
        }
    }
    
    /// Load template
    private func loadTemplate(templateId: String) async {
        // For now, use the hardcoded motor inspection template
        // In production, this would fetch from server or local storage
        template = InspectionTemplate.motorInspection
    }
    
    /// Update a field value
    func updateField(sectionKey: String, fieldKey: String, value: String?) async {
        guard let inspection = inspection else { return }
        
        let key = "\(sectionKey).\(fieldKey)"
        fieldValues[key] = value ?? ""
        
        isSaving = true
        
        do {
            // Update or create field in local database
            try await database.database.write { db in
                if let existingField = try InspectionField
                    .filter(Column("inspectionId") == inspection.id)
                    .filter(Column("sectionKey") == sectionKey)
                    .filter(Column("fieldKey") == fieldKey)
                    .fetchOne(db) {
                    
                    var updated = existingField
                    updated.value = value
                    updated.updatedAt = Date()
                    try updated.update(db)
                } else {
                    // Create new field
                    let newField = InspectionField(
                        id: UUID().uuidString,
                        inspectionId: inspection.id,
                        sectionKey: sectionKey,
                        fieldKey: fieldKey,
                        value: value,
                        valueType: .text,
                        required: false,
                        displayOrder: 0,
                        createdAt: Date(),
                        updatedAt: Date(),
                        syncStatus: .pending
                    )
                    try newField.insert(db)
                }
            }
            
            // Queue sync
            try await sync.queueSync(
                entityType: .inspectionField,
                entityId: "\(inspection.id)-\(sectionKey)-\(fieldKey)",
                operation: .update,
                payload: ["sectionKey": sectionKey, "fieldKey": fieldKey, "value": value ?? ""]
            )
            
            // Try to sync to server if online
            if sync.isOnline {
                _ = try await api.updateInspectionFields(
                    id: inspection.id,
                    fields: [FieldUpdate(sectionKey: sectionKey, fieldKey: fieldKey, value: value)]
                )
            }
            
            updateProgress()
            isSaving = false
        } catch {
            print("Error updating field: \(error)")
            isSaving = false
        }
    }
    
    /// Complete the inspection
    func completeInspection() async throws {
        guard let inspection = inspection else { return }
        
        // Validate all required fields are filled
        guard isFormComplete else {
            throw NSError(domain: "InspectionViewModel", code: 1, userInfo: [
                NSLocalizedDescriptionKey: "Please complete all required fields"
            ])
        }
        
        // Update inspection status
        var updated = inspection
        updated.status = .completed
        updated.completedAt = Date()
        updated.updatedAt = Date()
        
        let inspectionToSave = updated
        try await database.database.write { db in
            try inspectionToSave.update(db)
        }
        
        // Queue sync
        try await sync.queueSync(
            entityType: .inspection,
            entityId: inspection.id,
            operation: .update,
            payload: updated
        )
        
        // Try to sync to server if online
        if sync.isOnline {
            _ = try await api.completeInspection(id: inspection.id)
        }
        
        self.inspection = updated
    }
    
    /// Check if form is complete
    var isFormComplete: Bool {
        guard let template = template else { return false }
        
        for section in template.sections {
            for field in section.fields where field.required {
                let key = "\(section.key).\(field.key)"
                if fieldValues[key]?.isEmpty ?? true {
                    return false
                }
            }
        }
        return true
    }
    
    /// Check if a section is complete
    func isSectionComplete(_ section: TemplateSection) -> Bool {
        for field in section.fields where field.required {
            let key = "\(section.key).\(field.key)"
            if fieldValues[key]?.isEmpty ?? true {
                return false
            }
        }
        return true
    }
    
    /// Update completion progress
    private func updateProgress() {
        guard let template = template else {
            completionProgress = 0.0
            return
        }
        
        var totalRequired = 0
        var completed = 0
        
        for section in template.sections {
            for field in section.fields where field.required {
                totalRequired += 1
                let key = "\(section.key).\(field.key)"
                if !(fieldValues[key]?.isEmpty ?? true) {
                    completed += 1
                }
            }
        }
        
        completionProgress = totalRequired > 0 ? Double(completed) / Double(totalRequired) : 0.0
    }
}
