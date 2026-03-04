import SwiftUI

// MARK: - Deevo Sentinel Pill Badge
// Used for status indicators, tags, and labels

public enum PillBadgeStyle {
    case primary
    case secondary
    case accent
    case success
    case warning
    case error
    case info
    case riskLow
    case riskModerate
    case riskElevated
    case riskCritical
    case custom(background: Color, foreground: Color)
    
    var backgroundColor: Color {
        switch self {
        case .primary: return DeevoColors.primary
        case .secondary: return DeevoColors.secondary
        case .accent: return DeevoColors.accent.opacity(0.2)
        case .success: return DeevoColors.success.opacity(0.2)
        case .warning: return DeevoColors.warning.opacity(0.2)
        case .error: return DeevoColors.error.opacity(0.2)
        case .info: return DeevoColors.info.opacity(0.2)
        case .riskLow: return DeevoColors.riskLow.opacity(0.2)
        case .riskModerate: return DeevoColors.riskModerate.opacity(0.2)
        case .riskElevated: return DeevoColors.riskElevated.opacity(0.2)
        case .riskCritical: return DeevoColors.riskCritical.opacity(0.2)
        case .custom(let bg, _): return bg
        }
    }
    
    var foregroundColor: Color {
        switch self {
        case .primary: return DeevoColors.textPrimary
        case .secondary: return DeevoColors.textPrimary
        case .accent: return DeevoColors.accent
        case .success: return DeevoColors.success
        case .warning: return DeevoColors.warning
        case .error: return DeevoColors.error
        case .info: return DeevoColors.info
        case .riskLow: return DeevoColors.riskLow
        case .riskModerate: return DeevoColors.riskModerate
        case .riskElevated: return DeevoColors.riskElevated
        case .riskCritical: return DeevoColors.riskCritical
        case .custom(_, let fg): return fg
        }
    }
}

public struct PillBadge: View {
    let text: String
    let icon: String?
    let style: PillBadgeStyle
    
    public init(
        _ text: String,
        icon: String? = nil,
        style: PillBadgeStyle = .primary
    ) {
        self.text = text
        self.icon = icon
        self.style = style
    }
    
    public var body: some View {
        HStack(spacing: 4) {
            if let icon = icon {
                Image(systemName: icon)
                    .font(.system(size: 10, weight: .semibold))
            }
            Text(text)
                .font(DeevoTypography.labelSmall)
                .fontWeight(.semibold)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 5)
        .background(style.backgroundColor)
        .foregroundColor(style.foregroundColor)
        .cornerRadius(20)
    }
}

// MARK: - Status Badge (Larger variant)

public struct StatusBadge: View {
    let text: String
    let icon: String?
    let style: PillBadgeStyle
    
    public init(
        _ text: String,
        icon: String? = nil,
        style: PillBadgeStyle = .primary
    ) {
        self.text = text
        self.icon = icon
        self.style = style
    }
    
    public var body: some View {
        HStack(spacing: 6) {
            if let icon = icon {
                Image(systemName: icon)
                    .font(.system(size: 12, weight: .semibold))
            }
            Text(text)
                .font(DeevoTypography.labelMedium)
                .fontWeight(.semibold)
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(style.backgroundColor)
        .foregroundColor(style.foregroundColor)
        .cornerRadius(8)
    }
}

// MARK: - Risk Score Badge

public struct RiskScoreBadge: View {
    let score: Int
    
    public init(score: Int) {
        self.score = max(0, min(100, score))
    }
    
    private var riskBand: (String, PillBadgeStyle) {
        switch score {
        case 0...30: return ("Low", .riskLow)
        case 31...60: return ("Moderate", .riskModerate)
        case 61...80: return ("Elevated", .riskElevated)
        default: return ("Critical", .riskCritical)
        }
    }
    
    public var body: some View {
        HStack(spacing: 8) {
            Text("\(score)")
                .font(DeevoTypography.headlineMedium)
                .fontWeight(.bold)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(riskBand.0)
                    .font(DeevoTypography.labelSmall)
                    .fontWeight(.semibold)
                Text("Risk Score")
                    .font(DeevoTypography.captionSmall)
            }
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 10)
        .background(riskBand.1.backgroundColor)
        .foregroundColor(riskBand.1.foregroundColor)
        .cornerRadius(10)
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: 16) {
        HStack(spacing: 8) {
            PillBadge("Pending", icon: "clock", style: .warning)
            PillBadge("Approved", icon: "checkmark", style: .success)
            PillBadge("Rejected", icon: "xmark", style: .error)
        }
        
        HStack(spacing: 8) {
            PillBadge("Low", style: .riskLow)
            PillBadge("Moderate", style: .riskModerate)
            PillBadge("Elevated", style: .riskElevated)
            PillBadge("Critical", style: .riskCritical)
        }
        
        StatusBadge("In Review", icon: "eye", style: .info)
        
        HStack(spacing: 16) {
            RiskScoreBadge(score: 25)
            RiskScoreBadge(score: 55)
            RiskScoreBadge(score: 75)
            RiskScoreBadge(score: 92)
        }
    }
    .padding()
    .background(DeevoColors.backgroundDark)
}
