import SwiftUI

// MARK: - Deevo Sentinel Secondary Button
// Used for secondary actions, cancel buttons, and alternative options

public struct SecondaryButton: View {
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
                        .progressViewStyle(CircularProgressViewStyle(tint: DeevoColors.accent))
                        .scaleEffect(0.8)
                } else {
                    if let icon = icon {
                        Image(systemName: icon)
                            .font(.system(size: 16, weight: .medium))
                    }
                    Text(title)
                        .font(DeevoTypography.labelLarge)
                        .fontWeight(.medium)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .background(Color.clear)
            .foregroundColor(isDisabled ? DeevoColors.textTertiary : DeevoColors.accent)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(isDisabled ? DeevoColors.textTertiary : DeevoColors.accent, lineWidth: 1.5)
            )
            .cornerRadius(12)
        }
        .disabled(isDisabled || isLoading)
        .animation(.easeInOut(duration: 0.2), value: isLoading)
        .animation(.easeInOut(duration: 0.2), value: isDisabled)
    }
}

// MARK: - Secondary Button Variants

public struct SecondaryButtonSmall: View {
    let title: String
    let icon: String?
    let action: () -> Void
    
    public init(
        _ title: String,
        icon: String? = nil,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.icon = icon
        self.action = action
    }
    
    public var body: some View {
        Button(action: action) {
            HStack(spacing: 6) {
                if let icon = icon {
                    Image(systemName: icon)
                        .font(.system(size: 14, weight: .medium))
                }
                Text(title)
                    .font(DeevoTypography.labelMedium)
                    .fontWeight(.medium)
            }
            .padding(.horizontal, 16)
            .frame(height: 36)
            .background(Color.clear)
            .foregroundColor(DeevoColors.accent)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(DeevoColors.accent, lineWidth: 1)
            )
        }
    }
}

// MARK: - Destructive Button

public struct DestructiveButton: View {
    let title: String
    let icon: String?
    let action: () -> Void
    
    public init(
        _ title: String,
        icon: String? = nil,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.icon = icon
        self.action = action
    }
    
    public var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                if let icon = icon {
                    Image(systemName: icon)
                        .font(.system(size: 16, weight: .medium))
                }
                Text(title)
                    .font(DeevoTypography.labelLarge)
                    .fontWeight(.medium)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .background(DeevoColors.error.opacity(0.15))
            .foregroundColor(DeevoColors.error)
            .cornerRadius(12)
        }
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: 20) {
        SecondaryButton("Cancel", icon: "xmark") {
            print("Tapped")
        }
        
        SecondaryButton("Loading...", isLoading: true) {
            print("Tapped")
        }
        
        SecondaryButton("Disabled", isDisabled: true) {
            print("Tapped")
        }
        
        SecondaryButtonSmall("Edit", icon: "pencil") {
            print("Tapped")
        }
        
        DestructiveButton("Delete Claim", icon: "trash") {
            print("Tapped")
        }
    }
    .padding()
    .background(DeevoColors.backgroundDark)
}
