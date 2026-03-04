import SwiftUI

/// Branded launch screen for Deevo Sentinel
/// Displays the app logo, name, and tagline with the Deevo design system
struct LaunchScreenView: View {
    @State private var isAnimating = false
    
    var body: some View {
        ZStack {
            // Background gradient
            LinearGradient(
                colors: [
                    DeevoColors.backgroundDark,
                    DeevoColors.primary
                ],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()
            
            VStack(spacing: 32) {
                Spacer()
                
                // Logo container
                ZStack {
                    // Outer glow ring
                    Circle()
                        .stroke(
                            DeevoColors.accent.opacity(0.3),
                            lineWidth: 2
                        )
                        .frame(width: 160, height: 160)
                        .scaleEffect(isAnimating ? 1.1 : 1.0)
                        .opacity(isAnimating ? 0.5 : 1.0)
                    
                    // Inner circle with icon
                    Circle()
                        .fill(DeevoColors.primary)
                        .frame(width: 140, height: 140)
                        .shadow(color: DeevoColors.accent.opacity(0.4), radius: 20)
                    
                    // Shield icon representing security/protection
                    Image(systemName: "shield.checkered")
                        .font(.system(size: 64, weight: .medium))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [DeevoColors.accent, DeevoColors.accentLight],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                }
                
                VStack(spacing: 12) {
                    // App name
                    Text("Deevo Sentinel")
                        .font(.system(size: 42, weight: .bold, design: .default))
                        .foregroundColor(DeevoColors.textPrimary)
                        .tracking(1)
                    
                    // Tagline
                    Text("Sovereign Claims Decision Infrastructure")
                        .font(.system(size: 16, weight: .medium, design: .default))
                        .foregroundColor(DeevoColors.accent)
                        .tracking(2)
                        .textCase(.uppercase)
                }
                
                Spacer()
                
                // Loading indicator
                VStack(spacing: 16) {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: DeevoColors.accent))
                        .scaleEffect(1.2)
                    
                    Text("Initializing secure environment...")
                        .font(.system(size: 13, weight: .regular))
                        .foregroundColor(DeevoColors.textSecondary)
                }
                
                Spacer()
                    .frame(height: 40)
                
                // Footer branding
                VStack(spacing: 4) {
                    Text("Powered by")
                        .font(.system(size: 11, weight: .regular))
                        .foregroundColor(DeevoColors.textTertiary)
                    
                    Text("Deevo Analytics")
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(DeevoColors.textSecondary)
                }
                .padding(.bottom, 32)
            }
        }
        .onAppear {
            withAnimation(
                .easeInOut(duration: 1.5)
                .repeatForever(autoreverses: true)
            ) {
                isAnimating = true
            }
        }
    }
}

#Preview {
    LaunchScreenView()
}
