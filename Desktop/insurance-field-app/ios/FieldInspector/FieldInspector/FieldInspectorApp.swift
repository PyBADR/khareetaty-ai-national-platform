import SwiftUI

@main
struct DeevoSentinelApp: App {
    
    @StateObject private var appState = AppState()
    
    init() {
        // Validate configuration at launch
        Config.validate()
        
        // Print configuration in debug builds
        Config.printConfiguration()
        
        // Initialize database
        do {
            try DatabaseManager.shared.setup()
        } catch {
            AppLogger.critical("Failed to initialize database: \(error)")
            fatalError("Failed to initialize database: \(error)")
        }
        
        // Configure app appearance with Deevo theme
        configureAppearance()
        
        AppLogger.info("App initialized successfully", category: AppLogger.app)
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
        if let token = UserDefaults.standard.string(forKey: "authToken"),
           let refreshToken = UserDefaults.standard.string(forKey: "refreshToken") {
            self.authToken = token
            self.isAuthenticated = true
            Task {
                try? await APIService.shared.setAuthToken(token, refreshToken: refreshToken, expiresIn: 3600)
            }
        }
    }
    
    func login(token: String, refreshToken: String, expiresIn: Int, user: User) {
        self.authToken = token
        self.currentUser = user
        self.isAuthenticated = true
        UserDefaults.standard.set(token, forKey: "authToken")
        UserDefaults.standard.set(refreshToken, forKey: "refreshToken")
        Task {
            try? await APIService.shared.setAuthToken(token, refreshToken: refreshToken, expiresIn: expiresIn)
        }
    }
    
    func logout() {
        self.authToken = nil
        self.currentUser = nil
        self.isAuthenticated = false
        UserDefaults.standard.removeObject(forKey: "authToken")
        UserDefaults.standard.removeObject(forKey: "refreshToken")
        Task {
            try? await APIService.shared.clearAuthToken()
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
