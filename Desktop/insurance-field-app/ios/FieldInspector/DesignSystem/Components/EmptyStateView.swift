import SwiftUI

// MARK: - Deevo Sentinel Empty State View
// Used when there's no content to display

public struct EmptyStateView: View {
    let icon: String
    let title: String
    let message: String
    let actionTitle: String?
    let action: (() -> Void)?
    let iconColor: Color?
    
    public init(
        icon: String,
        title: String,
        message: String,
        actionTitle: String? = nil,
        action: (() -> Void)? = nil,
        iconColor: Color? = nil
    ) {
        self.icon = icon
        self.title = title
        self.message = message
        self.actionTitle = actionTitle
        self.action = action
        self.iconColor = iconColor
    }
    
    public var body: some View {
        VStack(spacing: 24) {
            // Icon
            ZStack {
                Circle()
                    .fill(DeevoColors.surface)
                    .frame(width: 100, height: 100)
                
                Image(systemName: icon)
                    .font(.system(size: 40, weight: .light))
                    .foregroundColor(iconColor ?? DeevoColors.textTertiary)
            }
            
            // Text
            VStack(spacing: 8) {
                Text(title)
                    .font(DeevoTypography.headlineLarge)
                    .foregroundColor(DeevoColors.textPrimary)
                    .multilineTextAlignment(.center)
                
                Text(message)
                    .font(DeevoTypography.bodyMedium)
                    .foregroundColor(DeevoColors.textSecondary)
                    .multilineTextAlignment(.center)
                    .lineLimit(3)
            }
            .padding(.horizontal, 32)
            
            // Action Button
            if let actionTitle = actionTitle, let action = action {
                PrimaryButton(actionTitle, action: action)
                    .frame(maxWidth: 200)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(40)
    }
}

// MARK: - Preset Empty States

extension EmptyStateView {
    /// Empty state for no claims
    public static var noClaims: EmptyStateView {
        EmptyStateView(
            icon: "doc.text.magnifyingglass",
            title: "No Claims Found",
            message: "There are no claims matching your current filters. Try adjusting your search criteria."
        )
    }
    
    /// Empty state for no inspections
    public static var noInspections: EmptyStateView {
        EmptyStateView(
            icon: "checklist",
            title: "No Inspections",
            message: "This claim doesn't have any inspections yet. Start a new inspection to begin the assessment."
        )
    }
    
    /// Empty state for no media
    public static var noMedia: EmptyStateView {
        EmptyStateView(
            icon: "photo.on.rectangle.angled",
            title: "No Evidence Captured",
            message: "No photos or documents have been attached to this inspection yet."
        )
    }
    
    /// Empty state for offline
    public static var offline: EmptyStateView {
        EmptyStateView(
            icon: "wifi.slash",
            title: "You're Offline",
            message: "Connect to the internet to sync your data and access the latest claims."
        )
    }
    
    /// Empty state for sync queue
    public static var syncQueueEmpty: EmptyStateView {
        EmptyStateView(
            icon: "checkmark.circle",
            title: "All Synced",
            message: "All your data has been synchronized with the server. You're up to date."
        )
    }
}

// MARK: - Preview

#Preview {
    VStack {
        EmptyStateView(
            icon: "tray",
            title: "Inbox Empty",
            message: "You have no pending claims to review. Check back later for new assignments.",
            actionTitle: "Refresh",
            action: { print("Refresh") }
        )
    }
    .background(DeevoColors.backgroundDark)
}
