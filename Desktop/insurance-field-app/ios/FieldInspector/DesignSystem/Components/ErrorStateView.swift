import SwiftUI

// MARK: - Deevo Sentinel Error State View
// Used for displaying errors and failure states

public enum ErrorSeverity {
    case warning
    case error
    case critical
    
    var color: Color {
        switch self {
        case .warning: return DeevoColors.warning
        case .error: return DeevoColors.error
        case .critical: return DeevoColors.riskCritical
        }
    }
    
    var icon: String {
        switch self {
        case .warning: return "exclamationmark.triangle"
        case .error: return "xmark.circle"
        case .critical: return "exclamationmark.octagon"
        }
    }
}

public struct ErrorStateView: View {
    let title: String
    let message: String
    let severity: ErrorSeverity
    let retryTitle: String?
    let retryAction: (() -> Void)?
    let dismissTitle: String?
    let dismissAction: (() -> Void)?
    
    public init(
        title: String,
        message: String,
        severity: ErrorSeverity = .error,
        retryTitle: String? = "Try Again",
        retryAction: (() -> Void)? = nil,
        dismissTitle: String? = nil,
        dismissAction: (() -> Void)? = nil
    ) {
        self.title = title
        self.message = message
        self.severity = severity
        self.retryTitle = retryTitle
        self.retryAction = retryAction
        self.dismissTitle = dismissTitle
        self.dismissAction = dismissAction
    }
    
    public var body: some View {
        VStack(spacing: 24) {
            // Icon
            ZStack {
                Circle()
                    .fill(severity.color.opacity(0.15))
                    .frame(width: 100, height: 100)
                
                Image(systemName: severity.icon)
                    .font(.system(size: 44, weight: .light))
                    .foregroundColor(severity.color)
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
                    .lineLimit(4)
            }
            .padding(.horizontal, 32)
            
            // Actions
            VStack(spacing: 12) {
                if let retryTitle = retryTitle, let retryAction = retryAction {
                    PrimaryButton(retryTitle, icon: "arrow.clockwise", action: retryAction)
                        .frame(maxWidth: 200)
                }
                
                if let dismissTitle = dismissTitle, let dismissAction = dismissAction {
                    SecondaryButton(dismissTitle, action: dismissAction)
                        .frame(maxWidth: 200)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(40)
    }
}

// MARK: - Inline Error Banner

public struct ErrorBanner: View {
    let message: String
    let severity: ErrorSeverity
    let dismissAction: (() -> Void)?
    
    public init(
        message: String,
        severity: ErrorSeverity = .error,
        dismissAction: (() -> Void)? = nil
    ) {
        self.message = message
        self.severity = severity
        self.dismissAction = dismissAction
    }
    
    public var body: some View {
        HStack(spacing: 12) {
            Image(systemName: severity.icon)
                .font(.system(size: 18, weight: .medium))
                .foregroundColor(severity.color)
            
            Text(message)
                .font(DeevoTypography.bodyMedium)
                .foregroundColor(DeevoColors.textPrimary)
                .lineLimit(2)
            
            Spacer()
            
            if let dismissAction = dismissAction {
                Button(action: dismissAction) {
                    Image(systemName: "xmark")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(DeevoColors.textSecondary)
                }
            }
        }
        .padding(16)
        .background(severity.color.opacity(0.1))
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(severity.color.opacity(0.3), lineWidth: 1)
        )
        .cornerRadius(12)
    }
}

// MARK: - Preset Error States

extension ErrorStateView {
    /// Network error with custom message
    public static func networkError(message: String, retryAction: @escaping () -> Void) -> ErrorStateView {
        ErrorStateView(
            title: "Connection Failed",
            message: message,
            severity: .error,
            retryAction: retryAction
        )
    }
    
    /// Network error with default message
    public static func networkError(retryAction: @escaping () -> Void) -> ErrorStateView {
        ErrorStateView(
            title: "Connection Failed",
            message: "Unable to connect to the server. Please check your internet connection and try again.",
            severity: .error,
            retryAction: retryAction
        )
    }
    
    /// Server error
    public static func serverError(retryAction: @escaping () -> Void) -> ErrorStateView {
        ErrorStateView(
            title: "Server Error",
            message: "Something went wrong on our end. Our team has been notified. Please try again later.",
            severity: .error,
            retryAction: retryAction
        )
    }
    
    /// Authentication error
    public static func authError(loginAction: @escaping () -> Void) -> ErrorStateView {
        ErrorStateView(
            title: "Session Expired",
            message: "Your session has expired. Please log in again to continue.",
            severity: .warning,
            retryTitle: "Log In",
            retryAction: loginAction
        )
    }
    
    /// Sync error
    public static func syncError(retryAction: @escaping () -> Void) -> ErrorStateView {
        ErrorStateView(
            title: "Sync Failed",
            message: "Some items could not be synchronized. Your data is saved locally and will sync when the connection is restored.",
            severity: .warning,
            retryAction: retryAction
        )
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: 24) {
        ErrorBanner(
            message: "Failed to load claim details",
            severity: .error,
            dismissAction: { print("Dismiss") }
        )
        .padding(.horizontal)
        
        ErrorBanner(
            message: "3 items pending sync",
            severity: .warning
        )
        .padding(.horizontal)
        
        Spacer()
        
        ErrorStateView(
            title: "Something Went Wrong",
            message: "We couldn't load your claims. Please check your connection and try again.",
            severity: .error,
            retryAction: { print("Retry") },
            dismissTitle: "Go Back",
            dismissAction: { print("Dismiss") }
        )
    }
    .background(DeevoColors.backgroundDark)
}
