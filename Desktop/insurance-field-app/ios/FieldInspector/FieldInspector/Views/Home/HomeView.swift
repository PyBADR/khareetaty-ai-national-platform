import SwiftUI

struct HomeView: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var syncService = SyncService.shared
    
    @State private var selectedTab = 0
    
    var body: some View {
        NavigationSplitView {
            // Sidebar
            List {
                // Claims section
                Button(action: { selectedTab = 0 }) {
                    Label("Inbox", systemImage: "tray.fill")
                }
                .listRowBackground(selectedTab == 0 ? Color.accentColor.opacity(0.2) : Color.clear)
                
                Button(action: { selectedTab = 1 }) {
                    Label("My Claims", systemImage: "person.fill")
                }
                .listRowBackground(selectedTab == 1 ? Color.accentColor.opacity(0.2) : Color.clear)
                
                // Sync section
                Button(action: { selectedTab = 2 }) {
                    HStack {
                        Label("Outbox", systemImage: "arrow.up.circle")
                        Spacer()
                        if syncService.syncState.pendingCount > 0 {
                            Text("\(syncService.syncState.pendingCount)")
                                .font(.caption)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 2)
                                .background(DeevoColors.accent)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                        }
                    }
                }
                .listRowBackground(selectedTab == 2 ? Color.accentColor.opacity(0.2) : Color.clear)
                
                // Tools section
                Button(action: { selectedTab = 3 }) {
                    Label("Templates", systemImage: "doc.text.fill")
                }
                .listRowBackground(selectedTab == 3 ? Color.accentColor.opacity(0.2) : Color.clear)
                
                Button(action: { selectedTab = 4 }) {
                    Label("Search", systemImage: "magnifyingglass")
                }
                .listRowBackground(selectedTab == 4 ? Color.accentColor.opacity(0.2) : Color.clear)
                
                // Executive Dashboard
                Button(action: { selectedTab = 6 }) {
                    Label("Dashboard", systemImage: "chart.bar.fill")
                }
                .listRowBackground(selectedTab == 6 ? Color.accentColor.opacity(0.2) : Color.clear)
                
                // Regulatory Export
                Button(action: { selectedTab = 7 }) {
                    Label("Export", systemImage: "square.and.arrow.up")
                }
                .listRowBackground(selectedTab == 7 ? Color.accentColor.opacity(0.2) : Color.clear)
                
                // Settings
                Button(action: { selectedTab = 5 }) {
                    Label("Settings", systemImage: "gear")
                }
                .listRowBackground(selectedTab == 5 ? Color.accentColor.opacity(0.2) : Color.clear)
            }
            .listStyle(.sidebar)
            .navigationTitle("Deevo Sentinel")
            .toolbar {
                ToolbarItem(placement: .bottomBar) {
                    HStack {
                        // Sync status indicator
                        if syncService.syncState.isSyncing {
                            ProgressView()
                                .scaleEffect(0.8)
                            Text("Syncing...")
                                .font(.caption)
                        } else if !syncService.isOnline {
                            Image(systemName: "wifi.slash")
                                .foregroundColor(DeevoColors.accent)
                            Text("Offline")
                                .font(.caption)
                                .foregroundColor(DeevoColors.accent)
                        } else {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(DeevoColors.success)
                            Text("Online")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        
                        Spacer()
                        
                        // User info
                        if let user = appState.currentUser {
                            Text(user.fullName)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }
            }
        } detail: {
            // Detail view based on selection
            switch selectedTab {
            case 0:
                ClaimInboxView(showAssignedOnly: false)
            case 1:
                ClaimInboxView(showAssignedOnly: true)
            case 2:
                OutboxView()
            case 3:
                TemplatesView()
            case 4:
                SearchView()
            case 5:
                SettingsView()
            case 6:
                ExecutiveDashboardView()
            case 7:
                RegulatoryExportView()
            default:
                ClaimInboxView(showAssignedOnly: false)
            }
        }
    }
}

#Preview {
    HomeView()
        .environmentObject(AppState())
}
