import SwiftUI
import Combine

// MARK: - Toast Message
struct ToastMessage: Identifiable, Equatable {
    let id = UUID()
    let type: ToastType
    let title: String
    let message: String
    let duration: TimeInterval
    
    init(type: ToastType, title: String, message: String = "", duration: TimeInterval = 3.0) {
        self.type = type
        self.title = title
        self.message = message
        self.duration = duration
    }
    
    static func == (lhs: ToastMessage, rhs: ToastMessage) -> Bool {
        lhs.id == rhs.id
    }
}

// MARK: - Toast Type
enum ToastType {
    case success
    case error
    case warning
    case info
    
    var color: Color {
        switch self {
        case .success: return .green
        case .error: return .red
        case .warning: return .orange
        case .info: return .blue
        }
    }
    
    var icon: String {
        switch self {
        case .success: return "checkmark.circle.fill"
        case .error: return "xmark.circle.fill"
        case .warning: return "exclamationmark.triangle.fill"
        case .info: return "info.circle.fill"
        }
    }
}

// MARK: - Toast Manager
class ToastManager: ObservableObject {
    static let shared = ToastManager()
    
    @Published var currentToast: ToastMessage?
    private var toastQueue: [ToastMessage] = []
    private var isShowingToast = false
    
    private init() {}
    
    // MARK: - Public Methods
    
    func success(_ title: String, message: String = "", duration: TimeInterval = 3.0) {
        show(ToastMessage(type: .success, title: title, message: message, duration: duration))
    }
    
    func error(_ title: String, message: String = "", duration: TimeInterval = 4.0) {
        show(ToastMessage(type: .error, title: title, message: message, duration: duration))
    }
    
    func warning(_ title: String, message: String = "", duration: TimeInterval = 3.5) {
        show(ToastMessage(type: .warning, title: title, message: message, duration: duration))
    }
    
    func info(_ title: String, message: String = "", duration: TimeInterval = 3.0) {
        show(ToastMessage(type: .info, title: title, message: message, duration: duration))
    }
    
    func dismiss() {
        withAnimation {
            currentToast = nil
            isShowingToast = false
            showNextToast()
        }
    }
    
    // MARK: - Private Methods
    
    private func show(_ toast: ToastMessage) {
        if isShowingToast {
            toastQueue.append(toast)
        } else {
            displayToast(toast)
        }
    }
    
    private func displayToast(_ toast: ToastMessage) {
        withAnimation {
            currentToast = toast
            isShowingToast = true
        }
        
        DispatchQueue.main.asyncAfter(deadline: .now() + toast.duration) { [weak self] in
            self?.dismiss()
        }
    }
    
    private func showNextToast() {
        guard !toastQueue.isEmpty else { return }
        let nextToast = toastQueue.removeFirst()
        displayToast(nextToast)
    }
}

// MARK: - Toast View
struct ToastView: View {
    let toast: ToastMessage
    let onDismiss: () -> Void
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: toast.type.icon)
                .font(.title2)
                .foregroundColor(.white)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(toast.title)
                    .font(.headline)
                    .foregroundColor(.white)
                
                if !toast.message.isEmpty {
                    Text(toast.message)
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.9))
                }
            }
            
            Spacer()
            
            Button(action: onDismiss) {
                Image(systemName: "xmark")
                    .font(.caption)
                    .foregroundColor(.white)
            }
        }
        .padding()
        .background(toast.type.color)
        .cornerRadius(12)
        .shadow(radius: 10)
        .padding(.horizontal)
    }
}

// MARK: - Toast Modifier
struct ToastModifier: ViewModifier {
    @ObservedObject var toastManager = ToastManager.shared
    
    func body(content: Content) -> some View {
        ZStack {
            content
            
            if let toast = toastManager.currentToast {
                VStack {
                    ToastView(toast: toast) {
                        toastManager.dismiss()
                    }
                    .transition(.move(edge: .top).combined(with: .opacity))
                    
                    Spacer()
                }
                .zIndex(999)
            }
        }
    }
}

extension View {
    func toast() -> some View {
        modifier(ToastModifier())
    }
}
