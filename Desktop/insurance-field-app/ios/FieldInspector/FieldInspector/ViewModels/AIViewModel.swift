import Foundation
import Combine

/// ViewModel for managing AI decision suggestions
@MainActor
class AIViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var decision: AIDecision?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var requestDuration: TimeInterval?
    
    // MARK: - Computed Properties
    
    var hasDecision: Bool {
        decision != nil
    }
    
    var confidenceLevel: String {
        guard let confidence = decision?.confidence else { return "Unknown" }
        
        if confidence >= 0.9 {
            return "Very High"
        } else if confidence >= 0.75 {
            return "High"
        } else if confidence >= 0.5 {
            return "Medium"
        } else {
            return "Low"
        }
    }
    
    var actionColor: String {
        guard let action = decision?.recommendedAction else { return "gray" }
        
        switch action {
        case .approve:
            return "green"
        case .reject:
            return "red"
        case .needMoreInfo:
            return "orange"
        case .refer:
            return "blue"
        }
    }
    
    // MARK: - Properties
    
    private let api: APIService
    private lazy var audit: AuditViewModel = AuditViewModel()
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(
        api: APIService = .shared
    ) {
        self.api = api
    }
    
    // MARK: - Public Methods
    
    /// Request AI decision suggestion for a claim
    func requestSuggestion(claimId: String, actorId: String) async {
        isLoading = true
        errorMessage = nil
        decision = nil
        
        let startTime = Date()
        
        do {
            // Create audit event for request
            try await audit.createEvent(
                actorId: actorId,
                claimId: claimId,
                eventType: AuditEventType.aiSuggestionRequested.rawValue,
                eventPayload: [
                    "claimId": claimId,
                    "timestamp": ISO8601DateFormatter().string(from: Date())
                ]
            )
            
            // Request AI suggestion
            let response = try await api.getAISuggestion(claimId: claimId)
            
            decision = response.decision
            requestDuration = Date().timeIntervalSince(startTime)
            
            // Create audit event for response
            try await audit.createEvent(
                actorId: actorId,
                claimId: claimId,
                eventType: AuditEventType.aiSuggestionReceived.rawValue,
                eventPayload: [
                    "claimId": claimId,
                    "recommendedAction": response.decision.recommendedAction.rawValue,
                    "confidence": String(response.decision.confidence),
                    "durationMs": String(Int(requestDuration! * 1000)),
                    "timestamp": ISO8601DateFormatter().string(from: Date())
                ]
            )
            
            isLoading = false
        } catch {
            errorMessage = error.localizedDescription
            requestDuration = Date().timeIntervalSince(startTime)
            isLoading = false
            
            // Create audit event for error
            try? await audit.createEvent(
                actorId: actorId,
                claimId: claimId,
                eventType: "ai.suggestion_failed",
                eventPayload: [
                    "claimId": claimId,
                    "error": error.localizedDescription,
                    "timestamp": ISO8601DateFormatter().string(from: Date())
                ]
            )
        }
    }
    
    /// Clear current decision
    func clearDecision() {
        decision = nil
        errorMessage = nil
        requestDuration = nil
    }
    
    /// Validate AI decision against schema
    func validateDecision(_ decision: AIDecision) -> (valid: Bool, errors: [String]) {
        var errors: [String] = []
        
        // Validate recommended_action - enum is always valid
        // No validation needed since AIRecommendedAction is an enum
        
        // Validate confidence
        if decision.confidence < 0.0 || decision.confidence > 1.0 {
            errors.append("Confidence must be between 0.0 and 1.0")
        }
        
        // Validate required arrays
        if decision.reasonCodes.isEmpty {
            errors.append("reason_codes cannot be empty")
        }
        
        if decision.keyFindings.isEmpty {
            errors.append("key_findings cannot be empty")
        }
        
        if decision.nextSteps.isEmpty {
            errors.append("next_steps cannot be empty")
        }
        
        // Validate audit_summary
        if decision.auditSummary.isEmpty {
            errors.append("audit_summary cannot be empty")
        }
        
        return (errors.isEmpty, errors)
    }
    
    /// Format decision for display
    func formatDecision() -> String {
        guard let decision = decision else { return "No decision available" }
        
        var output = ""
        output += "Recommended Action: \(decision.recommendedAction.rawValue.uppercased())\n"
        output += "Confidence: \(String(format: "%.1f%%", decision.confidence * 100))\n\n"
        
        output += "Reason Codes:\n"
        for code in decision.reasonCodes {
            output += "  • \(code)\n"
        }
        output += "\n"
        
        output += "Key Findings:\n"
        for finding in decision.keyFindings {
            output += "  • \(finding)\n"
        }
        output += "\n"
        
        if !decision.missingInfo.isEmpty {
            output += "Missing Information:\n"
            for info in decision.missingInfo {
                output += "  • \(info)\n"
            }
            output += "\n"
        }
        
        output += "Next Steps:\n"
        for step in decision.nextSteps {
            output += "  • \(step)\n"
        }
        output += "\n"
        
        if !decision.policyNotes.isEmpty {
            output += "Policy Notes:\n"
            for note in decision.policyNotes {
                output += "  • \(note)\n"
            }
            output += "\n"
        }
        
        output += "Audit Summary: \(decision.auditSummary)"
        
        return output
    }
    
    /// Export decision as JSON
    func exportDecisionJSON() throws -> Data {
        guard let decision = decision else {
            throw NSError(domain: "AIViewModel", code: 1, userInfo: [
                NSLocalizedDescriptionKey: "No decision to export"
            ])
        }
        
        let encoder = JSONEncoder()
        encoder.outputFormatting = .prettyPrinted
        encoder.dateEncodingStrategy = .iso8601
        
        return try encoder.encode(decision)
    }
}
