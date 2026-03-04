import SwiftUI

@main
struct DeevoSentinelApp: App {
    
    @StateObject private var appState = AppState()
    
    init() {
        // Initialize database
        do {
            try DatabaseManager.shared.setup()
        } catch {
            fatalError("Failed to initialize database: \(error)")
        }
        
        // Configure app appearance with Deevo theme
        configureAppearance()
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .tint(DeevoColors.accent)
        }
    }
    
    private func configureAppearance() {
        // Navigation bar appearance
        let navAppearance = UINavigationBarAppearance()
        navAppearance.configureWithOpaqueBackground()
        navAppearance.backgroundColor = UIColor(DeevoColors.backgroundDark)
        navAppearance.titleTextAttributes = [.foregroundColor: UIColor(DeevoColors.textPrimary)]
        navAppearance.largeTitleTextAttributes = [.foregroundColor: UIColor(DeevoColors.textPrimary)]
        UINavigationBar.appearance().standardAppearance = navAppearance
        UINavigationBar.appearance().scrollEdgeAppearance = navAppearance
        
        // Tab bar appearance
        let tabAppearance = UITabBarAppearance()
        tabAppearance.configureWithOpaqueBackground()
        tabAppearance.backgroundColor = UIColor(DeevoColors.backgroundDark)
        UITabBar.appearance().standardAppearance = tabAppearance
        UITabBar.appearance().scrollEdgeAppearance = tabAppearance
    }
}

// MARK: - App State

class AppState: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var authToken: String?
    
    init() {
        // Check for saved auth token
        if let token = UserDefaults.standard.string(forKey: "authToken") {
            self.authToken = token
            self.isAuthenticated = true
            Task {
                await APIService.shared.setAuthToken(token)
            }
        }
    }
    
    func login(token: String, user: User) {
        self.authToken = token
        self.currentUser = user
        self.isAuthenticated = true
        UserDefaults.standard.set(token, forKey: "authToken")
        Task {
            await APIService.shared.setAuthToken(token)
        }
    }
    
    func logout() {
        self.authToken = nil
        self.currentUser = nil
        self.isAuthenticated = false
        UserDefaults.standard.removeObject(forKey: "authToken")
        Task {
            await APIService.shared.setAuthToken(nil)
        }
    }
}

// MARK: - Content View

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Group {
            if appState.isAuthenticated {
                HomeView()
            } else {
                LoginView()
            }
        }
    }
}
