import Foundation

// MARK: - Type Alias for backward compatibility
typealias AIDecision = AIDecisionResponse

// MARK: - AI Recommended Action

enum AIRecommendedAction: String, Codable {
    case approve = "approve"
    case reject = "reject"
    case needMoreInfo = "need_more_info"
    case refer = "refer"
    
    var displayName: String {
        switch self {
        case .approve: return "Approve"
        case .reject: return "Reject"
        case .needMoreInfo: return "Need More Info"
        case .refer: return "Refer to Specialist"
        }
    }
    
    var iconName: String {
        switch self {
        case .approve: return "checkmark.circle.fill"
        case .reject: return "xmark.circle.fill"
        case .needMoreInfo: return "questionmark.circle.fill"
        case .refer: return "arrow.right.circle.fill"
        }
    }
    
    var color: String {
        switch self {
        case .approve: return "green"
        case .reject: return "red"
        case .needMoreInfo: return "orange"
        case .refer: return "blue"
        }
    }
}

// MARK: - AI Decision Response

struct AIDecisionResponse: Codable, Equatable {
    let recommendedAction: AIRecommendedAction
    let confidence: Double
    let reasonCodes: [String]
    let keyFindings: [String]
    let missingInfo: [String]
    let nextSteps: [String]
    let policyNotes: [String]
    let auditSummary: String
    
    enum CodingKeys: String, CodingKey {
        case recommendedAction = "recommended_action"
        case confidence
        case reasonCodes = "reason_codes"
        case keyFindings = "key_findings"
        case missingInfo = "missing_info"
        case nextSteps = "next_steps"
        case policyNotes = "policy_notes"
        case auditSummary = "audit_summary"
    }
    
    var confidencePercentage: String {
        String(format: "%.0f%%", confidence * 100)
    }
    
    var confidenceLevel: String {
        switch confidence {
        case 0.8...1.0: return "High"
        case 0.6..<0.8: return "Medium"
        case 0.4..<0.6: return "Low"
        default: return "Very Low"
        }
    }
}

// MARK: - AI Suggestion Request

struct AISuggestionRequest: Codable {
    let claimId: String
}

// MARK: - AI Suggestion Response Wrapper

struct AISuggestionResponse: Codable {
    let decision: AIDecisionResponse
    let metadata: AIMetadata
}

struct AIMetadata: Codable {
    let durationMs: Int
    let model: String
}
