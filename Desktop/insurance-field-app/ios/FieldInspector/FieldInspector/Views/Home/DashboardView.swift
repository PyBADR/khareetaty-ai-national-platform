import SwiftUI

/// ION-style 6-tile dashboard for DEEVO Field Inspector
/// Matches the ION app dashboard layout with Outbox, Forms, Drafts, Sent, Inbox, Search tiles
struct DashboardView: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var syncService = SyncService.shared
    
    // Navigation state
    @State private var navigateToOutbox = false
    @State private var navigateToForms = false
    @State private var navigateToDrafts = false
    @State private var navigateToSent = false
    @State private var navigateToInbox = false
    @State private var navigateToSearch = false
    
    // Tile counts (would be fetched from database)
    @State private var outboxCount = 0
    @State private var formsCount = 13
    @State private var draftsCount = 0
    @State private var sentCount = 0
    @State private var inboxCount = 12
    
    private let columns = [
        GridItem(.flexible(), spacing: 16),
        GridItem(.flexible(), spacing: 16),
        GridItem(.flexible(), spacing: 16)
    ]
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Header
                    headerSection
                    
                    // 6-tile grid
                    tilesGrid
                    
                    // Recent Activity
                    recentActivitySection
                    
                    // AI Advisory Signal
                    aiAdvisorySection
                }
                .padding(24)
            }
            .background(DeevoColors.backgroundDark)
            .navigationTitle("")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Text("DEEVO Field Inspector")
                        .font(.headline)
                        .foregroundStyle(.white)
                }
                ToolbarItem(placement: .topBarTrailing) {
                    HStack(spacing: 16) {
                        Button(action: {}) {
                            Image(systemName: "gearshape.fill")
                                .foregroundStyle(DeevoColors.textSecondary)
                        }
                        Button(action: {}) {
                            Image(systemName: "person.circle.fill")
                                .foregroundStyle(DeevoColors.textSecondary)
                        }
                        Button(action: {}) {
                            Image(systemName: "bell.fill")
                                .foregroundStyle(DeevoColors.textSecondary)
                        }
                    }
                }
            }
            .toolbarBackground(DeevoColors.primary, for: .navigationBar)
            .toolbarBackground(.visible, for: .navigationBar)
        }
    }
    
    // MARK: - Header Section
    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(greeting)
                .font(.title2)
                .fontWeight(.semibold)
                .foregroundStyle(.white)
            
            HStack(spacing: 8) {
                Text("GIG Takaful Kuwait")
                    .font(.subheadline)
                    .foregroundStyle(DeevoColors.textSecondary)
                
                Text("·")
                    .foregroundStyle(DeevoColors.textTertiary)
                
                Text("Sync: 2 min ago")
                    .font(.subheadline)
                    .foregroundStyle(DeevoColors.textSecondary)
                
                // Online indicator
                HStack(spacing: 4) {
                    Circle()
                        .fill(syncService.isOnline ? DeevoColors.success : DeevoColors.textTertiary)
                        .frame(width: 8, height: 8)
                    Text(syncService.isOnline ? "Online" : "Offline")
                        .font(.subheadline)
                        .foregroundStyle(syncService.isOnline ? DeevoColors.success : DeevoColors.textTertiary)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
    
    private var greeting: String {
        let hour = Calendar.current.component(.hour, from: Date())
        let name = appState.currentUser?.fullName.components(separatedBy: " ").first ?? "Inspector"
        
        switch hour {
        case 0..<12:
            return "Good morning, \(name)"
        case 12..<17:
            return "Good afternoon, \(name)"
        default:
            return "Good evening, \(name)"
        }
    }
    
    // MARK: - Tiles Grid
    private var tilesGrid: some View {
        LazyVGrid(columns: columns, spacing: 16) {
            // Row 1
            DashboardTile(
                title: "Outbox",
                count: outboxCount,
                icon: "tray.and.arrow.up.fill",
                iconColor: .orange,
                isUrgent: outboxCount > 0
            ) {
                navigateToOutbox = true
            }
            
            DashboardTile(
                title: "Forms",
                count: formsCount,
                icon: "doc.text.fill",
                iconColor: .blue
            ) {
                navigateToForms = true
            }
            
            DashboardTile(
                title: "Drafts",
                count: draftsCount,
                icon: "pencil.and.outline",
                iconColor: .yellow
            ) {
                navigateToDrafts = true
            }
            
            // Row 2
            DashboardTile(
                title: "Sent",
                count: sentCount,
                icon: "checkmark.circle.fill",
                iconColor: .green
            ) {
                navigateToSent = true
            }
            
            DashboardTile(
                title: "Inbox",
                count: inboxCount,
                icon: "tray.fill",
                iconColor: .blue,
                showBadge: inboxCount > 0
            ) {
                navigateToInbox = true
            }
            
            DashboardTile(
                title: "Search",
                count: nil,
                icon: "magnifyingglass",
                iconColor: DeevoColors.textTertiary
            ) {
                navigateToSearch = true
            }
        }
    }
    
    // MARK: - Recent Activity Section
    private var recentActivitySection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recent Activity")
                .font(.headline)
                .foregroundStyle(.white)
            
            VStack(spacing: 8) {
                RecentActivityRow(
                    claimNumber: "FI-260227-A001",
                    claimType: "Motor Accident",
                    status: .inProgress
                )
                
                RecentActivityRow(
                    claimNumber: "FI-260223-B002",
                    claimType: "Theft Claim",
                    status: .review
                )
                
                RecentActivityRow(
                    claimNumber: "FI-260220-C003",
                    claimType: "Fire Damage",
                    status: .submitted
                )
            }
        }
        .padding(16)
        .background(DeevoColors.surface)
        .cornerRadius(12)
    }
    
    // MARK: - AI Advisory Section
    private var aiAdvisorySection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("AI Advisory Signal")
                .font(.headline)
                .foregroundStyle(.white)
            
            HStack(spacing: 12) {
                Image(systemName: "exclamationmark.triangle.fill")
                    .foregroundStyle(DeevoColors.warning)
                    .font(.title3)
                
                Text("1 claim flagged for consistency review")
                    .font(.subheadline)
                    .foregroundStyle(DeevoColors.textSecondary)
                
                Spacer()
                
                Button("View") {
                    // Navigate to flagged claims
                }
                .font(.subheadline.weight(.medium))
                .foregroundStyle(DeevoColors.accent)
            }
            .padding(12)
            .background(DeevoColors.warning.opacity(0.1))
            .cornerRadius(8)
        }
        .padding(16)
        .background(DeevoColors.surface)
        .cornerRadius(12)
    }
}

// MARK: - Dashboard Tile Component
struct DashboardTile: View {
    let title: String
    let count: Int?
    let icon: String
    let iconColor: Color
    var isUrgent: Bool = false
    var showBadge: Bool = false
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 12) {
                ZStack(alignment: .topTrailing) {
                    Image(systemName: icon)
                        .font(.system(size: 32))
                        .foregroundStyle(iconColor)
                    
                    // Badge for counts > 0
                    if showBadge, let count = count, count > 0 {
                        Text("\(count)")
                            .font(.caption2.weight(.bold))
                            .foregroundStyle(.white)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Color.red)
                            .clipShape(Capsule())
                            .offset(x: 8, y: -8)
                    }
                }
                
                Text(title)
                    .font(.subheadline.weight(.medium))
                    .foregroundStyle(.white)
                
                if let count = count {
                    Text("\(count)")
                        .font(.title.weight(.bold))
                        .foregroundStyle(isUrgent ? .orange : .white)
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 24)
            .background(DeevoColors.surface)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(DeevoColors.border, lineWidth: 1)
            )
            .cornerRadius(12)
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Recent Activity Row
struct RecentActivityRow: View {
    let claimNumber: String
    let claimType: String
    let status: ClaimStatus
    
    enum ClaimStatus {
        case inProgress, review, submitted, complete
        
        var label: String {
            switch self {
            case .inProgress: return "IN PROGRESS"
            case .review: return "REVIEW"
            case .submitted: return "SUBMITTED"
            case .complete: return "COMPLETE"
            }
        }
        
        var color: Color {
            switch self {
            case .inProgress: return .blue
            case .review: return .orange
            case .submitted: return .purple
            case .complete: return .green
            }
        }
    }
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(claimNumber)
                    .font(.subheadline.weight(.medium))
                    .foregroundStyle(.white)
                
                Text(claimType)
                    .font(.caption)
                    .foregroundStyle(DeevoColors.textSecondary)
            }
            
            Spacer()
            
            Text(status.label)
                .font(.caption.weight(.semibold))
                .foregroundStyle(status.color)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(status.color.opacity(0.15))
                .cornerRadius(4)
        }
        .padding(.vertical, 8)
    }
}

#Preview {
    DashboardView()
        .environmentObject(AppState())
}
