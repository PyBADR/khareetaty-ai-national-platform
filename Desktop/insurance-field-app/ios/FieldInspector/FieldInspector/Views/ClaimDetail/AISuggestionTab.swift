import SwiftUI

struct AISuggestionTab: View {
    let claimId: String
    
    @State private var decision: AIDecisionResponse?
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var metadata: AIMetadata?
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                if isLoading {
                    VStack(spacing: 16) {
                        ProgressView()
                            .scaleEffect(1.5)
                        Text("Analyzing claim data...")
                            .font(.headline)
                        Text("The AI is reviewing inspection data, photos, and claim details.")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding(40)
                } else if let decision = decision {
                    // Recommendation Card
                    VStack(spacing: 16) {
                        Image(systemName: decision.recommendedAction.iconName)
                            .font(.system(size: 50))
                            .foregroundColor(actionColor(decision.recommendedAction))
                        
                        Text(decision.recommendedAction.displayName)
                            .font(.title)
                            .fontWeight(.bold)
                        
                        HStack {
                            Text("Confidence:")
                                .foregroundColor(.secondary)
                            Text(decision.confidencePercentage)
                                .fontWeight(.semibold)
                            Text("(\(decision.confidenceLevel))")
                                .foregroundColor(.secondary)
                        }
                        
                        // Confidence bar
                        GeometryReader { geometry in
                            ZStack(alignment: .leading) {
                                Rectangle()
                                    .fill(Color(.systemGray5))
                                    .frame(height: 8)
                                    .cornerRadius(4)
                                
                                Rectangle()
                                    .fill(confidenceColor(decision.confidence))
                                    .frame(width: geometry.size.width * decision.confidence, height: 8)
                                    .cornerRadius(4)
                            }
                        }
                        .frame(height: 8)
                        .padding(.horizontal, 40)
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(16)
                    
                    // Key Findings
                    if !decision.keyFindings.isEmpty {
                        GroupBox {
                            VStack(alignment: .leading, spacing: 8) {
                                ForEach(decision.keyFindings, id: \.self) { finding in
                                    HStack(alignment: .top, spacing: 8) {
                                        Image(systemName: "checkmark.circle.fill")
                                            .foregroundColor(DeevoColors.success)
                                        Text(finding)
                                    }
                                }
                            }
                        } label: {
                            Label("Key Findings", systemImage: "magnifyingglass")
                        }
                    }
                    
                    // Missing Information
                    if !decision.missingInfo.isEmpty {
                        GroupBox {
                            VStack(alignment: .leading, spacing: 8) {
                                ForEach(decision.missingInfo, id: \.self) { info in
                                    HStack(alignment: .top, spacing: 8) {
                                        Image(systemName: "exclamationmark.triangle.fill")
                                            .foregroundColor(DeevoColors.accent)
                                        Text(info)
                                    }
                                }
                            }
                        } label: {
                            Label("Missing Information", systemImage: "questionmark.circle")
                        }
                    }
                    
                    // Next Steps
                    if !decision.nextSteps.isEmpty {
                        GroupBox {
                            VStack(alignment: .leading, spacing: 8) {
                                ForEach(Array(decision.nextSteps.enumerated()), id: \.offset) { index, step in
                                    HStack(alignment: .top, spacing: 8) {
                                        Text("\(index + 1).")
                                            .fontWeight(.semibold)
                                            .foregroundColor(DeevoColors.secondary)
                                        Text(step)
                                    }
                                }
                            }
                        } label: {
                            Label("Recommended Next Steps", systemImage: "arrow.right.circle")
                        }
                    }
                    
                    // Policy Notes
                    if !decision.policyNotes.isEmpty {
                        GroupBox {
                            VStack(alignment: .leading, spacing: 8) {
                                ForEach(decision.policyNotes, id: \.self) { note in
                                    HStack(alignment: .top, spacing: 8) {
                                        Image(systemName: "doc.text")
                                            .foregroundColor(DeevoColors.secondary)
                                        Text(note)
                                    }
                                }
                            }
                        } label: {
                            Label("Policy Notes", systemImage: "doc.text")
                        }
                    }
                    
                    // Reason Codes
                    if !decision.reasonCodes.isEmpty {
                        GroupBox {
                            FlowLayout(spacing: 8) {
                                ForEach(decision.reasonCodes, id: \.self) { code in
                                    Text(code)
                                        .font(.caption)
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 4)
                                        .background(DeevoColors.secondary.opacity(0.1))
                                        .foregroundColor(DeevoColors.secondary)
                                        .cornerRadius(4)
                                }
                            }
                        } label: {
                            Label("Reason Codes", systemImage: "tag")
                        }
                    }
                    
                    // Audit Summary
                    GroupBox {
                        Text(decision.auditSummary)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    } label: {
                        Label("Audit Summary", systemImage: "clock.arrow.circlepath")
                    }
                    
                    // Metadata
                    if let metadata = metadata {
                        HStack {
                            Text("Model: \(metadata.model)")
                            Spacer()
                            Text("Duration: \(metadata.durationMs)ms")
                        }
                        .font(.caption)
                        .foregroundColor(.secondary)
                    }
                    
                    // Refresh button
                    Button(action: requestSuggestion) {
                        Label("Request New Analysis", systemImage: "arrow.clockwise")
                    }
                    .buttonStyle(.bordered)
                    
                } else if let error = errorMessage {
                    VStack(spacing: 16) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.system(size: 50))
                            .foregroundColor(DeevoColors.accent)
                        Text("Analysis Failed")
                            .font(.headline)
                        Text(error)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                        Button("Try Again") {
                            requestSuggestion()
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .padding(40)
                } else {
                    VStack(spacing: 16) {
                        Image(systemName: "brain")
                            .font(.system(size: 60))
                            .foregroundColor(.secondary)
                        Text("AI Decision Assistance")
                            .font(.headline)
                        Text("Get an AI-powered analysis of this claim based on inspection data, photos, and claim details.")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                        Button(action: requestSuggestion) {
                            Label("Request AI Analysis", systemImage: "sparkles")
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .padding(40)
                }
            }
            .padding()
        }
    }
    
    private func requestSuggestion() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                let response = try await APIService.shared.getAISuggestion(claimId: claimId)
                await MainActor.run {
                    decision = response.decision
                    metadata = response.metadata
                    isLoading = false
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isLoading = false
                }
            }
        }
    }
    
    private func actionColor(_ action: AIRecommendedAction) -> Color {
        switch action {
        case .approve: return DeevoColors.success
        case .reject: return DeevoColors.error
        case .needMoreInfo: return DeevoColors.accent
        case .refer: return DeevoColors.secondary
        }
    }
    
    private func confidenceColor(_ confidence: Double) -> Color {
        switch confidence {
        case 0.8...1.0: return DeevoColors.riskLow
        case 0.6..<0.8: return DeevoColors.riskModerate
        case 0.4..<0.6: return DeevoColors.riskElevated
        default: return DeevoColors.riskCritical
        }
    }
}

// MARK: - Flow Layout

struct FlowLayout: Layout {
    var spacing: CGFloat = 8
    
    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = FlowResult(in: proposal.width ?? 0, subviews: subviews, spacing: spacing)
        return result.size
    }
    
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = FlowResult(in: bounds.width, subviews: subviews, spacing: spacing)
        for (index, subview) in subviews.enumerated() {
            subview.place(at: CGPoint(x: bounds.minX + result.positions[index].x,
                                      y: bounds.minY + result.positions[index].y),
                         proposal: .unspecified)
        }
    }
    
    struct FlowResult {
        var size: CGSize = .zero
        var positions: [CGPoint] = []
        
        init(in maxWidth: CGFloat, subviews: Subviews, spacing: CGFloat) {
            var x: CGFloat = 0
            var y: CGFloat = 0
            var rowHeight: CGFloat = 0
            
            for subview in subviews {
                let size = subview.sizeThatFits(.unspecified)
                
                if x + size.width > maxWidth && x > 0 {
                    x = 0
                    y += rowHeight + spacing
                    rowHeight = 0
                }
                
                positions.append(CGPoint(x: x, y: y))
                rowHeight = max(rowHeight, size.height)
                x += size.width + spacing
                
                self.size.width = max(self.size.width, x)
            }
            
            self.size.height = y + rowHeight
        }
    }
}
