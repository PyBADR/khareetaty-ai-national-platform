import SwiftUI

// MARK: - Unified Error Presentation

/// Unified error presentation component for consistent error handling across the app
struct ErrorBanner: View {
    let error: AppError
    let onDismiss: (() -> Void)?
    let onRetry: (() -> Void)?
    
    init(error: AppError, onDismiss: (() -> Void)? = nil, onRetry: (() -> Void)? = nil) {
        self.error = error
        self.onDismiss = onDismiss
        self.onRetry = onRetry
    }
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: error.iconName)
                .foregroundStyle(error.color)
                .font(.title3)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(error.title)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.primary)
                Text(error.message)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }
            
            Spacer()
            
            if let onRetry = onRetry, error.isRetryable {
                Button("Retry") {
                    onRetry()
                }
                .font(.caption.weight(.medium))
                .foregroundStyle(DeevoColors.accent)
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
                .background(DeevoColors.accent.opacity(0.15))
                .cornerRadius(6)
            }
            
            if let onDismiss = onDismiss {
                Button {
                    onDismiss()
                } label: {
                    Image(systemName: "xmark")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .padding(12)
        .background(error.backgroundColor)
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(error.color.opacity(0.3), lineWidth: 1)
        )
    }
}

// MARK: - App Error

/// Unified error type for the app
struct AppError: Identifiable, Equatable {
    let id: String
    let type: ErrorType
    let title: String
    let message: String
    let underlyingError: String?
    let isRetryable: Bool
    
    init(
        id: String = UUID().uuidString,
        type: ErrorType,
        title: String,
        message: String,
        underlyingError: String? = nil,
        isRetryable: Bool = false
    ) {
        self.id = id
        self.type = type
        self.title = title
        self.message = message
        self.underlyingError = underlyingError
        self.isRetryable = isRetryable
    }
    
    var iconName: String {
        switch type {
        case .network: return "wifi.slash"
        case .sync: return "arrow.triangle.2.circlepath"
        case .validation: return "exclamationmark.triangle.fill"
        case .database: return "externaldrive.fill.badge.xmark"
        case .permission: return "lock.fill"
        case .server: return "server.rack"
        case .unknown: return "questionmark.circle.fill"
        }
    }
    
    var color: Color {
        switch type {
        case .network: return DeevoColors.error
        case .sync: return .orange
        case .validation: return .yellow
        case .database: return DeevoColors.error
        case .permission: return .purple
        case .server: return DeevoColors.error
        case .unknown: return .gray
        }
    }
    
    var backgroundColor: Color {
        color.opacity(0.1)
    }
    
    static func == (lhs: AppError, rhs: AppError) -> Bool {
        lhs.id == rhs.id
    }
}

enum ErrorType: String {
    case network
    case sync
    case validation
    case database
    case permission
    case server
    case unknown
}

// MARK: - Error Factory

extension AppError {
    static func network(message: String = "Please check your internet connection and try again.") -> AppError {
        AppError(
            type: .network,
            title: "Connection Error",
            message: message,
            isRetryable: true
        )
    }
    
    static func sync(message: String, isRetryable: Bool = true) -> AppError {
        AppError(
            type: .sync,
            title: "Sync Error",
            message: message,
            isRetryable: isRetryable
        )
    }
    
    static func validation(message: String) -> AppError {
        AppError(
            type: .validation,
            title: "Validation Error",
            message: message,
            isRetryable: false
        )
    }
    
    static func database(message: String) -> AppError {
        AppError(
            type: .database,
            title: "Database Error",
            message: message,
            isRetryable: false
        )
    }
    
    static func permission(message: String) -> AppError {
        AppError(
            type: .permission,
            title: "Permission Required",
            message: message,
            isRetryable: false
        )
    }
    
    static func server(message: String) -> AppError {
        AppError(
            type: .server,
            title: "Server Error",
            message: message,
            isRetryable: true
        )
    }
    
    static func from(_ error: Error) -> AppError {
        if let operationError = error as? OperationError {
            switch operationError {
            case .invalidPayload:
                return .validation(message: operationError.localizedDescription)
            case .networkUnavailable:
                return .network()
            case .serverError(let msg):
                return .server(message: msg)
            }
        }
        
        if let templateError = error as? TemplateLoaderError {
            return AppError(
                type: .database,
                title: "Template Error",
                message: templateError.localizedDescription,
                isRetryable: false
            )
        }
        
        // Check for common error patterns
        let nsError = error as NSError
        if nsError.domain == NSURLErrorDomain {
            return .network()
        }
        
        return AppError(
            type: .unknown,
            title: "Error",
            message: error.localizedDescription,
            underlyingError: String(describing: error),
            isRetryable: false
        )
    }
}

// MARK: - Error Presenter View Modifier

struct ErrorPresenter: ViewModifier {
    @Binding var error: AppError?
    let onRetry: (() -> Void)?
    
    func body(content: Content) -> some View {
        content
            .overlay(alignment: .top) {
                if let error = error {
                    ErrorBanner(
                        error: error,
                        onDismiss: { self.error = nil },
                        onRetry: onRetry
                    )
                    .padding()
                    .transition(.move(edge: .top).combined(with: .opacity))
                    .animation(.spring(response: 0.3), value: self.error)
                }
            }
    }
}

extension View {
    func errorPresenter(error: Binding<AppError?>, onRetry: (() -> Void)? = nil) -> some View {
        modifier(ErrorPresenter(error: error, onRetry: onRetry))
    }
}

// MARK: - Error Alert Modifier

struct ErrorAlert: ViewModifier {
    @Binding var error: AppError?
    let onRetry: (() -> Void)?
    
    func body(content: Content) -> some View {
        content
            .alert(
                error?.title ?? "Error",
                isPresented: Binding(
                    get: { error != nil },
                    set: { if !$0 { error = nil } }
                )
            ) {
                Button("OK", role: .cancel) {
                    error = nil
                }
                if let onRetry = onRetry, error?.isRetryable == true {
                    Button("Retry") {
                        error = nil
                        onRetry()
                    }
                }
            } message: {
                Text(error?.message ?? "An unknown error occurred.")
            }
    }
}

extension View {
    func errorAlert(error: Binding<AppError?>, onRetry: (() -> Void)? = nil) -> some View {
        modifier(ErrorAlert(error: error, onRetry: onRetry))
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: 20) {
        ErrorBanner(error: .network())
        ErrorBanner(error: .sync(message: "Failed to sync 3 items"))
        ErrorBanner(error: .validation(message: "Please fill in all required fields"))
        ErrorBanner(error: .database(message: "Could not save data"))
    }
    .padding()
}
