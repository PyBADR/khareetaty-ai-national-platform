import SwiftUI

/// View displayed when the user's session has expired
struct SessionExpiryView: View {
    @Environment(\.dismiss) private var dismiss
    
    let onRelogin: () -> Void
    let hasPendingOfflineData: Bool
    
    var body: some View {
        VStack(spacing: 32) {
            Spacer()
            
            // Icon
            Image(systemName: "clock.badge.exclamationmark")
                .font(.system(size: 72))
                .foregroundStyle(DeevoColors.accent)
            
            // Title
            Text("Session Expired")
                .font(DeevoTypography.displayMedium)
                .foregroundStyle(DeevoColors.textPrimary)
            
            // Message
            Text("Your session has expired for security reasons. Please log in again to continue.")
                .font(DeevoTypography.bodyLarge)
                .foregroundStyle(DeevoColors.textSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)
            
            // Offline data notice
            if hasPendingOfflineData {
                HStack(spacing: 12) {
                    Image(systemName: "icloud.and.arrow.up")
                        .foregroundStyle(DeevoColors.accent)
                    
                    Text("Your offline changes are safely stored and will sync after you log in.")
                        .font(DeevoTypography.caption)
                        .foregroundStyle(DeevoColors.textSecondary)
                }
                .padding(16)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(DeevoColors.accent.opacity(0.1))
                )
                .padding(.horizontal, 24)
            }
            
            Spacer()
            
            // Login button
            PrimaryButton("Log In Again") {
                onRelogin()
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 48)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(DeevoColors.backgroundDark)
    }
}

/// Modifier to handle session expiry globally
struct SessionExpiryModifier: ViewModifier {
    @State private var showSessionExpiry = false
    @State private var hasPendingOfflineData = false
    
    let onRelogin: () -> Void
    
    func body(content: Content) -> some View {
        content
            .onReceive(NotificationCenter.default.publisher(for: .sessionExpired)) { _ in
                // Check for pending offline data
                Task {
                    hasPendingOfflineData = await checkPendingOfflineData()
                    showSessionExpiry = true
                }
            }
            .fullScreenCover(isPresented: $showSessionExpiry) {
                SessionExpiryView(
                    onRelogin: {
                        showSessionExpiry = false
                        onRelogin()
                    },
                    hasPendingOfflineData: hasPendingOfflineData
                )
            }
    }
    
    private func checkPendingOfflineData() async -> Bool {
        // Check if there are any pending sync items in the local database
        // This is a simplified check - in production, query the sync queue
        return false // Placeholder - implement based on SyncService
    }
}

extension View {
    /// Add session expiry handling to a view
    func handleSessionExpiry(onRelogin: @escaping () -> Void) -> some View {
        modifier(SessionExpiryModifier(onRelogin: onRelogin))
    }
}

#Preview {
    SessionExpiryView(
        onRelogin: {},
        hasPendingOfflineData: true
    )
}
