import SwiftUI

/// Branded splash screen for DEEVO Field Inspector
/// Displays for 1.8 seconds then fades to login
/// No spinner per Apple HIG guidelines
struct LaunchScreenView: View {
    @State private var opacity = 0.0
    
    var body: some View {
        ZStack {
            // Background gradient - navy to darker navy
            LinearGradient(
                colors: [
                    DeevoColors.backgroundDark,
                    DeevoColors.primary
                ],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()
            
            VStack(spacing: 16) {
                // DEEVO Shield Logo
                ZStack {
                    // Outer glow
                    Circle()
                        .fill(DeevoColors.accent.opacity(0.15))
                        .frame(width: 160, height: 160)
                    
                    // Inner circle
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [
                                    DeevoColors.primary,
                                    DeevoColors.backgroundDark
                                ],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 140, height: 140)
                        .shadow(color: DeevoColors.accent.opacity(0.3), radius: 20)
                    
                    // Shield icon
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
                
                // App name
                Text("DEEVO Analytics")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundStyle(.white)
                
                // Subtitle
                Text("Field Inspector")
                    .font(.system(size: 16, weight: .regular))
                    .foregroundStyle(DeevoColors.textSecondary)
            }
            .opacity(opacity)
            .onAppear {
                withAnimation(.easeIn(duration: 0.4)) {
                    opacity = 1.0
                }
            }
        }
    }
}

#Preview {
    LaunchScreenView()
}
