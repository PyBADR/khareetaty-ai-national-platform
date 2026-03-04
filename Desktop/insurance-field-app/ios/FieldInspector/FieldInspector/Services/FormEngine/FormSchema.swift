import Foundation

// MARK: - Form Schema (JSON-Driven Forms)

/// Root schema for a JSON-driven form template
struct FormSchema: Codable, Equatable {
    let id: String
    let name: String
    let version: String
    let category: String
    let description: String?
    let sections: [FormSection]
    let submitButtonText: String?
    let validationRules: [FormValidationRule]?
    
    init(
        id: String,
        name: String,
        version: String = "1.0",
        category: String,
        description: String? = nil,
        sections: [FormSection],
        submitButtonText: String? = nil,
        validationRules: [FormValidationRule]? = nil
    ) {
        self.id = id
        self.name = name
        self.version = version
        self.category = category
        self.description = description
        self.sections = sections
        self.submitButtonText = submitButtonText
        self.validationRules = validationRules
    }
}

// MARK: - Form Section

struct FormSection: Codable, Equatable, Identifiable {
    let id: String
    let title: String
    let description: String?
    let icon: String?
    let isCollapsible: Bool
    let isInitiallyExpanded: Bool
    let fields: [FormField]
    
    init(
        id: String,
        title: String,
        description: String? = nil,
        icon: String? = nil,
        isCollapsible: Bool = true,
        isInitiallyExpanded: Bool = true,
        fields: [FormField]
    ) {
        self.id = id
        self.title = title
        self.description = description
        self.icon = icon
        self.isCollapsible = isCollapsible
        self.isInitiallyExpanded = isInitiallyExpanded
        self.fields = fields
    }
}

// MARK: - Form Field

struct FormField: Codable, Equatable, Identifiable {
    let id: String
    let type: FormFieldType
    let label: String
    let placeholder: String?
    let helpText: String?
    let isRequired: Bool
    let defaultValue: AnyCodableValue?
    let validation: FieldValidation?
    let options: [FieldOption]?  // For select, radio, checkbox
    let config: FieldConfig?
    
    init(
        id: String,
        type: FormFieldType,
        label: String,
        placeholder: String? = nil,
        helpText: String? = nil,
        isRequired: Bool = false,
        defaultValue: AnyCodableValue? = nil,
        validation: FieldValidation? = nil,
        options: [FieldOption]? = nil,
        config: FieldConfig? = nil
    ) {
        self.id = id
        self.type = type
        self.label = label
        self.placeholder = placeholder
        self.helpText = helpText
        self.isRequired = isRequired
        self.defaultValue = defaultValue
        self.validation = validation
        self.options = options
        self.config = config
    }
}

// MARK: - Form Field Type

enum FormFieldType: String, Codable, CaseIterable {
    case text = "text"
    case textArea = "textarea"
    case number = "number"
    case email = "email"
    case phone = "phone"
    case date = "date"
    case time = "time"
    case dateTime = "datetime"
    case select = "select"
    case radio = "radio"
    case checkbox = "checkbox"
    case toggle = "toggle"
    case slider = "slider"
    case photo = "photo"
    case photoGrid = "photo_grid"
    case signature = "signature"
    case location = "location"
    case voiceNote = "voice_note"
    case counter = "counter"
    case rating = "rating"
    case hidden = "hidden"
}

// MARK: - Field Option (for select, radio, checkbox)

struct FieldOption: Codable, Equatable, Identifiable {
    let id: String
    let label: String
    let value: String
    let icon: String?
    
    init(id: String? = nil, label: String, value: String, icon: String? = nil) {
        self.id = id ?? value
        self.label = label
        self.value = value
        self.icon = icon
    }
}

// MARK: - Field Validation

struct FieldValidation: Codable, Equatable {
    let minLength: Int?
    let maxLength: Int?
    let minValue: Double?
    let maxValue: Double?
    let pattern: String?  // Regex pattern
    let patternMessage: String?
    let minPhotos: Int?
    let maxPhotos: Int?
    
    init(
        minLength: Int? = nil,
        maxLength: Int? = nil,
        minValue: Double? = nil,
        maxValue: Double? = nil,
        pattern: String? = nil,
        patternMessage: String? = nil,
        minPhotos: Int? = nil,
        maxPhotos: Int? = nil
    ) {
        self.minLength = minLength
        self.maxLength = maxLength
        self.minValue = minValue
        self.maxValue = maxValue
        self.pattern = pattern
        self.patternMessage = patternMessage
        self.minPhotos = minPhotos
        self.maxPhotos = maxPhotos
    }
}

// MARK: - Field Config (type-specific configuration)

struct FieldConfig: Codable, Equatable {
    // Slider config
    let sliderMin: Double?
    let sliderMax: Double?
    let sliderStep: Double?
    let sliderLabels: [String]?  // Labels for min/max
    
    // Photo config
    let photoColumns: Int?
    let photoLabel: String?
    let allowCamera: Bool?
    let allowGallery: Bool?
    
    // Counter config
    let counterMin: Int?
    let counterMax: Int?
    
    // Rating config
    let ratingMax: Int?
    let ratingIcon: String?
    
    // Location config
    let showMap: Bool?
    let autoCapture: Bool?
    
    init(
        sliderMin: Double? = nil,
        sliderMax: Double? = nil,
        sliderStep: Double? = nil,
        sliderLabels: [String]? = nil,
        photoColumns: Int? = nil,
        photoLabel: String? = nil,
        allowCamera: Bool? = nil,
        allowGallery: Bool? = nil,
        counterMin: Int? = nil,
        counterMax: Int? = nil,
        ratingMax: Int? = nil,
        ratingIcon: String? = nil,
        showMap: Bool? = nil,
        autoCapture: Bool? = nil
    ) {
        self.sliderMin = sliderMin
        self.sliderMax = sliderMax
        self.sliderStep = sliderStep
        self.sliderLabels = sliderLabels
        self.photoColumns = photoColumns
        self.photoLabel = photoLabel
        self.allowCamera = allowCamera
        self.allowGallery = allowGallery
        self.counterMin = counterMin
        self.counterMax = counterMax
        self.ratingMax = ratingMax
        self.ratingIcon = ratingIcon
        self.showMap = showMap
        self.autoCapture = autoCapture
    }
}

// MARK: - Form Validation Rule (cross-field validation)

struct FormValidationRule: Codable, Equatable {
    let id: String
    let type: ValidationRuleType
    let fields: [String]  // Field IDs involved
    let message: String
    let condition: String?  // JSON Logic or simple expression
    
    init(
        id: String,
        type: ValidationRuleType,
        fields: [String],
        message: String,
        condition: String? = nil
    ) {
        self.id = id
        self.type = type
        self.fields = fields
        self.message = message
        self.condition = condition
    }
}

enum ValidationRuleType: String, Codable {
    case requiredIf = "required_if"
    case requiredUnless = "required_unless"
    case matchField = "match_field"
    case custom = "custom"
}

// MARK: - AnyCodableValue (for dynamic default values)

struct AnyCodableValue: Codable, Equatable {
    let value: Any
    
    init(_ value: Any) {
        self.value = value
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        
        if let intValue = try? container.decode(Int.self) {
            value = intValue
        } else if let doubleValue = try? container.decode(Double.self) {
            value = doubleValue
        } else if let boolValue = try? container.decode(Bool.self) {
            value = boolValue
        } else if let stringValue = try? container.decode(String.self) {
            value = stringValue
        } else if let arrayValue = try? container.decode([AnyCodableValue].self) {
            value = arrayValue.map { $0.value }
        } else if let dictValue = try? container.decode([String: AnyCodableValue].self) {
            value = dictValue.mapValues { $0.value }
        } else {
            value = NSNull()
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        
        switch value {
        case let intValue as Int:
            try container.encode(intValue)
        case let doubleValue as Double:
            try container.encode(doubleValue)
        case let boolValue as Bool:
            try container.encode(boolValue)
        case let stringValue as String:
            try container.encode(stringValue)
        case let arrayValue as [Any]:
            try container.encode(arrayValue.map { AnyCodableValue($0) })
        case let dictValue as [String: Any]:
            try container.encode(dictValue.mapValues { AnyCodableValue($0) })
        default:
            try container.encodeNil()
        }
    }
    
    static func == (lhs: AnyCodableValue, rhs: AnyCodableValue) -> Bool {
        // Simple equality check for common types
        switch (lhs.value, rhs.value) {
        case (let l as Int, let r as Int): return l == r
        case (let l as Double, let r as Double): return l == r
        case (let l as Bool, let r as Bool): return l == r
        case (let l as String, let r as String): return l == r
        default: return false
        }
    }
    
    var stringValue: String? { value as? String }
    var intValue: Int? { value as? Int }
    var doubleValue: Double? { value as? Double }
    var boolValue: Bool? { value as? Bool }
}
