import Foundation

// MARK: - Inspection Template

struct InspectionTemplate: Codable, Identifiable {
    let id: String
    let name: String
    let description: String?
    let version: String
    let claimType: String
    let sections: [TemplateSection]
    let isActive: Bool
    
    enum CodingKeys: String, CodingKey {
        case id, name, description, version, claimType, sections, isActive
    }
}

// MARK: - Template Section

struct TemplateSection: Codable, Identifiable {
    let key: String
    let title: String
    let description: String?
    let order: Int
    let fields: [TemplateField]
    
    var id: String { key }
}

// MARK: - Template Field

struct TemplateField: Codable, Identifiable {
    let key: String
    let label: String
    let type: FieldValueType
    let required: Bool
    let order: Int
    let placeholder: String?
    let options: [String]?
    let multiline: Bool?
    
    var id: String { key }
    
    enum CodingKeys: String, CodingKey {
        case key, label, type, required, order, placeholder, options, multiline
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        key = try container.decode(String.self, forKey: .key)
        label = try container.decode(String.self, forKey: .label)
        
        // Handle type as string and convert to enum
        let typeString = try container.decode(String.self, forKey: .type)
        type = FieldValueType(rawValue: typeString) ?? .text
        
        required = try container.decodeIfPresent(Bool.self, forKey: .required) ?? false
        order = try container.decodeIfPresent(Int.self, forKey: .order) ?? 0
        placeholder = try container.decodeIfPresent(String.self, forKey: .placeholder)
        options = try container.decodeIfPresent([String].self, forKey: .options)
        multiline = try container.decodeIfPresent(Bool.self, forKey: .multiline)
    }
}

// MARK: - Template JSON Wrapper (for API response)

struct TemplateWrapper: Codable {
    let name: String
    let description: String?
    let version: String
    let claimType: String
    let sections: [TemplateSection]
}

// MARK: - Default Motor Inspection Template

extension InspectionTemplate {
    static let motorInspection: InspectionTemplate = {
        let sections = [
            TemplateSection(
                key: "vehicle_info",
                title: "Vehicle Information",
                description: "Verify and record vehicle details",
                order: 1,
                fields: [
                    TemplateField(
                        key: "vin_verified",
                        label: "VIN Verified",
                        type: .toggle,
                        required: true,
                        order: 1,
                        placeholder: nil,
                        options: nil,
                        multiline: nil
                    ),
                    TemplateField(
                        key: "odometer_reading",
                        label: "Odometer Reading",
                        type: .number,
                        required: true,
                        order: 2,
                        placeholder: "Enter current mileage",
                        options: nil,
                        multiline: nil
                    ),
                    TemplateField(
                        key: "vehicle_condition",
                        label: "Overall Vehicle Condition",
                        type: .dropdown,
                        required: true,
                        order: 3,
                        placeholder: nil,
                        options: ["Excellent", "Good", "Fair", "Poor"],
                        multiline: nil
                    ),
                ]
            ),
            TemplateSection(
                key: "damage_areas",
                title: "Damage Assessment",
                description: "Document all damage areas",
                order: 2,
                fields: [
                    TemplateField(
                        key: "front_bumper_damage",
                        label: "Front Bumper Damage",
                        type: .dropdown,
                        required: true,
                        order: 1,
                        placeholder: nil,
                        options: ["None", "Minor Scratches", "Dents", "Cracked", "Severe"],
                        multiline: nil
                    ),
                    TemplateField(
                        key: "rear_bumper_damage",
                        label: "Rear Bumper Damage",
                        type: .dropdown,
                        required: true,
                        order: 2,
                        placeholder: nil,
                        options: ["None", "Minor Scratches", "Dents", "Cracked", "Severe"],
                        multiline: nil
                    ),
                    TemplateField(
                        key: "damage_description",
                        label: "Detailed Damage Description",
                        type: .text,
                        required: true,
                        order: 3,
                        placeholder: "Describe all visible damage in detail...",
                        options: nil,
                        multiline: true
                    ),
                ]
            ),
            TemplateSection(
                key: "photos_checklist",
                title: "Photo Documentation",
                description: "Required photos for the inspection",
                order: 3,
                fields: [
                    TemplateField(
                        key: "photo_front",
                        label: "Front View Photo",
                        type: .photo,
                        required: true,
                        order: 1,
                        placeholder: nil,
                        options: nil,
                        multiline: nil
                    ),
                    TemplateField(
                        key: "photo_rear",
                        label: "Rear View Photo",
                        type: .photo,
                        required: true,
                        order: 2,
                        placeholder: nil,
                        options: nil,
                        multiline: nil
                    ),
                    TemplateField(
                        key: "photo_damage",
                        label: "Primary Damage Photo",
                        type: .photo,
                        required: true,
                        order: 3,
                        placeholder: nil,
                        options: nil,
                        multiline: nil
                    ),
                ]
            ),
            TemplateSection(
                key: "approval",
                title: "Approval & Signature",
                description: "Final approval and signature",
                order: 4,
                fields: [
                    TemplateField(
                        key: "inspection_complete",
                        label: "Inspection Complete",
                        type: .toggle,
                        required: true,
                        order: 1,
                        placeholder: nil,
                        options: nil,
                        multiline: nil
                    ),
                    TemplateField(
                        key: "estimated_repair_cost",
                        label: "Estimated Repair Cost",
                        type: .number,
                        required: true,
                        order: 2,
                        placeholder: "Enter estimated cost in USD",
                        options: nil,
                        multiline: nil
                    ),
                    TemplateField(
                        key: "recommendation",
                        label: "Recommendation",
                        type: .dropdown,
                        required: true,
                        order: 3,
                        placeholder: nil,
                        options: ["Approve Repair", "Total Loss", "Further Investigation", "Deny Claim"],
                        multiline: nil
                    ),
                    TemplateField(
                        key: "inspection_date",
                        label: "Inspection Date",
                        type: .date,
                        required: true,
                        order: 4,
                        placeholder: nil,
                        options: nil,
                        multiline: nil
                    ),
                    TemplateField(
                        key: "inspector_signature",
                        label: "Inspector Signature",
                        type: .signature,
                        required: true,
                        order: 5,
                        placeholder: nil,
                        options: nil,
                        multiline: nil
                    ),
                ]
            ),
        ]
        
        return InspectionTemplate(
            id: "motor-inspection-v1",
            name: "Motor Vehicle Inspection",
            description: "Standard inspection template for motor vehicle claims",
            version: "1.0",
            claimType: "motor",
            sections: sections,
            isActive: true
        )
    }()
}

// MARK: - TemplateField Memberwise Init Extension

extension TemplateField {
    init(
        key: String,
        label: String,
        type: FieldValueType,
        required: Bool,
        order: Int,
        placeholder: String?,
        options: [String]?,
        multiline: Bool?
    ) {
        self.key = key
        self.label = label
        self.type = type
        self.required = required
        self.order = order
        self.placeholder = placeholder
        self.options = options
        self.multiline = multiline
    }
}
