import Foundation
import Network

/// Serial processor for queued operations with retry/backoff
@MainActor
final class OperationProcessor: ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = OperationProcessor()
    
    // MARK: - Published Properties
    
    @Published private(set) var isProcessing = false
    @Published private(set) var currentOperation: QueuedOperation?
    @Published private(set) var lastError: String?
    
    // MARK: - Properties
    
    private let operationRepository: OperationRepository
    private let api: APIService
    private let backoffConfig: OperationBackoffConfig
    private var processingTask: Task<Void, Never>?
    private let monitor: NWPathMonitor
    private let monitorQueue = DispatchQueue(label: "com.fieldinspector.operationprocessor.network")
    private var isOnline = true
    
    // MARK: - Initialization
    
    private init() {
        self.operationRepository = OperationRepository.shared
        self.api = APIService.shared
        self.backoffConfig = OperationBackoffConfig.default
        self.monitor = NWPathMonitor()
        
        setupNetworkMonitoring()
    }
    
    // MARK: - Network Monitoring
    
    private func setupNetworkMonitoring() {
        monitor.pathUpdateHandler = { [weak self] path in
            Task { @MainActor in
                guard let self = self else { return }
                let wasOffline = !self.isOnline
                self.isOnline = path.status == .satisfied
                
                // Auto-process when coming online
                if path.status == .satisfied && wasOffline {
                    await self.processQueue()
                }
            }
        }
        monitor.start(queue: monitorQueue)
    }
    
    // MARK: - Queue Processing
    
    /// Start processing the queue
    func processQueue() async {
        guard isOnline else {
            AppLogger.sync.info("Offline - skipping queue processing")
            return
        }
        
        guard !isProcessing else {
            AppLogger.sync.info("Already processing queue")
            return
        }
        
        isProcessing = true
        lastError = nil
        
        do {
            // Process pending operations
            var pendingOps = try await operationRepository.fetchPending()
            
            while !pendingOps.isEmpty && isOnline {
                for operation in pendingOps {
                    currentOperation = operation
                    await processOperation(operation)
                    
                    // Check if we should continue
                    guard isOnline else { break }
                }
                
                // Fetch any new pending operations
                pendingOps = try await operationRepository.fetchPending()
            }
            
            // Process operations ready for retry
            let retryOps = try await operationRepository.fetchReadyForRetry()
            for operation in retryOps {
                guard isOnline else { break }
                currentOperation = operation
                await processOperation(operation)
            }
            
        } catch {
            AppLogger.error("Error processing queue", error: error, category: AppLogger.sync)
            lastError = error.localizedDescription
        }
        
        currentOperation = nil
        isProcessing = false
    }
    
    /// Process a single operation
    private func processOperation(_ operation: QueuedOperation) async {
        AppLogger.sync.info("Processing operation: \(operation.id, privacy: .public) type: \(operation.operationType.rawValue, privacy: .public)")
        
        do {
            // Mark as processing
            try await operationRepository.markProcessing(id: operation.id)
            
            // Execute the operation based on type
            switch operation.operationType {
            case .submitForm:
                try await executeSubmitForm(operation)
            case .uploadEvidence:
                try await executeUploadEvidence(operation)
            case .updateClaim:
                try await executeUpdateClaim(operation)
            case .createInspection:
                try await executeCreateInspection(operation)
            case .updateInspection:
                try await executeUpdateInspection(operation)
            case .deleteMedia:
                try await executeDeleteMedia(operation)
            }
            
            // Mark as completed
            try await operationRepository.markCompleted(id: operation.id)
            AppLogger.sync.info("✅ Operation completed: \(operation.id, privacy: .public)")
            
        } catch {
            await handleOperationError(operation, error: error)
        }
    }
    
    /// Handle operation error with exponential backoff
    private func handleOperationError(_ operation: QueuedOperation, error: Error) async {
        let errorMessage = error.localizedDescription
        AppLogger.error("Operation failed: \(operation.id)", error: error, category: AppLogger.sync)
        
        // Calculate next retry delay using exponential backoff
        let nextRetryDelay = backoffConfig.delay(forAttempt: operation.attempts)
        
        do {
            if operation.attempts + 1 >= operation.maxAttempts {
                // Max attempts reached - mark as permanently failed
                try await operationRepository.markFailed(
                    id: operation.id,
                    error: "Max attempts (\(operation.maxAttempts)) reached. Last error: \(errorMessage)",
                    nextRetryDelay: 0
                )
                AppLogger.sync.warning("❌ Operation permanently failed after \(operation.maxAttempts) attempts: \(operation.id, privacy: .public)")
            } else {
                // Schedule retry
                try await operationRepository.markFailed(
                    id: operation.id,
                    error: errorMessage,
                    nextRetryDelay: nextRetryDelay
                )
                AppLogger.sync.info("⏳ Operation scheduled for retry in \(Int(nextRetryDelay))s: \(operation.id, privacy: .public)")
            }
        } catch {
            AppLogger.error("Failed to update operation status", error: error, category: AppLogger.sync)
        }
        
        lastError = errorMessage
    }
    
    // MARK: - Operation Executors
    
    private func executeSubmitForm(_ operation: QueuedOperation) async throws {
        // Decode payload and submit form
        guard let payloadData = operation.payloadJson.data(using: .utf8) else {
            throw OperationError.invalidPayload
        }
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let payload = try decoder.decode(FormSubmissionPayload.self, from: payloadData)
        
        // Submit to API
        try await api.submitForm(payload: payload)
        
        // Update form draft status
        try await FormRepository.shared.markSynced(id: payload.draftId)
    }
    
    private func executeUploadEvidence(_ operation: QueuedOperation) async throws {
        guard let payloadData = operation.payloadJson.data(using: .utf8) else {
            throw OperationError.invalidPayload
        }
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let payload = try decoder.decode(EvidenceUploadPayload.self, from: payloadData)
        
        // Upload to API
        let remoteUrl = try await api.uploadEvidence(payload: payload)
        
        // Update media asset with remote URL
        try await EvidenceRepository.shared.markSynced(id: payload.mediaAssetId, remoteUrl: remoteUrl)
    }
    
    private func executeUpdateClaim(_ operation: QueuedOperation) async throws {
        guard let payloadData = operation.payloadJson.data(using: .utf8) else {
            throw OperationError.invalidPayload
        }
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let payload = try decoder.decode(ClaimUpdatePayload.self, from: payloadData)
        
        // Update via API
        try await api.updateClaim(payload: payload)
        
        // Mark claim as synced
        try await ClaimRepository.shared.markSynced(id: payload.claimId)
    }
    
    private func executeCreateInspection(_ operation: QueuedOperation) async throws {
        guard let payloadData = operation.payloadJson.data(using: .utf8) else {
            throw OperationError.invalidPayload
        }
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let payload = try decoder.decode(InspectionCreatePayload.self, from: payloadData)
        
        // Create via API
        try await api.createInspection(payload: payload)
    }
    
    private func executeUpdateInspection(_ operation: QueuedOperation) async throws {
        guard let payloadData = operation.payloadJson.data(using: .utf8) else {
            throw OperationError.invalidPayload
        }
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let payload = try decoder.decode(InspectionUpdatePayload.self, from: payloadData)
        
        // Update via API
        try await api.updateInspection(payload: payload)
    }
    
    private func executeDeleteMedia(_ operation: QueuedOperation) async throws {
        guard let payloadData = operation.payloadJson.data(using: .utf8) else {
            throw OperationError.invalidPayload
        }
        
        let decoder = JSONDecoder()
        let payload = try decoder.decode(MediaDeletePayload.self, from: payloadData)
        
        // Delete via API
        try await api.deleteMedia(mediaAssetId: payload.mediaAssetId)
    }
    
    // MARK: - Manual Retry
    
    /// Retry a specific failed operation
    func retryOperation(id: String) async {
        do {
            try await operationRepository.resetForRetry(id: id)
            await processQueue()
        } catch {
            AppLogger.error("Failed to retry operation", error: error, category: AppLogger.sync)
            lastError = error.localizedDescription
        }
    }
    
    /// Retry all failed operations
    func retryAllFailed() async {
        do {
            let failedOps = try await operationRepository.fetchFailed()
            for op in failedOps {
                try await operationRepository.resetForRetry(id: op.id)
            }
            await processQueue()
        } catch {
            AppLogger.error("Failed to retry all operations", error: error, category: AppLogger.sync)
            lastError = error.localizedDescription
        }
    }
    
    // MARK: - Cleanup
    
    func cleanup() async {
        do {
            try await operationRepository.cleanupCompleted(olderThanDays: 7)
        } catch {
            AppLogger.error("Failed to cleanup operations", error: error, category: AppLogger.sync)
        }
    }
}

// MARK: - Operation Error

enum OperationError: LocalizedError {
    case invalidPayload
    case networkUnavailable
    case serverError(String)
    
    var errorDescription: String? {
        switch self {
        case .invalidPayload:
            return "Invalid operation payload"
        case .networkUnavailable:
            return "Network unavailable"
        case .serverError(let message):
            return "Server error: \(message)"
        }
    }
}

// MARK: - Operation Payloads

struct FormSubmissionPayload: Codable {
    let draftId: String
    let templateId: String
    let claimId: String?
    let inspectionId: String?
    let dataJson: String
}

struct EvidenceUploadPayload: Codable {
    let mediaAssetId: String
    let claimId: String
    let localPath: String
    let mimeType: String
    let filename: String
}

struct ClaimUpdatePayload: Codable {
    let claimId: String
    let updates: [String: String]
}

struct InspectionCreatePayload: Codable {
    let inspectionId: String
    let claimId: String
    let templateId: String
}

struct InspectionUpdatePayload: Codable {
    let inspectionId: String
    let fields: [String: String]
}

struct MediaDeletePayload: Codable {
    let mediaAssetId: String
}

// MARK: - Backoff Configuration

/// Configuration for exponential backoff retry strategy
struct OperationBackoffConfig {
    let initialDelay: TimeInterval
    let maxDelay: TimeInterval
    let multiplier: Double
    
    static let `default` = OperationBackoffConfig(
        initialDelay: 1.0,      // 1 second
        maxDelay: 300.0,        // 5 minutes
        multiplier: 2.0         // Double each time
    )
    
    /// Calculate delay for a given attempt number (0-indexed)
    func delay(forAttempt attempt: Int) -> TimeInterval {
        let delay = initialDelay * pow(multiplier, Double(attempt))
        return min(delay, maxDelay)
    }
}
