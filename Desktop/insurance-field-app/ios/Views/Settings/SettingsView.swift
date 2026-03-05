import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var appState: AppState
    
    @State private var apiBaseURL = "http://localhost:3000/api"
    @State private var environment = "Development"
    @State private var showDebugLogs = false
    @State private var showLogoutAlert = false
    @State private var showClearDataAlert = false
    
    var body: some View {
        Form {
            // User Info
            if let user = appState.currentUser {
                Section("Account") {
                    HStack {
                        ZStack {
                            Circle()
                                .fill(DeevoColors.primary)
                                .frame(width: 50, height: 50)
                            Text(user.initials)
                                .font(.headline)
                                .foregroundColor(.white)
                        }
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(user.fullName)
                                .font(.headline)
                            Text(user.email)
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                            Text(user.role.displayName)
                                .font(.caption)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 2)
                                .background(DeevoColors.secondary.opacity(0.1))
                                .foregroundColor(DeevoColors.secondary)
                                .cornerRadius(4)
                        }
                    }
                    .padding(.vertical, 8)
                }
            }
            
            // API Configuration
            Section("API Configuration") {
                TextField("API Base URL", text: $apiBaseURL)
                    .textContentType(.URL)
                    .autocapitalization(.none)
                
                Picker("Environment", selection: $environment) {
                    Text("Development").tag("Development")
                    Text("Staging").tag("Staging")
                    Text("Production").tag("Production")
                }
            }
            
            // Debug
            Section("Debug") {
                Toggle("Show Debug Logs", isOn: $showDebugLogs)
                
                NavigationLink("View Logs") {
                    DebugLogsView()
                }
                
                Button("Test API Connection") {
                    testAPIConnection()
                }
            }
            
            // Privacy & Security
            Section("Privacy & Security") {
                PrivacyModeToggle()
                
                NavigationLink("Security Settings") {
                    PrivacySettingsView()
                }
            }
            
            // Data Management
            Section("Data Management") {
                Button("Clear Local Cache") {
                    showClearDataAlert = true
                }
                .foregroundColor(DeevoColors.accent)
                
                LabeledContent("Database Size", value: "12.4 MB")
                LabeledContent("Media Cache", value: "45.2 MB")
            }
            
            // App Info
            Section("About") {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Deevo Sentinel")
                        .font(.headline)
                        .foregroundColor(DeevoColors.primary)
                    Text("Sovereign Claims Decision Infrastructure")
                        .font(.subheadline)
                        .foregroundColor(DeevoColors.secondary)
                }
                .padding(.vertical, 4)
                
                LabeledContent("Version", value: "1.0.0")
                LabeledContent("Build", value: "2026.03.03")
                
                Link("Privacy Policy", destination: URL(string: "https://deevo.ai/privacy")!)
                Link("Terms of Service", destination: URL(string: "https://deevo.ai/terms")!)
            }
            
            // Branding Footer
            Section {
                HStack {
                    Spacer()
                    VStack(spacing: 4) {
                        Text("Powered by")
                            .font(.caption2)
                            .foregroundColor(DeevoColors.textTertiary)
                        Text("Deevo Analytics")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(DeevoColors.accent)
                    }
                    Spacer()
                }
                .padding(.vertical, 8)
            }
            
            // Logout
            Section {
                Button("Sign Out") {
                    showLogoutAlert = true
                }
                .foregroundColor(.red)
            }
        }
        .navigationTitle("Settings")
        .alert("Sign Out", isPresented: $showLogoutAlert) {
            Button("Cancel", role: .cancel) {}
            Button("Sign Out", role: .destructive) {
                appState.logout()
            }
        } message: {
            Text("Are you sure you want to sign out? Any unsynced data will be preserved.")
        }
        .alert("Clear Local Cache", isPresented: $showClearDataAlert) {
            Button("Cancel", role: .cancel) {}
            Button("Clear", role: .destructive) {
                clearLocalCache()
            }
        } message: {
            Text("This will clear all cached data. Unsynced changes will NOT be deleted.")
        }
    }
    
    private func testAPIConnection() {
        Task {
            do {
                _ = try await APIService.shared.getCurrentUser()
                // Show success
            } catch {
                // Show error
            }
        }
    }
    
    private func clearLocalCache() {
        // Clear cache implementation
    }
}

// MARK: - Debug Logs View

struct DebugLogsView: View {
    @State private var logs: [LogEntry] = []
    
    var body: some View {
        List {
            ForEach(logs) { log in
                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text(log.level.rawValue.uppercased())
                            .font(.caption)
                            .fontWeight(.bold)
                            .foregroundColor(log.level.color)
                        
                        Spacer()
                        
                        Text(log.timestamp.formatted(date: .omitted, time: .standard))
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                    
                    Text(log.message)
                        .font(.caption)
                        .foregroundColor(.primary)
                }
                .padding(.vertical, 4)
            }
        }
        .navigationTitle("Debug Logs")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button("Clear") {
                    logs = []
                }
            }
        }
        .onAppear {
            loadLogs()
        }
    }
    
    private func loadLogs() {
        // Sample logs
        logs = [
            LogEntry(level: .info, message: "App launched", timestamp: Date().addingTimeInterval(-3600)),
            LogEntry(level: .info, message: "User logged in: john.smith@fieldinsurance.com", timestamp: Date().addingTimeInterval(-3500)),
            LogEntry(level: .debug, message: "Fetching claims from API", timestamp: Date().addingTimeInterval(-3400)),
            LogEntry(level: .info, message: "Loaded 5 claims", timestamp: Date().addingTimeInterval(-3300)),
            LogEntry(level: .warning, message: "Network latency high: 2.3s", timestamp: Date().addingTimeInterval(-1800)),
            LogEntry(level: .error, message: "Failed to upload media: timeout", timestamp: Date().addingTimeInterval(-900)),
            LogEntry(level: .info, message: "Sync completed: 3 items", timestamp: Date().addingTimeInterval(-300)),
        ]
    }
}

// MARK: - Log Entry

struct LogEntry: Identifiable {
    let id = UUID()
    let level: LogLevel
    let message: String
    let timestamp: Date
}

enum LogLevel: String {
    case debug, info, warning, error
    
    var color: Color {
        switch self {
        case .debug: return .gray
        case .info: return DeevoColors.secondary
        case .warning: return .orange
        case .error: return .red
        }
    }
}

#Preview {
    NavigationStack {
        SettingsView()
            .environmentObject(AppState())
    }
}
