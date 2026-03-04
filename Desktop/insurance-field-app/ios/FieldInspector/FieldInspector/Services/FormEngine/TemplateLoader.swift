import Foundation

/// Loads form templates from bundle and manages template cache
@MainActor
final class TemplateLoader {
    
    // MARK: - Singleton
    
    static let shared = TemplateLoader()
    
    // MARK: - Properties
    
    private var templateCache: [String: FormSchema] = [:]
    private let formRepository: FormRepository
    
    // MARK: - Initialization
    
    private init() {
        self.formRepository = FormRepository.shared
    }
    
    // MARK: - Load from Bundle
    
    /// Load all templates from bundle Forms/Templates/*.json
    func loadBundleTemplates() async throws -> [FormSchema] {
        var templates: [FormSchema] = []
        
        guard let bundlePath = Bundle.main.resourcePath else {
            throw TemplateLoaderError.bundleNotFound
        }
        
        let templatesPath = (bundlePath as NSString).appendingPathComponent("Forms/Templates")
        let fileManager = FileManager.default
        
        // Check if directory exists
        var isDirectory: ObjCBool = false
        guard fileManager.fileExists(atPath: templatesPath, isDirectory: &isDirectory),
              isDirectory.boolValue else {
            AppLogger.sync.warning("Templates directory not found at: \(templatesPath, privacy: .public)")
            return templates
        }
        
        // Get all JSON files
        let files = try fileManager.contentsOfDirectory(atPath: templatesPath)
        let jsonFiles = files.filter { $0.hasSuffix(".json") }
        
        for filename in jsonFiles {
            let filePath = (templatesPath as NSString).appendingPathComponent(filename)
            
            do {
                let data = try Data(contentsOf: URL(fileURLWithPath: filePath))
                let schema = try JSONDecoder().decode(FormSchema.self, from: data)
                templates.append(schema)
                templateCache[schema.id] = schema
                
                AppLogger.sync.info("Loaded template: \(schema.name, privacy: .public) (\(schema.id, privacy: .public))")
            } catch {
                AppLogger.error("Failed to load template \(filename)", error: error, category: AppLogger.sync)
            }
        }
        
        // Sync to database
        for schema in templates {
            try await syncTemplateToDatabase(schema)
        }
        
        return templates
    }
    
    /// Load a specific template by ID from cache or bundle
    func loadTemplate(id: String) async throws -> FormSchema {
        // Check cache first
        if let cached = templateCache[id] {
            return cached
        }
        
        // Try to load from database
        if let dbTemplate = try await formRepository.fetchTemplate(id: id) {
            let schema = try JSONDecoder().decode(
                FormSchema.self,
                from: dbTemplate.schemaJson.data(using: .utf8) ?? Data()
            )
            templateCache[id] = schema
            return schema
        }
        
        // Try to load from bundle
        if let bundleSchema = try loadFromBundle(id: id) {
            templateCache[id] = bundleSchema
            return bundleSchema
        }
        
        throw TemplateLoaderError.templateNotFound(id)
    }
    
    /// Load template from bundle by ID
    private func loadFromBundle(id: String) throws -> FormSchema? {
        guard let bundlePath = Bundle.main.resourcePath else {
            return nil
        }
        
        let templatesPath = (bundlePath as NSString).appendingPathComponent("Forms/Templates")
        let filePath = (templatesPath as NSString).appendingPathComponent("\(id).json")
        
        guard FileManager.default.fileExists(atPath: filePath) else {
            return nil
        }
        
        let data = try Data(contentsOf: URL(fileURLWithPath: filePath))
        return try JSONDecoder().decode(FormSchema.self, from: data)
    }
    
    // MARK: - Database Sync
    
    /// Sync a template schema to the database
    private func syncTemplateToDatabase(_ schema: FormSchema) async throws {
        let encoder = JSONEncoder()
        encoder.outputFormatting = .prettyPrinted
        let schemaData = try encoder.encode(schema)
        let schemaJson = String(data: schemaData, encoding: .utf8) ?? "{}"
        
        let template = FormTemplate(
            id: schema.id,
            name: schema.name,
            version: schema.version,
            category: schema.category,
            schemaJson: schemaJson,
            isActive: true
        )
        
        try await formRepository.saveTemplate(template)
    }
    
    // MARK: - Cache Management
    
    /// Clear the template cache
    func clearCache() {
        templateCache.removeAll()
    }
    
    /// Get all cached templates
    func getCachedTemplates() -> [FormSchema] {
        Array(templateCache.values)
    }
    
    /// Reload all templates from bundle
    func reloadTemplates() async throws -> [FormSchema] {
        clearCache()
        return try await loadBundleTemplates()
    }
}

// MARK: - Template Loader Error

enum TemplateLoaderError: LocalizedError {
    case bundleNotFound
    case templateNotFound(String)
    case invalidSchema(String)
    
    var errorDescription: String? {
        switch self {
        case .bundleNotFound:
            return "Bundle resource path not found"
        case .templateNotFound(let id):
            return "Template not found: \(id)"
        case .invalidSchema(let reason):
            return "Invalid template schema: \(reason)"
        }
    }
}
