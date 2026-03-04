import SwiftUI

// MARK: - Deevo Sentinel Section Card
// Used for grouping related content in a card container

public struct SectionCard<Content: View>: View {
    let title: String?
    let subtitle: String?
    let icon: String?
    let action: (() -> Void)?
    let actionLabel: String?
    let content: Content
    
    public init(
        title: String? = nil,
        subtitle: String? = nil,
        icon: String? = nil,
        action: (() -> Void)? = nil,
        actionLabel: String? = nil,
        @ViewBuilder content: () -> Content
    ) {
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self.action = action
        self.actionLabel = actionLabel
        self.content = content()
    }
    
    public var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Header
            if title != nil || action != nil {
                HStack(alignment: .center) {
                    if let icon = icon {
                        Image(systemName: icon)
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(DeevoColors.accent)
                    }
                    
                    VStack(alignment: .leading, spacing: 2) {
                        if let title = title {
                            Text(title)
                                .font(DeevoTypography.headlineMedium)
                                .foregroundColor(DeevoColors.textPrimary)
                        }
                        
                        if let subtitle = subtitle {
                            Text(subtitle)
                                .font(DeevoTypography.caption)
                                .foregroundColor(DeevoColors.textTertiary)
                        }
                    }
                    
                    Spacer()
                    
                    if let action = action, let actionLabel = actionLabel {
                        Button(action: action) {
                            Text(actionLabel)
                                .font(DeevoTypography.labelMedium)
                                .foregroundColor(DeevoColors.accent)
                        }
                    }
                }
            }
            
            // Content
            content
        }
        .padding(20)
        .background(DeevoColors.surface)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(DeevoColors.border, lineWidth: 1)
        )
    }
}

// MARK: - Compact Section Card

public struct CompactSectionCard<Content: View>: View {
    let content: Content
    
    public init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }
    
    public var body: some View {
        content
            .padding(16)
            .background(DeevoColors.surface)
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(DeevoColors.border, lineWidth: 1)
            )
    }
}

// MARK: - Info Row (for use inside cards)

public struct InfoRow: View {
    let label: String
    let value: String
    let icon: String?
    let valueColor: Color
    
    public init(
        label: String,
        value: String,
        icon: String? = nil,
        valueColor: Color = DeevoColors.textPrimary
    ) {
        self.label = label
        self.value = value
        self.icon = icon
        self.valueColor = valueColor
    }
    
    public var body: some View {
        HStack {
            if let icon = icon {
                Image(systemName: icon)
                    .font(.system(size: 14))
                    .foregroundColor(DeevoColors.textTertiary)
                    .frame(width: 24)
            }
            
            Text(label)
                .font(DeevoTypography.bodyMedium)
                .foregroundColor(DeevoColors.textSecondary)
            
            Spacer()
            
            Text(value)
                .font(DeevoTypography.bodyMedium)
                .fontWeight(.medium)
                .foregroundColor(valueColor)
        }
    }
}

// MARK: - Divider

public struct SectionDivider: View {
    public init() {}
    
    public var body: some View {
        Rectangle()
            .fill(DeevoColors.border)
            .frame(height: 1)
    }
}

// MARK: - Preview

#Preview {
    ScrollView {
        VStack(spacing: 20) {
            SectionCard(
                title: "Claim Details",
                subtitle: "Last updated 2 hours ago",
                icon: "doc.text",
                action: { print("Edit") },
                actionLabel: "Edit"
            ) {
                VStack(spacing: 12) {
                    InfoRow(label: "Claim ID", value: "CLM-2024-001", icon: "number")
                    SectionDivider()
                    InfoRow(label: "Status", value: "In Review", icon: "clock", valueColor: DeevoColors.warning)
                    SectionDivider()
                    InfoRow(label: "Amount", value: "$12,500.00", icon: "dollarsign.circle")
                }
            }
            
            CompactSectionCard {
                HStack {
                    Image(systemName: "exclamationmark.triangle")
                        .foregroundColor(DeevoColors.warning)
                    Text("3 items require attention")
                        .font(DeevoTypography.bodyMedium)
                        .foregroundColor(DeevoColors.textPrimary)
                    Spacer()
                    Image(systemName: "chevron.right")
                        .foregroundColor(DeevoColors.textTertiary)
                }
            }
        }
        .padding()
    }
    .background(DeevoColors.backgroundDark)
}
