import Foundation
import GRDB

// MARK: - Risk Engine

/// Deterministic risk scoring engine (0-100)
/// Risk Bands:
/// - 0-30: Low
/// - 31-60: Moderate
/// - 61-80: Elevated
/// - 81-100: Critical

enum RiskBand: String, CaseIterable {
    case low = "low"
    case moderate = "moderate"
    case elevated = "elevated"
    case critical = "critical"
    
    var displayName: String {
        rawValue.capitalized
    }
    
    var range: ClosedRange<Int> {
        switch self {
        case .low: return 0...30
        case .moderate: return 31...60
        case .elevated: return 61...80
        case .critical: return 81...100
        }
    }
    
    var color: Color {
        switch self {
        case .low: return DeevoColors.success
        case .moderate: return DeevoColors.warning
        case .elevated: return Color.orange
        case .critical: return DeevoColors.error
        }
    }
    
    static func from(score: Int) -> RiskBand {
        switch score {
        case 0...30: return .low
        case 31...60: return .moderate
        case 61...80: return .elevated
        default: return .critical
        }
    }
}

struct RiskFactor: Identifiable {
    let id = UUID()
    let name: String
    let description: String
    let points: Int
    let maxPoints: Int
    let category: RiskCategory
}

enum RiskCategory: String, CaseIterable {
    case claimAmount = "Claim Amount"
    case documentation = "Documentation"
    case timing = "Timing"
    case history = "History"
    case aiConfidence = "AI Confidence"
}

struct RiskAssessment {
    let totalScore: Int
    let band: RiskBand
    let factors: [RiskFactor]
    let assessedAt: Date
    
    var normalizedScore: Double {
        Double(totalScore) / 100.0
    }
}

import SwiftUI

class RiskEngineService {
    static let shared = RiskEngineService()
    
    private init() {}
    
    // MARK: - Risk Calculation
    
    /// Calculate deterministic risk score for a claim
    /// Returns score 0-100
    func calculateRiskScore(for claim: Claim, priorClaimsCount: Int = 0, missingDocsCount: Int = 0) -> RiskAssessment {
        var factors: [RiskFactor] = []
        var totalScore = 0
        
        // 1. Claim Amount Band (0-25 points)
        let amountScore = calculateAmountScore(claim.claimAmount)
        factors.append(RiskFactor(
            name: "Claim Amount",
            description: amountDescription(claim.claimAmount),
            points: amountScore,
            maxPoints: 25,
            category: .claimAmount
        ))
        totalScore += amountScore
        
        // 2. Missing Documents (0-20 points)
        let docsScore = calculateMissingDocsScore(missingDocsCount)
        factors.append(RiskFactor(
            name: "Missing Documents",
            description: "\(missingDocsCount) required document(s) missing",
            points: docsScore,
            maxPoints: 20,
            category: .documentation
        ))
        totalScore += docsScore
        
        // 3. Late Reporting (0-20 points)
        let incidentDate = claim.incidentDate ?? claim.createdAt
        let reportingScore = calculateLateReportingScore(incidentDate, reportedDate: claim.createdAt)
        let daysSinceIncident = Calendar.current.dateComponents([.day], from: incidentDate, to: claim.createdAt).day ?? 0
        factors.append(RiskFactor(
            name: "Reporting Delay",
            description: "Reported \(daysSinceIncident) day(s) after incident",
            points: reportingScore,
            maxPoints: 20,
            category: .timing
        ))
        totalScore += reportingScore
        
        // 4. Prior Claims (0-20 points)
        let priorScore = calculatePriorClaimsScore(priorClaimsCount)
        factors.append(RiskFactor(
            name: "Prior Claims",
            description: "\(priorClaimsCount) prior claim(s) in last 12 months",
            points: priorScore,
            maxPoints: 20,
            category: .history
        ))
        totalScore += priorScore
        
        // 5. Low AI Confidence Penalty (0-15 points)
        let aiScore = calculateAIConfidencePenalty(claim.aiConfidence)
        factors.append(RiskFactor(
            name: "AI Confidence",
            description: aiConfidenceDescription(claim.aiConfidence),
            points: aiScore,
            maxPoints: 15,
            category: .aiConfidence
        ))
        totalScore += aiScore
        
        // Clamp to 0-100
        totalScore = min(100, max(0, totalScore))
        
        return RiskAssessment(
            totalScore: totalScore,
            band: RiskBand.from(score: totalScore),
            factors: factors,
            assessedAt: Date()
        )
    }
    
    // MARK: - Individual Score Calculations
    
    /// Claim amount scoring:
    /// - Under $5,000: 0 points
    /// - $5,000 - $25,000: 5 points
    /// - $25,000 - $50,000: 10 points
    /// - $50,000 - $100,000: 15 points
    /// - $100,000 - $250,000: 20 points
    /// - Over $250,000: 25 points
    private func calculateAmountScore(_ amount: Double) -> Int {
        switch amount {
        case ..<5000: return 0
        case 5000..<25000: return 5
        case 25000..<50000: return 10
        case 50000..<100000: return 15
        case 100000..<250000: return 20
        default: return 25
        }
    }
    
    private func amountDescription(_ amount: Double) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.maximumFractionDigits = 0
        let formatted = formatter.string(from: NSNumber(value: amount)) ?? "$\(Int(amount))"
        
        switch amount {
        case ..<5000: return "\(formatted) - Low value claim"
        case 5000..<25000: return "\(formatted) - Standard claim"
        case 25000..<50000: return "\(formatted) - Moderate value claim"
        case 50000..<100000: return "\(formatted) - High value claim"
        case 100000..<250000: return "\(formatted) - Very high value claim"
        default: return "\(formatted) - Exceptional value claim"
        }
    }
    
    /// Missing documents scoring:
    /// - 0 missing: 0 points
    /// - 1 missing: 5 points
    /// - 2 missing: 10 points
    /// - 3 missing: 15 points
    /// - 4+ missing: 20 points
    private func calculateMissingDocsScore(_ count: Int) -> Int {
        switch count {
        case 0: return 0
        case 1: return 5
        case 2: return 10
        case 3: return 15
        default: return 20
        }
    }
    
    /// Late reporting scoring:
    /// - Within 3 days: 0 points
    /// - 4-7 days: 5 points
    /// - 8-14 days: 10 points
    /// - 15-30 days: 15 points
    /// - Over 30 days: 20 points
    private func calculateLateReportingScore(_ incidentDate: Date, reportedDate: Date) -> Int {
        let days = Calendar.current.dateComponents([.day], from: incidentDate, to: reportedDate).day ?? 0
        
        switch days {
        case ..<4: return 0
        case 4...7: return 5
        case 8...14: return 10
        case 15...30: return 15
        default: return 20
        }
    }
    
    /// Prior claims scoring:
    /// - 0 prior: 0 points
    /// - 1 prior: 5 points
    /// - 2 prior: 10 points
    /// - 3 prior: 15 points
    /// - 4+ prior: 20 points
    private func calculatePriorClaimsScore(_ count: Int) -> Int {
        switch count {
        case 0: return 0
        case 1: return 5
        case 2: return 10
        case 3: return 15
        default: return 20
        }
    }
    
    /// AI confidence penalty:
    /// - 80%+ confidence: 0 points
    /// - 60-79% confidence: 5 points
    /// - 40-59% confidence: 10 points
    /// - Under 40% confidence: 15 points
    private func calculateAIConfidencePenalty(_ confidence: Double?) -> Int {
        guard let confidence = confidence else { return 10 } // Default penalty if no AI analysis
        
        switch confidence {
        case 0.8...: return 0
        case 0.6..<0.8: return 5
        case 0.4..<0.6: return 10
        default: return 15
        }
    }
    
    private func aiConfidenceDescription(_ confidence: Double?) -> String {
        guard let confidence = confidence else {
            return "No AI analysis available"
        }
        
        let percentage = Int(confidence * 100)
        switch confidence {
        case 0.8...: return "\(percentage)% - High confidence"
        case 0.6..<0.8: return "\(percentage)% - Moderate confidence"
        case 0.4..<0.6: return "\(percentage)% - Low confidence"
        default: return "\(percentage)% - Very low confidence"
        }
    }
    
    // MARK: - Batch Processing
    
    /// Calculate and update risk scores for all claims
    func recalculateAllRiskScores() async throws {
        let claims = try await DatabaseManager.shared.database.read { db in
            try Claim.fetchAll(db)
        }
        
        for claim in claims {
            let assessment = calculateRiskScore(for: claim)
            
            try await DatabaseManager.shared.database.write { db in
                var updatedClaim = claim
                updatedClaim.riskScore = assessment.totalScore
                try updatedClaim.update(db)
            }
        }
    }
}
