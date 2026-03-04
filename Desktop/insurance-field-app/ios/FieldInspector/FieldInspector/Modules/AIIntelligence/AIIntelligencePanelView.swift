import SwiftUI
import GRDB

// MARK: - AI Intelligence Models

enum AIRecommendation: String, Codable {
    case approve = "approve"
    case deny = "deny"
    case review = "review"
    
    var displayName: String {
        switch self {
        case .approve: return "Approve Claim"
        case .deny: return "Deny Claim"
        case .review: return "Manual Review Required"
        }
    }
    
    var icon: String {
        switch self {
        case .approve: return "checkmark.circle.fill"
        case .deny: return "xmark.circle.fill"
        case .review: return "eye.circle.fill"
        }
    }
    
    var color: Color {
        switch self {
        case .approve: return DeevoColors.success
        case .deny: return DeevoColors.error
        case .review: return DeevoColors.warning
        }
    }
}

struct AIExplanation: Identifiable, Equatable {
    let id: UUID
    let factor: String
    let impact: String
    let weight: Double
    let isPositive: Bool
    
    init(factor: String, impact: String, weight: Double, isPositive: Bool) {
        self.id = UUID()
        self.factor = factor
        self.impact = impact
        self.weight = weight
        self.isPositive = isPositive
    }
}

struct AIOverrideRecord: Identifiable, Codable {
    let id: String
    let claimId: String
    let originalDecision: String
    let overrideDecision: String
    let justification: String
    let overriddenBy: String
    let overriddenAt: Date
}

// MARK: - AI Intelligence Panel View

struct AIIntelligencePanelView: View {
    let claim: Claim
    @StateObject private var viewModel: AIIntelligenceViewModel
    @State private var showOverrideSheet = false
    
    init(claim: Claim) {
        self.claim = claim
        self._viewModel = StateObject(wrappedValue: AIIntelligenceViewModel(claim: claim))
    }
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // AI Recommendation Header
                recommendationHeader
                
                // Confidence Gauge
                confidenceSection
                
                // Explainability Section
                explainabilitySection
                
                // Override Section
                overrideSection
                
                // Audit Log
                auditLogSection
            }
            .padding()
        }
        .background(DeevoColors.backgroundDark.ignoresSafeArea())
        .navigationTitle("AI Intelligence")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showOverrideSheet) {
            AIOverrideSheet(claim: claim, viewModel: viewModel)
        }
    }
    
    // MARK: - Recommendation Header
    
    private var recommendationHeader: some View {
        SectionCard {
            VStack(spacing: 16) {
                HStack {
                    Text("AI Recommendation")
                        .font(DeevoTypography.headlineMedium)
                        .foregroundColor(DeevoColors.textPrimary)
                    Spacer()
                    PillBadge(
                        viewModel.recommendation.displayName,
                        style: viewModel.recommendation == .approve ? .success : 
                               viewModel.recommendation == .deny ? .error : .warning
                    )
                }
                
                HStack(spacing: 16) {
                    Image(systemName: viewModel.recommendation.icon)
                        .font(.system(size: 48))
                        .foregroundColor(viewModel.recommendation.color)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(viewModel.recommendation.displayName)
                            .font(DeevoTypography.displayMedium)
                            .foregroundColor(DeevoColors.textPrimary)
                        
                        Text("Based on \(viewModel.explanations.count) factors")
                            .font(DeevoTypography.bodyMedium)
                            .foregroundColor(DeevoColors.textSecondary)
                    }
                    
                    Spacer()
                }
            }
            .padding()
        }
    }
    
    // MARK: - Confidence Section
    
    private var confidenceSection: some View {
        SectionCard {
            VStack(spacing: 16) {
                HStack {
                    Text("Confidence Score")
                        .font(DeevoTypography.headlineMedium)
                        .foregroundColor(DeevoColors.textPrimary)
                    Spacer()
                    Text(String(format: "%.0f%%", viewModel.confidence * 100))
                        .font(DeevoTypography.displayMedium)
                        .foregroundColor(confidenceColor)
                }
                
                ConfidenceGauge(value: viewModel.confidence)
                
                HStack {
                    Text("Low")
                        .font(DeevoTypography.labelSmall)
                        .foregroundColor(DeevoColors.textTertiary)
                    Spacer()
                    Text("High")
                        .font(DeevoTypography.labelSmall)
                        .foregroundColor(DeevoColors.textTertiary)
                }
            }
            .padding()
        }
    }
    
    private var confidenceColor: Color {
        if viewModel.confidence >= 0.8 {
            return DeevoColors.success
        } else if viewModel.confidence >= 0.6 {
            return DeevoColors.warning
        } else {
            return DeevoColors.error
        }
    }
    
    // MARK: - Explainability Section
    
    private var explainabilitySection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Decision Factors")
                .font(DeevoTypography.headlineMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            SectionCard {
                VStack(spacing: 0) {
                    ForEach(viewModel.explanations) { explanation in
                        ExplanationRow(explanation: explanation)
                        if explanation.id != viewModel.explanations.last?.id {
                            Divider()
                                .background(DeevoColors.divider)
                        }
                    }
                }
                .padding(.vertical, 8)
            }
        }
    }
    
    // MARK: - Override Section
    
    private var overrideSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Manual Override")
                .font(DeevoTypography.headlineMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            SectionCard {
                VStack(spacing: 16) {
                    if let override = viewModel.currentOverride {
                        // Show current override
                        HStack {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundColor(DeevoColors.warning)
                            Text("Decision Overridden")
                                .font(DeevoTypography.labelMedium)
                                .foregroundColor(DeevoColors.warning)
                            Spacer()
                        }
                        
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Text("Original:")
                                    .font(DeevoTypography.labelSmall)
                                    .foregroundColor(DeevoColors.textTertiary)
                                Text(override.originalDecision.capitalized)
                                    .font(DeevoTypography.labelMedium)
                                    .foregroundColor(DeevoColors.textSecondary)
                            }
                            
                            HStack {
                                Text("Override:")
                                    .font(DeevoTypography.labelSmall)
                                    .foregroundColor(DeevoColors.textTertiary)
                                Text(override.overrideDecision.capitalized)
                                    .font(DeevoTypography.labelMedium)
                                    .foregroundColor(DeevoColors.textPrimary)
                            }
                            
                            Text("Justification: \(override.justification)")
                                .font(DeevoTypography.bodySmall)
                                .foregroundColor(DeevoColors.textSecondary)
                            
                            Text("By \(override.overriddenBy) on \(override.overriddenAt.formatted())")
                                .font(DeevoTypography.labelSmall)
                                .foregroundColor(DeevoColors.textTertiary)
                        }
                    } else {
                        Text("Override the AI decision if you disagree with the recommendation. A justification is required for audit purposes.")
                            .font(DeevoTypography.bodySmall)
                            .foregroundColor(DeevoColors.textSecondary)
                    }
                    
                    PrimaryButton("Override Decision") {
                        showOverrideSheet = true
                    }
                }
                .padding()
            }
        }
    }
    
    // MARK: - Audit Log Section
    
    private var auditLogSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("AI Audit Trail")
                    .font(DeevoTypography.headlineMedium)
                    .foregroundColor(DeevoColors.textPrimary)
                Spacer()
                Text("\(viewModel.auditEntries.count) entries")
                    .font(DeevoTypography.labelSmall)
                    .foregroundColor(DeevoColors.textTertiary)
            }
            
            SectionCard {
                if viewModel.auditEntries.isEmpty {
                    EmptyStateView(
                        icon: "doc.text.magnifyingglass",
                        title: "No Audit Entries",
                        message: "AI decision history will appear here"
                    )
                    .padding()
                } else {
                    LazyVStack(spacing: 0) {
                        ForEach(viewModel.auditEntries) { entry in
                            AuditEntryRow(entry: entry)
                            if entry.id != viewModel.auditEntries.last?.id {
                                Divider()
                                    .background(DeevoColors.divider)
                            }
                        }
                    }
                    .padding(.vertical, 8)
                }
            }
        }
    }
}

// MARK: - Supporting Views

struct ConfidenceGauge: View {
    let value: Double
    
    var body: some View {
        GeometryReader { geometry in
            ZStack(alignment: .leading) {
                // Background
                RoundedRectangle(cornerRadius: 8)
                    .fill(DeevoColors.surfaceElevated)
                    .frame(height: 24)
                
                // Gradient fill
                RoundedRectangle(cornerRadius: 8)
                    .fill(
                        LinearGradient(
                            colors: [DeevoColors.error, DeevoColors.warning, DeevoColors.success],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .frame(width: geometry.size.width * CGFloat(value), height: 24)
                
                // Indicator
                Circle()
                    .fill(Color.white)
                    .frame(width: 20, height: 20)
                    .shadow(radius: 2)
                    .offset(x: geometry.size.width * CGFloat(value) - 10)
            }
        }
        .frame(height: 24)
    }
}

struct ExplanationRow: View {
    let explanation: AIExplanation
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: explanation.isPositive ? "arrow.up.circle.fill" : "arrow.down.circle.fill")
                .foregroundColor(explanation.isPositive ? DeevoColors.success : DeevoColors.error)
                .font(.system(size: 24))
            
            VStack(alignment: .leading, spacing: 2) {
                Text(explanation.factor)
                    .font(DeevoTypography.labelMedium)
                    .foregroundColor(DeevoColors.textPrimary)
                Text(explanation.impact)
                    .font(DeevoTypography.bodySmall)
                    .foregroundColor(DeevoColors.textSecondary)
            }
            
            Spacer()
            
            Text(String(format: "%.0f%%", explanation.weight * 100))
                .font(DeevoTypography.labelMedium)
                .foregroundColor(explanation.isPositive ? DeevoColors.success : DeevoColors.error)
        }
        .padding(.horizontal)
        .padding(.vertical, 12)
    }
}

struct AuditEntryRow: View {
    let entry: AIAuditEntry
    
    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(DeevoColors.accent.opacity(0.2))
                .frame(width: 36, height: 36)
                .overlay(
                    Image(systemName: entry.icon)
                        .foregroundColor(DeevoColors.accent)
                        .font(.system(size: 14))
                )
            
            VStack(alignment: .leading, spacing: 2) {
                Text(entry.action)
                    .font(DeevoTypography.labelMedium)
                    .foregroundColor(DeevoColors.textPrimary)
                Text(entry.details)
                    .font(DeevoTypography.bodySmall)
                    .foregroundColor(DeevoColors.textSecondary)
                    .lineLimit(2)
            }
            
            Spacer()
            
            Text(entry.timestamp, style: .relative)
                .font(DeevoTypography.labelSmall)
                .foregroundColor(DeevoColors.textTertiary)
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
    }
}

struct AIAuditEntry: Identifiable, Equatable {
    let id: UUID
    let action: String
    let details: String
    let timestamp: Date
    let icon: String
    
    init(action: String, details: String, timestamp: Date, icon: String) {
        self.id = UUID()
        self.action = action
        self.details = details
        self.timestamp = timestamp
        self.icon = icon
    }
}

// MARK: - Override Sheet

struct AIOverrideSheet: View {
    let claim: Claim
    @ObservedObject var viewModel: AIIntelligenceViewModel
    @Environment(\.dismiss) private var dismiss
    @State private var selectedDecision: AIRecommendation = .approve
    @State private var justification = ""
    @State private var isSubmitting = false
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Current Decision
                    SectionCard {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Current AI Decision")
                                .font(DeevoTypography.labelMedium)
                                .foregroundColor(DeevoColors.textSecondary)
                            
                            HStack {
                                Image(systemName: viewModel.recommendation.icon)
                                    .foregroundColor(viewModel.recommendation.color)
                                Text(viewModel.recommendation.displayName)
                                    .font(DeevoTypography.headlineMedium)
                                    .foregroundColor(DeevoColors.textPrimary)
                            }
                        }
                        .padding()
                    }
                    
                    // New Decision
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Override To")
                            .font(DeevoTypography.labelMedium)
                            .foregroundColor(DeevoColors.textSecondary)
                        
                        ForEach([AIRecommendation.approve, .deny, .review], id: \.rawValue) { decision in
                            Button(action: { selectedDecision = decision }) {
                                HStack {
                                    Image(systemName: decision.icon)
                                        .foregroundColor(decision.color)
                                    Text(decision.displayName)
                                        .foregroundColor(DeevoColors.textPrimary)
                                    Spacer()
                                    if selectedDecision == decision {
                                        Image(systemName: "checkmark.circle.fill")
                                            .foregroundColor(DeevoColors.accent)
                                    }
                                }
                                .padding()
                                .background(
                                    RoundedRectangle(cornerRadius: 8)
                                        .fill(selectedDecision == decision ? DeevoColors.accent.opacity(0.1) : DeevoColors.surface)
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 8)
                                                .stroke(selectedDecision == decision ? DeevoColors.accent : DeevoColors.divider, lineWidth: 1)
                                        )
                                )
                            }
                        }
                    }
                    
                    // Justification
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Justification (Required)")
                            .font(DeevoTypography.labelMedium)
                            .foregroundColor(DeevoColors.textSecondary)
                        
                        TextEditor(text: $justification)
                            .frame(minHeight: 120)
                            .padding(8)
                            .background(DeevoColors.surface)
                            .cornerRadius(8)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(DeevoColors.divider, lineWidth: 1)
                            )
                        
                        Text("Minimum 20 characters required for audit compliance")
                            .font(DeevoTypography.labelSmall)
                            .foregroundColor(DeevoColors.textTertiary)
                    }
                    
                    // Warning
                    HStack(spacing: 12) {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundColor(DeevoColors.warning)
                        Text("This action will be logged in the audit trail and cannot be undone.")
                            .font(DeevoTypography.bodySmall)
                            .foregroundColor(DeevoColors.textSecondary)
                    }
                    .padding()
                    .background(DeevoColors.warning.opacity(0.1))
                    .cornerRadius(8)
                }
                .padding()
            }
            .background(DeevoColors.backgroundDark.ignoresSafeArea())
            .navigationTitle("Override AI Decision")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                        .foregroundColor(DeevoColors.textSecondary)
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Submit") {
                        submitOverride()
                    }
                    .disabled(justification.count < 20 || isSubmitting)
                    .foregroundColor(justification.count >= 20 ? DeevoColors.accent : DeevoColors.textTertiary)
                }
            }
        }
    }
    
    private func submitOverride() {
        isSubmitting = true
        viewModel.submitOverride(
            newDecision: selectedDecision,
            justification: justification
        ) {
            dismiss()
        }
    }
}

// MARK: - View Model

@MainActor
class AIIntelligenceViewModel: ObservableObject {
    let claim: Claim
    @Published var recommendation: AIRecommendation = .review
    @Published var confidence: Double = 0.0
    @Published var explanations: [AIExplanation] = []
    @Published var currentOverride: AIOverrideRecord?
    @Published var auditEntries: [AIAuditEntry] = []
    
    init(claim: Claim) {
        self.claim = claim
        loadAIData()
    }
    
    func loadAIData() {
        // Parse AI decision from claim
        if let decision = claim.aiDecision {
            recommendation = AIRecommendation(rawValue: decision) ?? .review
        }
        
        confidence = claim.aiConfidence ?? 0.75
        
        // Generate explanations based on claim data
        var factors: [AIExplanation] = []
        
        // Claim amount factor
        if claim.claimAmount < 5000 {
            factors.append(AIExplanation(
                factor: "Claim Amount",
                impact: "Low value claim under $5,000",
                weight: 0.15,
                isPositive: true
            ))
        } else if claim.claimAmount > 50000 {
            factors.append(AIExplanation(
                factor: "Claim Amount",
                impact: "High value claim over $50,000",
                weight: 0.25,
                isPositive: false
            ))
        }
        
        // Documentation factor
        factors.append(AIExplanation(
            factor: "Documentation",
            impact: "Required documents provided",
            weight: 0.20,
            isPositive: true
        ))
        
        // Reporting timeliness
        if let incidentDate = claim.incidentDate {
            let daysSinceIncident = Calendar.current.dateComponents([.day], from: incidentDate, to: claim.createdAt).day ?? 0
            if daysSinceIncident <= 7 {
                factors.append(AIExplanation(
                    factor: "Reporting Timeliness",
                    impact: "Reported within 7 days of incident",
                    weight: 0.15,
                    isPositive: true
                ))
            } else {
                factors.append(AIExplanation(
                    factor: "Reporting Timeliness",
                    impact: "Reported \(daysSinceIncident) days after incident",
                    weight: 0.10,
                    isPositive: false
                ))
            }
        }
        
        // Risk score factor
        if let riskScore = claim.riskScore {
            if riskScore <= 30 {
                factors.append(AIExplanation(
                    factor: "Risk Assessment",
                    impact: "Low risk score (\(riskScore))",
                    weight: 0.25,
                    isPositive: true
                ))
            } else if riskScore > 60 {
                factors.append(AIExplanation(
                    factor: "Risk Assessment",
                    impact: "Elevated risk score (\(riskScore))",
                    weight: 0.30,
                    isPositive: false
                ))
            }
        }
        
        explanations = factors
        
        // Load audit entries
        auditEntries = [
            AIAuditEntry(
                action: "AI Analysis Completed",
                details: "Recommendation: \(recommendation.displayName) with \(Int(confidence * 100))% confidence",
                timestamp: claim.updatedAt,
                icon: "cpu"
            ),
            AIAuditEntry(
                action: "Claim Submitted",
                details: "Initial claim submission for processing",
                timestamp: claim.createdAt,
                icon: "doc.badge.plus"
            )
        ]
    }
    
    func submitOverride(newDecision: AIRecommendation, justification: String, completion: @escaping () -> Void) {
        let override = AIOverrideRecord(
            id: UUID().uuidString,
            claimId: claim.id,
            originalDecision: recommendation.rawValue,
            overrideDecision: newDecision.rawValue,
            justification: justification,
            overriddenBy: "Current User",
            overriddenAt: Date()
        )
        
        currentOverride = override
        
        // Add audit entry
        auditEntries.insert(
            AIAuditEntry(
                action: "Decision Overridden",
                details: "Changed from \(recommendation.displayName) to \(newDecision.displayName)",
                timestamp: Date(),
                icon: "arrow.triangle.2.circlepath"
            ),
            at: 0
        )
        
        recommendation = newDecision
        
        // TODO: Persist to database and sync
        
        completion()
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        AIIntelligencePanelView(claim: Claim(
            claimNumber: "CLM-2024-001",
            policyNumber: "POL-123456",
            status: .pendingReview,
            customerName: "John Doe",
            customerPhone: "555-1234",
            customerEmail: "john@example.com",
            incidentDate: Date().addingTimeInterval(-86400 * 5),
            incidentDescription: "Water damage from burst pipe",
            aiDecision: "approve",
            aiConfidence: 0.85,
            riskScore: 35,
            claimAmount: 15000,
            tenantId: "tenant-1"
        ))
    }
}
