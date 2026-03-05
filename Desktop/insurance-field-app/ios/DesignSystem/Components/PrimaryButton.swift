import SwiftUI

// MARK: - Deevo Sentinel Primary Button
// Used for main CTAs and primary actions

public struct PrimaryButton: View {
    let title: String
    let icon: String?
    let isLoading: Bool
    let isDisabled: Bool
    let action: () -> Void
    
    public init(
        _ title: String,
        icon: String? = nil,
        isLoading: Bool = false,
        isDisabled: Bool = false,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.icon = icon
        self.isLoading = isLoading
        self.isDisabled = isDisabled
        self.action = action
    }
    
    public var body: some View {
        Button(action: {
            if !isLoading && !isDisabled {
                action()
            }
        }) {
            HStack(spacing: 8) {
                if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: DeevoColors.primary))
                        .scaleEffect(0.8)
                } else {
                    if let icon = icon {
                        Image(systemName: icon)
                            .font(.system(size: 16, weight: .semibold))
                    }
                    Text(title)
                        .font(DeevoTypography.labelLarge)
                        .fontWeight(.semibold)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .background(isDisabled ? DeevoColors.textTertiary : DeevoColors.accent)
            .foregroundColor(isDisabled ? DeevoColors.textSecondary : DeevoColors.primary)
            .cornerRadius(12)
        }
        .disabled(isDisabled || isLoading)
        .animation(.easeInOut(duration: 0.2), value: isLoading)
        .animation(.easeInOut(duration: 0.2), value: isDisabled)
    }
}

// MARK: - Primary Button Variants

public struct PrimaryButtonSmall: View {
    let title: String
    let icon: String?
    let isLoading: Bool
    let action: () -> Void
    
    public init(
        _ title: String,
        icon: String? = nil,
        isLoading: Bool = false,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.icon = icon
        self.isLoading = isLoading
        self.action = action
    }
    
    public var body: some View {
        Button(action: action) {
            HStack(spacing: 6) {
                if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: DeevoColors.primary))
                        .scaleEffect(0.7)
                } else {
                    if let icon = icon {
                        Image(systemName: icon)
                            .font(.system(size: 14, weight: .semibold))
                    }
                    Text(title)
                        .font(DeevoTypography.labelMedium)
                        .fontWeight(.semibold)
                }
            }
            .padding(.horizontal, 16)
            .frame(height: 36)
            .background(DeevoColors.accent)
            .foregroundColor(DeevoColors.primary)
            .cornerRadius(8)
        }
        .disabled(isLoading)
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: 20) {
        PrimaryButton("Submit Claim", icon: "checkmark.circle") {
            print("Tapped")
        }
        
        PrimaryButton("Loading...", isLoading: true) {
            print("Tapped")
        }
        
        PrimaryButton("Disabled", isDisabled: true) {
            print("Tapped")
        }
        
        PrimaryButtonSmall("Quick Action", icon: "bolt") {
            print("Tapped")
        }
    }
    .padding()
    .background(DeevoColors.backgroundDark)
}
