import SwiftUI

// MARK: - Risk Assessment View

struct RiskAssessmentView: View {
    let claim: Claim
    @StateObject private var viewModel: RiskAssessmentViewModel
    
    init(claim: Claim) {
        self.claim = claim
        self._viewModel = StateObject(wrappedValue: RiskAssessmentViewModel(claim: claim))
    }
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Risk Score Header
                riskScoreHeader
                
                // Risk Gauge
                riskGaugeSection
                
                // Risk Factors Breakdown
                riskFactorsSection
                
                // Risk Band Legend
                riskBandLegend
            }
            .padding()
        }
        .background(DeevoColors.backgroundDark.ignoresSafeArea())
        .navigationTitle("Risk Assessment")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button(action: { viewModel.recalculate() }) {
                    Image(systemName: "arrow.clockwise")
                        .foregroundColor(DeevoColors.accent)
                }
            }
        }
    }
    
    // MARK: - Risk Score Header
    
    private var riskScoreHeader: some View {
        SectionCard {
            VStack(spacing: 16) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Risk Score")
                            .font(DeevoTypography.labelMedium)
                            .foregroundColor(DeevoColors.textSecondary)
                        Text("\(viewModel.assessment.totalScore)")
                            .font(.system(size: 64, weight: .bold))
                            .foregroundColor(viewModel.assessment.band.color)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing, spacing: 8) {
                        PillBadge(
                            viewModel.assessment.band.displayName,
                            style: .custom(background: viewModel.assessment.band.color.opacity(0.2), foreground: viewModel.assessment.band.color)
                        )
                        
                        Text("Range: \(viewModel.assessment.band.range.lowerBound)-\(viewModel.assessment.band.range.upperBound)")
                            .font(DeevoTypography.labelSmall)
                            .foregroundColor(DeevoColors.textTertiary)
                    }
                }
                
                HStack {
                    Image(systemName: "clock")
                        .foregroundColor(DeevoColors.textTertiary)
                    Text("Assessed: \(viewModel.assessment.assessedAt.formatted())")
                        .font(DeevoTypography.labelSmall)
                        .foregroundColor(DeevoColors.textTertiary)
                }
            }
            .padding()
        }
    }
    
    // MARK: - Risk Gauge Section
    
    private var riskGaugeSection: some View {
        SectionCard {
            VStack(spacing: 16) {
                Text("Risk Level")
                    .font(DeevoTypography.headlineMedium)
                    .foregroundColor(DeevoColors.textPrimary)
                
                RiskGauge(score: viewModel.assessment.totalScore)
                    .frame(height: 120)
                
                HStack {
                    ForEach(RiskBand.allCases, id: \.rawValue) { band in
                        VStack(spacing: 4) {
                            Circle()
                                .fill(band.color)
                                .frame(width: 12, height: 12)
                            Text(band.displayName)
                                .font(DeevoTypography.labelSmall)
                                .foregroundColor(DeevoColors.textSecondary)
                        }
                        .frame(maxWidth: .infinity)
                    }
                }
            }
            .padding()
        }
    }
    
    // MARK: - Risk Factors Section
    
    private var riskFactorsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Risk Factors")
                .font(DeevoTypography.headlineMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            SectionCard {
                VStack(spacing: 8) {
                    ForEach(0..<viewModel.assessment.factors.count, id: \.self) { index in
                        RiskFactorRow(factor: viewModel.assessment.factors[index])
                    }
                }
                .padding(.vertical, 8)
            }
        }
    }
    
    // MARK: - Risk Band Legend
    
    private var riskBandLegend: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Risk Band Reference")
                .font(DeevoTypography.headlineMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            SectionCard {
                VStack(spacing: 12) {
                    ForEach(RiskBand.allCases, id: \.rawValue) { band in
                        HStack {
                            RoundedRectangle(cornerRadius: 4)
                                .fill(band.color)
                                .frame(width: 24, height: 24)
                            
                            Text(band.displayName)
                                .font(DeevoTypography.labelMedium)
                                .foregroundColor(DeevoColors.textPrimary)
                            
                            Spacer()
                            
                            Text("\(band.range.lowerBound) - \(band.range.upperBound)")
                                .font(DeevoTypography.labelMedium)
                                .foregroundColor(DeevoColors.textSecondary)
                        }
                    }
                }
                .padding()
            }
        }
    }
}

// MARK: - Supporting Views

struct RiskGauge: View {
    let score: Int
    
    var body: some View {
        GeometryReader { geometry in
            let width = geometry.size.width
            let height = geometry.size.height
            let centerX = width / 2
            let centerY = height
            let radius = min(width / 2, height) - 20
            
            ZStack {
                // Background arc
                Path { path in
                    path.addArc(
                        center: CGPoint(x: centerX, y: centerY),
                        radius: radius,
                        startAngle: .degrees(180),
                        endAngle: .degrees(0),
                        clockwise: false
                    )
                }
                .stroke(DeevoColors.surfaceElevated, lineWidth: 20)
                
                // Colored segments
                ForEach(Array(RiskBand.allCases.enumerated()), id: \.element.rawValue) { index, band in
                    let startAngle = 180.0 + (Double(band.range.lowerBound) / 100.0 * 180.0)
                    let endAngle = 180.0 + (Double(band.range.upperBound) / 100.0 * 180.0)
                    
                    Path { path in
                        path.addArc(
                            center: CGPoint(x: centerX, y: centerY),
                            radius: radius,
                            startAngle: .degrees(startAngle),
                            endAngle: .degrees(endAngle),
                            clockwise: false
                        )
                    }
                    .stroke(band.color, lineWidth: 20)
                }
                
                // Needle
                let needleAngle = 180.0 + (Double(score) / 100.0 * 180.0)
                let needleLength = radius - 30
                let needleX = centerX + needleLength * cos(needleAngle * .pi / 180)
                let needleY = centerY + needleLength * sin(needleAngle * .pi / 180)
                
                Path { path in
                    path.move(to: CGPoint(x: centerX, y: centerY))
                    path.addLine(to: CGPoint(x: needleX, y: needleY))
                }
                .stroke(DeevoColors.textPrimary, lineWidth: 3)
                
                // Center circle
                Circle()
                    .fill(DeevoColors.textPrimary)
                    .frame(width: 16, height: 16)
                    .position(x: centerX, y: centerY)
            }
        }
    }
}

struct RiskFactorRow: View {
    let factor: RiskFactor
    
    private var percentage: Double {
        guard factor.maxPoints > 0 else { return 0 }
        return Double(factor.points) / Double(factor.maxPoints)
    }
    
    private var severityColor: Color {
        switch percentage {
        case 0: return DeevoColors.success
        case ..<0.5: return DeevoColors.warning
        default: return DeevoColors.error
        }
    }
    
    var body: some View {
        VStack(spacing: 8) {
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text(factor.name)
                        .font(DeevoTypography.labelMedium)
                        .foregroundColor(DeevoColors.textPrimary)
                    Text(factor.description)
                        .font(DeevoTypography.bodySmall)
                        .foregroundColor(DeevoColors.textSecondary)
                }
                
                Spacer()
                
                Text("\(factor.points)/\(factor.maxPoints)")
                    .font(DeevoTypography.labelMedium)
                    .foregroundColor(severityColor)
            }
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(DeevoColors.surfaceElevated)
                        .frame(height: 6)
                        .cornerRadius(3)
                    
                    Rectangle()
                        .fill(severityColor)
                        .frame(width: geometry.size.width * CGFloat(percentage), height: 6)
                        .cornerRadius(3)
                }
            }
            .frame(height: 6)
        }
        .padding(.horizontal)
        .padding(.vertical, 12)
    }
}

// MARK: - View Model

@MainActor
class RiskAssessmentViewModel: ObservableObject {
    let claim: Claim
    @Published var assessment: RiskAssessment
    
    init(claim: Claim) {
        self.claim = claim
        self.assessment = RiskEngineService.shared.calculateRiskScore(for: claim)
    }
    
    func recalculate() {
        assessment = RiskEngineService.shared.calculateRiskScore(for: claim)
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        RiskAssessmentView(claim: Claim(
            claimNumber: "CLM-2024-001",
            policyNumber: "POL-123456",
            status: .pendingReview,
            customerName: "John Doe",
            customerPhone: "555-1234",
            customerEmail: "john@example.com",
            incidentDate: Date().addingTimeInterval(-86400 * 15),
            incidentDescription: "Water damage from burst pipe",
            tenantId: "tenant-1"
        ))
    }
}
