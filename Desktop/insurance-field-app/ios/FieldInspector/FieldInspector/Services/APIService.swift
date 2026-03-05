import Foundation

/// Notification posted when session expires and user needs to re-login
extension Notification.Name {
    static let sessionExpired = Notification.Name("DeevoSentinelSessionExpired")
}

/// API Service for communicating with the backend
actor APIService {
    
    // MARK: - Singleton
    
    static let shared = APIService()
    
    // MARK: - Properties
    
    private var baseURL: URL
    private var currentTenantId: String?
    private let session: URLSession
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    private let authCoordinator: AuthRefreshCoordinator
    private let keychainStore: KeychainStore
    
    // MARK: - Initialization
    
    private init() {
        // Load API URL from Config (populated via xcconfig -> Info.plist)
        self.baseURL = Config.apiBaseURL
        
        let sessionConfig = URLSessionConfiguration.default
        sessionConfig.timeoutIntervalForRequest = Config.apiTimeoutSeconds
        sessionConfig.timeoutIntervalForResource = Config.apiTimeoutSeconds * 2
        self.session = URLSession(configuration: sessionConfig)
        
        self.decoder = JSONDecoder()
        self.decoder.dateDecodingStrategy = .iso8601
        
        self.encoder = JSONEncoder()
        self.encoder.dateEncodingStrategy = .iso8601
        
        // Initialize secure storage and auth coordinator
        self.keychainStore = KeychainStore()
        self.authCoordinator = AuthRefreshCoordinator(
            keychainStore: keychainStore,
            apiBaseURL: Config.apiBaseURL.absoluteString
        )
        
        let urlString = self.baseURL.absoluteString
        AppLogger.api.info("APIService initialized with base URL: \(urlString, privacy: .public)")
    }
    
    // MARK: - Configuration
    
    func configure(baseURL: URL) {
        self.baseURL = baseURL
    }
    
    func setAuthToken(_ token: String, refreshToken: String, expiresIn: Int) async throws {
        let tokens = AuthTokens(
            accessToken: token,
            refreshToken: refreshToken,
            expiresAt: Date().addingTimeInterval(TimeInterval(expiresIn))
        )
        try await authCoordinator.setTokens(tokens)
    }
    
    func clearAuthToken() async throws {
        try await authCoordinator.clearTokens()
    }
    
    func setTenantId(_ tenantId: String?) {
        self.currentTenantId = tenantId
    }
    
    func getTenantId() -> String? {
        return currentTenantId
    }
    
    // MARK: - Generic Request
    
    private func request<T: Decodable>(
        endpoint: String,
        method: String = "GET",
        body: Encodable? = nil,
        queryItems: [URLQueryItem]? = nil,
        retryOn401: Bool = true
    ) async throws -> T {
        var urlComponents = URLComponents(url: baseURL.appendingPathComponent(endpoint), resolvingAgainstBaseURL: true)!
        urlComponents.queryItems = queryItems
        
        guard let url = urlComponents.url else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Get valid token from auth coordinator (handles refresh if needed)
        if let token = try? await authCoordinator.validAccessToken() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        if let body = body {
            request.httpBody = try encoder.encode(body)
        }
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        switch httpResponse.statusCode {
        case 200...299:
            return try decoder.decode(T.self, from: data)
        case 401:
            // Try to refresh token once if enabled
            if retryOn401 {
                // Force refresh and retry
                _ = try? await authCoordinator.refreshIfNeeded()
                let refreshed = try? await authCoordinator.validAccessToken()
                if refreshed != nil {
                    // Retry the original request with new token (no more retries)
                    return try await self.request(
                        endpoint: endpoint,
                        method: method,
                        body: body,
                        queryItems: queryItems,
                        retryOn401: false
                    )
                }
            }
            // Token refresh failed or not attempted - notify session expired
            await notifySessionExpired()
            throw APIError.sessionExpired
        case 403:
            throw APIError.forbidden
        case 404:
            throw APIError.notFound
        case 409:
            throw APIError.conflict
        case 400...499:
            if let errorResponse = try? decoder.decode(ErrorResponse.self, from: data) {
                throw APIError.clientError(errorResponse.error)
            }
            throw APIError.clientError("Request failed")
        case 500...599:
            throw APIError.serverError
        default:
            throw APIError.unknown
        }
    }
    
    // MARK: - Session Management
    
    /// Notify that the session has expired
    private func notifySessionExpired() async {
        await MainActor.run {
            NotificationCenter.default.post(name: .sessionExpired, object: nil)
        }
    }
    
    /// Clear authentication state (call on logout)
    func clearAuth() async throws {
        try await clearAuthToken()
        self.currentTenantId = nil
    }
    
    // MARK: - Auth Endpoints
    
    func login(email: String, password: String) async throws -> LoginResponse {
        struct LoginRequest: Encodable {
            let email: String
            let password: String
        }
        
        let response: LoginResponse = try await request(
            endpoint: "auth",
            method: "POST",
            body: LoginRequest(email: email, password: password)
        )
        
        try await setAuthToken(
            response.token,
            refreshToken: response.refreshToken ?? "",
            expiresIn: response.expiresIn ?? 3600
        )
        setTenantId(response.user.tenantId)
        return response
    }
    
    func getCurrentUser() async throws -> User {
        struct UserResponse: Decodable {
            let user: User
        }
        let response: UserResponse = try await request(endpoint: "auth")
        return response.user
    }
    
    // MARK: - Claims Endpoints
    
    func getClaims(
        status: ClaimStatus? = nil,
        priority: ClaimPriority? = nil,
        assignedToMe: Bool = false,
        search: String? = nil,
        page: Int = 1,
        limit: Int = 20
    ) async throws -> ClaimsResponse {
        var queryItems: [URLQueryItem] = [
            URLQueryItem(name: "page", value: String(page)),
            URLQueryItem(name: "limit", value: String(limit)),
        ]
        
        if let status = status {
            queryItems.append(URLQueryItem(name: "status", value: status.rawValue))
        }
        if let priority = priority {
            queryItems.append(URLQueryItem(name: "priority", value: priority.rawValue))
        }
        if assignedToMe {
            queryItems.append(URLQueryItem(name: "assignedToMe", value: "true"))
        }
        if let search = search, !search.isEmpty {
            queryItems.append(URLQueryItem(name: "search", value: search))
        }
        
        return try await request(endpoint: "claims", queryItems: queryItems)
    }
    
    func getClaim(id: String) async throws -> ClaimDetailResponse {
        return try await request(endpoint: "claims/\(id)")
    }
    
    func acceptClaim(id: String) async throws -> ClaimResponse {
        return try await request(endpoint: "claims/\(id)/accept", method: "POST")
    }
    
    func updateClaim(id: String, updates: ClaimUpdate) async throws -> ClaimResponse {
        return try await request(endpoint: "claims/\(id)", method: "PUT", body: updates)
    }
    
    // MARK: - Inspections Endpoints
    
    func getInspections(claimId: String? = nil) async throws -> InspectionsResponse {
        var queryItems: [URLQueryItem]? = nil
        if let claimId = claimId {
            queryItems = [URLQueryItem(name: "claimId", value: claimId)]
        }
        return try await request(endpoint: "inspections", queryItems: queryItems)
    }
    
    func createInspection(claimId: String, templateId: String) async throws -> InspectionResponse {
        struct CreateRequest: Encodable {
            let claimId: String
            let templateId: String
        }
        return try await request(
            endpoint: "inspections",
            method: "POST",
            body: CreateRequest(claimId: claimId, templateId: templateId)
        )
    }
    
    func getInspection(id: String) async throws -> InspectionDetailResponse {
        return try await request(endpoint: "inspections/\(id)")
    }
    
    func updateInspectionFields(id: String, fields: [FieldUpdate]) async throws -> FieldsResponse {
        struct UpdateRequest: Encodable {
            let fields: [FieldUpdate]
        }
        return try await request(
            endpoint: "inspections/\(id)/fields",
            method: "PUT",
            body: UpdateRequest(fields: fields)
        )
    }
    
    func completeInspection(id: String) async throws -> InspectionResponse {
        struct StatusUpdate: Encodable {
            let status: String
        }
        return try await request(
            endpoint: "inspections/\(id)",
            method: "PUT",
            body: StatusUpdate(status: "completed")
        )
    }
    
    // MARK: - Media Endpoints
    
    func getMediaAssets(claimId: String? = nil, inspectionId: String? = nil) async throws -> MediaAssetsResponse {
        var queryItems: [URLQueryItem] = []
        if let claimId = claimId {
            queryItems.append(URLQueryItem(name: "claimId", value: claimId))
        }
        if let inspectionId = inspectionId {
            queryItems.append(URLQueryItem(name: "inspectionId", value: inspectionId))
        }
        return try await request(endpoint: "media", queryItems: queryItems.isEmpty ? nil : queryItems)
    }
    
    func createMediaAsset(_ asset: MediaAssetCreate) async throws -> MediaAssetResponse {
        return try await request(endpoint: "media", method: "POST", body: asset)
    }
    
    /// Upload media file to server
    func uploadMedia(fileURL: URL, claimId: String) async throws -> MediaUploadResponse {
        let url = baseURL.appendingPathComponent("media/upload")
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        if let token = try? await authCoordinator.validAccessToken() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        
        // Add claimId field
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"claimId\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(claimId)\r\n".data(using: .utf8)!)
        
        // Add file
        let filename = fileURL.lastPathComponent
        let mimeType = "application/octet-stream"
        
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)
        
        if let fileData = try? Data(contentsOf: fileURL) {
            body.append(fileData)
        }
        
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        guard httpResponse.statusCode >= 200 && httpResponse.statusCode < 300 else {
            throw APIError.serverError
        }
        
        return try decoder.decode(MediaUploadResponse.self, from: data)
    }
    
    // MARK: - AI Endpoints
    
    func getAISuggestion(claimId: String) async throws -> AISuggestionResponse {
        return try await request(
            endpoint: "ai/suggest",
            method: "POST",
            body: AISuggestionRequest(claimId: claimId)
        )
    }
    
    // MARK: - Templates Endpoints
    
    func getTemplates(claimType: String? = nil) async throws -> TemplatesResponse {
        var queryItems: [URLQueryItem]? = nil
        if let claimType = claimType {
            queryItems = [URLQueryItem(name: "claimType", value: claimType)]
        }
        return try await request(endpoint: "templates", queryItems: queryItems)
    }
    
    // MARK: - Sync Endpoints
    
    func pushSync(request: SyncPushRequest) async throws -> SyncPushResponse {
        return try await self.request(endpoint: "sync/push", method: "POST", body: request)
    }
    
    func pullSync(request: SyncPullRequest) async throws -> SyncPullResponse {
        return try await self.request(endpoint: "sync/pull", method: "POST", body: request)
    }
    
    // MARK: - Queue Operation Endpoints (for OperationProcessor)
    
    /// Submit a form via the queue
    func submitForm(payload: FormSubmissionPayload) async throws {
        struct SubmitRequest: Encodable {
            let templateId: String
            let claimId: String?
            let inspectionId: String?
            let data: String
        }
        let _: EmptyResponse = try await request(
            endpoint: "forms/submit",
            method: "POST",
            body: SubmitRequest(
                templateId: payload.templateId,
                claimId: payload.claimId,
                inspectionId: payload.inspectionId,
                data: payload.dataJson
            )
        )
    }
    
    /// Upload evidence via the queue
    func uploadEvidence(payload: EvidenceUploadPayload) async throws -> String {
        let fileURL = URL(fileURLWithPath: payload.localPath)
        let response = try await uploadMedia(fileURL: fileURL, claimId: payload.claimId)
        return response.url
    }
    
    /// Update a claim via the queue
    func updateClaim(payload: ClaimUpdatePayload) async throws {
        var updates = ClaimUpdate()
        if let status = payload.updates["status"] {
            updates.status = status
        }
        if let priority = payload.updates["priority"] {
            updates.priority = priority
        }
        _ = try await updateClaim(id: payload.claimId, updates: updates)
    }
    
    /// Create an inspection via the queue
    func createInspection(payload: InspectionCreatePayload) async throws {
        _ = try await createInspection(claimId: payload.claimId, templateId: payload.templateId)
    }
    
    /// Update an inspection via the queue
    func updateInspection(payload: InspectionUpdatePayload) async throws {
        let fields = payload.fields.map { key, value in
            FieldUpdate(sectionKey: "", fieldKey: key, value: value)
        }
        _ = try await updateInspectionFields(id: payload.inspectionId, fields: fields)
    }
    
    /// Delete media via the queue
    func deleteMedia(mediaAssetId: String) async throws {
        let _: EmptyResponse = try await request(
            endpoint: "media/\(mediaAssetId)",
            method: "DELETE"
        )
    }
}

/// Empty response for endpoints that return no data
struct EmptyResponse: Decodable {}

// MARK: - API Error

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case unauthorized
    case sessionExpired
    case forbidden
    case notFound
    case conflict
    case clientError(String)
    case serverError
    case unknown
    
    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case .invalidResponse: return "Invalid response from server"
        case .unauthorized: return "Please log in again"
        case .sessionExpired: return "Your session has expired. Please log in again."
        case .forbidden: return "You don't have permission to perform this action"
        case .notFound: return "Resource not found"
        case .conflict: return "Conflict with existing data"
        case .clientError(let message): return message
        case .serverError: return "Server error. Please try again later."
        case .unknown: return "An unknown error occurred"
        }
    }
    
    var requiresReauth: Bool {
        switch self {
        case .sessionExpired, .unauthorized:
            return true
        default:
            return false
        }
    }
}

// MARK: - Response Types

struct ErrorResponse: Decodable {
    let error: String
}

struct TokenRefreshResponse: Decodable {
    let token: String
    let user: User
}

struct ClaimsResponse: Decodable {
    let claims: [Claim]
    let pagination: Pagination
}

struct Pagination: Decodable {
    let page: Int
    let limit: Int
    let total: Int
    let totalPages: Int
}

struct ClaimResponse: Decodable {
    let claim: Claim
}

struct ClaimDetailResponse: Decodable {
    let claim: Claim
}

struct ClaimUpdate: Encodable {
    var status: String?
    var priority: String?
}

struct InspectionsResponse: Decodable {
    let inspections: [Inspection]
}

struct InspectionResponse: Decodable {
    let inspection: Inspection
}

struct InspectionDetailResponse: Decodable {
    let inspection: Inspection
    let template: TemplateWrapper?
}

struct FieldUpdate: Encodable {
    let sectionKey: String
    let fieldKey: String
    let value: String?
}

struct FieldsResponse: Decodable {
    let fields: [InspectionField]
}

struct MediaAssetsResponse: Decodable {
    let mediaAssets: [MediaAsset]
}

struct MediaAssetCreate: Encodable {
    let claimId: String
    let inspectionId: String?
    let type: String
    let filename: String
    let mimeType: String
    let fileSize: Int
    let tags: [String]
    let caption: String?
    let latitude: Double?
    let longitude: Double?
}

struct MediaAssetResponse: Decodable {
    let mediaAsset: MediaAsset
}

struct MediaUploadResponse: Decodable {
    let url: String
    let mediaAssetId: String?
}

struct TemplatesResponse: Decodable {
    let templates: [InspectionTemplate]
}

// MARK: - Sync Types

struct SyncPushRequest: Encodable {
    let deviceId: String
    let items: [SyncItem]
    let lastSyncTimestamp: String?
}

struct SyncItem: Encodable {
    let id: String
    let deviceId: String
    let entityType: String
    let entityId: String
    let operation: String
    let payload: [String: String]
    let clientTimestamp: String
    let idempotencyKey: String?
    
    init(
        id: String,
        deviceId: String,
        entityType: String,
        entityId: String,
        operation: String,
        payload: [String: String],
        clientTimestamp: String,
        idempotencyKey: String? = nil
    ) {
        self.id = id
        self.deviceId = deviceId
        self.entityType = entityType
        self.entityId = entityId
        self.operation = operation
        self.payload = payload
        self.clientTimestamp = clientTimestamp
        self.idempotencyKey = idempotencyKey
    }
}

struct SyncPushResponse: Decodable {
    let success: Bool
    let processedCount: Int
    let failedItems: [FailedSyncItem]
    let serverTimestamp: String
    let conflicts: [SyncConflictResponse]?
}

struct FailedSyncItem: Decodable {
    let id: String
    let error: String
}

struct SyncConflictResponse: Decodable {
    let itemId: String
    let field: String
    let localValue: String
    let serverValue: String
}

struct SyncPullRequest: Encodable {
    let deviceId: String
    let lastSyncTimestamp: String?
    let entityTypes: [String]?
}

struct SyncPullResponse: Decodable, Sendable {
    let success: Bool
    let items: [SyncPullItem]
    let serverTimestamp: String
    let hasMore: Bool
}

struct SyncPullItem: Decodable, Sendable {
    let entityType: String
    let entityId: String
    let operation: String
    let payload: [String: AnyCodable]
    let serverTimestamp: String
}

// Helper for decoding arbitrary JSON
struct AnyCodable: Codable, Sendable {
    let value: SendableValue
    
    enum SendableValue: Sendable {
        case string(String)
        case int(Int)
        case double(Double)
        case bool(Bool)
        case null
    }
    
    init(_ value: Any) {
        if let string = value as? String {
            self.value = .string(string)
        } else if let int = value as? Int {
            self.value = .int(int)
        } else if let double = value as? Double {
            self.value = .double(double)
        } else if let bool = value as? Bool {
            self.value = .bool(bool)
        } else {
            self.value = .null
        }
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let string = try? container.decode(String.self) {
            value = .string(string)
        } else if let int = try? container.decode(Int.self) {
            value = .int(int)
        } else if let double = try? container.decode(Double.self) {
            value = .double(double)
        } else if let bool = try? container.decode(Bool.self) {
            value = .bool(bool)
        } else {
            value = .null
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch value {
        case .string(let s): try container.encode(s)
        case .int(let i): try container.encode(i)
        case .double(let d): try container.encode(d)
        case .bool(let b): try container.encode(b)
        case .null: try container.encodeNil()
        }
    }
}
