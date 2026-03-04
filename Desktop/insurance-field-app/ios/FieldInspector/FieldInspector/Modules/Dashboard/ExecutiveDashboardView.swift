import SwiftUI
import GRDB

// MARK: - Dashboard Models

struct DashboardMetrics: Equatable {
    var totalClaims: Int = 0
    var pendingSync: Int = 0
    var aiApproved: Int = 0
    var aiDenied: Int = 0
    var aiPending: Int = 0
    var lowRisk: Int = 0
    var moderateRisk: Int = 0
    var elevatedRisk: Int = 0
    var criticalRisk: Int = 0
    var last24HourActivity: Int = 0
    var statusBreakdown: [ClaimStatus: Int] = [:]
}

struct ActivityItem: Identifiable {
    let id: String
    let claimNumber: String
    let action: String
    let timestamp: Date
    let userName: String
}

// MARK: - Executive Dashboard View

struct ExecutiveDashboardView: View {
    @StateObject private var viewModel = ExecutiveDashboardViewModel()
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Header
                    dashboardHeader
                    
                    // Key Metrics Row
                    keyMetricsSection
                    
                    // AI Decision Breakdown
                    aiDecisionSection
                    
                    // Risk Distribution
                    riskDistributionSection
                    
                    // Status Chart
                    statusChartSection
                    
                    // Recent Activity
                    recentActivitySection
                }
                .padding()
            }
            .background(DeevoColors.backgroundDark.ignoresSafeArea())
            .navigationTitle("Executive Dashboard")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: { viewModel.refresh() }) {
                        Image(systemName: "arrow.clockwise")
                            .foregroundColor(DeevoColors.accent)
                    }
                }
            }
            .refreshable {
                await viewModel.refreshAsync()
            }
        }
        .onAppear {
            viewModel.loadMetrics()
        }
    }
    
    // MARK: - Dashboard Header
    
    private var dashboardHeader: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Deevo Sentinel")
                    .font(DeevoTypography.displayMedium)
                    .foregroundColor(DeevoColors.textPrimary)
                Text("Claims Intelligence Overview")
                    .font(DeevoTypography.bodyMedium)
                    .foregroundColor(DeevoColors.textSecondary)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 4) {
                Text(Date(), style: .date)
                    .font(DeevoTypography.labelMedium)
                    .foregroundColor(DeevoColors.textSecondary)
                Text("Last updated: \(viewModel.lastUpdated, style: .time)")
                    .font(DeevoTypography.labelSmall)
                    .foregroundColor(DeevoColors.textTertiary)
            }
        }
        .padding()
        .background(DeevoColors.surfaceElevated)
        .cornerRadius(12)
    }
    
    // MARK: - Key Metrics Section
    
    private var keyMetricsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Key Metrics")
                .font(DeevoTypography.headlineMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 16) {
                MetricCard(
                    title: "Total Claims",
                    value: "\(viewModel.metrics.totalClaims)",
                    icon: "doc.text.fill",
                    color: DeevoColors.secondary
                )
                
                MetricCard(
                    title: "Pending Sync",
                    value: "\(viewModel.metrics.pendingSync)",
                    icon: "arrow.triangle.2.circlepath",
                    color: viewModel.metrics.pendingSync > 0 ? DeevoColors.warning : DeevoColors.success
                )
                
                MetricCard(
                    title: "24h Activity",
                    value: "\(viewModel.metrics.last24HourActivity)",
                    icon: "clock.fill",
                    color: DeevoColors.accent
                )
                
                MetricCard(
                    title: "Critical Risk",
                    value: "\(viewModel.metrics.criticalRisk)",
                    icon: "exclamationmark.triangle.fill",
                    color: viewModel.metrics.criticalRisk > 0 ? DeevoColors.error : DeevoColors.success
                )
            }
        }
    }
    
    // MARK: - AI Decision Section
    
    private var aiDecisionSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("AI Decision Breakdown")
                .font(DeevoTypography.headlineMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            HStack(spacing: 16) {
                AIDecisionCard(
                    title: "Approved",
                    count: viewModel.metrics.aiApproved,
                    total: viewModel.metrics.totalClaims,
                    color: DeevoColors.success
                )
                
                AIDecisionCard(
                    title: "Denied",
                    count: viewModel.metrics.aiDenied,
                    total: viewModel.metrics.totalClaims,
                    color: DeevoColors.error
                )
                
                AIDecisionCard(
                    title: "Pending Review",
                    count: viewModel.metrics.aiPending,
                    total: viewModel.metrics.totalClaims,
                    color: DeevoColors.warning
                )
            }
        }
    }
    
    // MARK: - Risk Distribution Section
    
    private var riskDistributionSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Risk Distribution")
                .font(DeevoTypography.headlineMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            HStack(spacing: 12) {
                RiskBandCard(band: "Low", range: "0-30", count: viewModel.metrics.lowRisk, color: DeevoColors.success)
                RiskBandCard(band: "Moderate", range: "31-60", count: viewModel.metrics.moderateRisk, color: DeevoColors.warning)
                RiskBandCard(band: "Elevated", range: "61-80", count: viewModel.metrics.elevatedRisk, color: Color.orange)
                RiskBandCard(band: "Critical", range: "81-100", count: viewModel.metrics.criticalRisk, color: DeevoColors.error)
            }
        }
    }
    
    // MARK: - Status Chart Section
    
    private var statusChartSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Claims by Status")
                .font(DeevoTypography.headlineMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            SectionCard {
                VStack(spacing: 12) {
                    ForEach(ClaimStatus.allCases, id: \.self) { status in
                        StatusBarRow(
                            status: status,
                            count: viewModel.metrics.statusBreakdown[status] ?? 0,
                            total: viewModel.metrics.totalClaims
                        )
                    }
                }
                .padding()
            }
        }
    }
    
    // MARK: - Recent Activity Section
    
    private var recentActivitySection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("Recent Activity")
                    .font(DeevoTypography.headlineMedium)
                    .foregroundColor(DeevoColors.textPrimary)
                Spacer()
                Text("Last 24 hours")
                    .font(DeevoTypography.labelSmall)
                    .foregroundColor(DeevoColors.textTertiary)
            }
            
            SectionCard {
                if viewModel.recentActivity.isEmpty {
                    EmptyStateView(
                        icon: "clock",
                        title: "No Recent Activity",
                        message: "Activity from the last 24 hours will appear here"
                    )
                    .padding()
                } else {
                    LazyVStack(spacing: 8) {
                        ForEach(viewModel.recentActivity, id: \.id) { activity in
                            ActivityRow(activity: activity)
                        }
                    }
                    .padding(.vertical, 8)
                }
            }
        }
    }
}

// MARK: - Supporting Views

struct MetricCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 12) {
            HStack {
                Image(systemName: icon)
                    .font(.system(size: 20))
                    .foregroundColor(color)
                Spacer()
            }
            
            HStack {
                Text(value)
                    .font(DeevoTypography.displayLarge)
                    .foregroundColor(DeevoColors.textPrimary)
                Spacer()
            }
            
            HStack {
                Text(title)
                    .font(DeevoTypography.labelSmall)
                    .foregroundColor(DeevoColors.textSecondary)
                Spacer()
            }
        }
        .padding()
        .background(DeevoColors.surfaceElevated)
        .cornerRadius(12)
    }
}

struct AIDecisionCard: View {
    let title: String
    let count: Int
    let total: Int
    let color: Color
    
    private var percentage: Double {
        guard total > 0 else { return 0 }
        return Double(count) / Double(total) * 100
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Circle()
                    .fill(color)
                    .frame(width: 12, height: 12)
                Text(title)
                    .font(DeevoTypography.labelMedium)
                    .foregroundColor(DeevoColors.textSecondary)
            }
            
            Text("\(count)")
                .font(DeevoTypography.displayMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            Text(String(format: "%.1f%%", percentage))
                .font(DeevoTypography.labelSmall)
                .foregroundColor(color)
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(DeevoColors.surfaceElevated)
                        .frame(height: 6)
                        .cornerRadius(3)
                    
                    Rectangle()
                        .fill(color)
                        .frame(width: geometry.size.width * CGFloat(percentage / 100), height: 6)
                        .cornerRadius(3)
                }
            }
            .frame(height: 6)
        }
        .padding()
        .background(DeevoColors.surface)
        .cornerRadius(12)
    }
}

struct RiskBandCard: View {
    let band: String
    let range: String
    let count: Int
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Text("\(count)")
                .font(DeevoTypography.displayMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            Text(band)
                .font(DeevoTypography.labelMedium)
                .foregroundColor(color)
            
            Text(range)
                .font(DeevoTypography.labelSmall)
                .foregroundColor(DeevoColors.textTertiary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(DeevoColors.surface)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(color.opacity(0.3), lineWidth: 1)
                )
        )
    }
}

struct StatusBarRow: View {
    let status: ClaimStatus
    let count: Int
    let total: Int
    
    private var percentage: CGFloat {
        guard total > 0 else { return 0 }
        return CGFloat(count) / CGFloat(total)
    }
    
    var body: some View {
        VStack(spacing: 4) {
            HStack {
                Text(status.displayName)
                    .font(DeevoTypography.labelMedium)
                    .foregroundColor(DeevoColors.textPrimary)
                Spacer()
                Text("\(count)")
                    .font(DeevoTypography.labelMedium)
                    .foregroundColor(DeevoColors.textSecondary)
            }
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(DeevoColors.surfaceElevated)
                        .frame(height: 8)
                        .cornerRadius(4)
                    
                    Rectangle()
                        .fill(status.color)
                        .frame(width: geometry.size.width * percentage, height: 8)
                        .cornerRadius(4)
                }
            }
            .frame(height: 8)
        }
    }
}

struct ActivityRow: View {
    let activity: ActivityItem
    
    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(DeevoColors.accent.opacity(0.2))
                .frame(width: 40, height: 40)
                .overlay(
                    Image(systemName: "doc.text")
                        .foregroundColor(DeevoColors.accent)
                )
            
            VStack(alignment: .leading, spacing: 2) {
                Text(activity.claimNumber)
                    .font(DeevoTypography.labelMedium)
                    .foregroundColor(DeevoColors.textPrimary)
                Text(activity.action)
                    .font(DeevoTypography.bodySmall)
                    .foregroundColor(DeevoColors.textSecondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 2) {
                Text(activity.timestamp, style: .time)
                    .font(DeevoTypography.labelSmall)
                    .foregroundColor(DeevoColors.textTertiary)
                Text(activity.userName)
                    .font(DeevoTypography.labelSmall)
                    .foregroundColor(DeevoColors.textTertiary)
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
    }
}

// MARK: - View Model

@MainActor
class ExecutiveDashboardViewModel: ObservableObject {
    @Published var metrics = DashboardMetrics()
    @Published var recentActivity: [ActivityItem] = []
    @Published var lastUpdated = Date()
    @Published var isLoading = false
    
    func loadMetrics() {
        isLoading = true
        
        Task {
            do {
                let db = DatabaseManager.shared.database
                
                // Total claims
                let totalClaims = try await db.read { db in
                    try Claim.fetchCount(db)
                }
                
                // Pending sync
                let pendingSync = try await db.read { db in
                    try SyncQueueItem.filter(Column("status") == SyncStatus.pending.rawValue).fetchCount(db)
                }
                
                // AI decisions
                let aiApproved = try await db.read { db in
                    try Claim.filter(Column("aiDecision") == "approve").fetchCount(db)
                }
                let aiDenied = try await db.read { db in
                    try Claim.filter(Column("aiDecision") == "deny").fetchCount(db)
                }
                let aiPending = try await db.read { db in
                    try Claim.filter(Column("aiDecision") == nil || Column("aiDecision") == "review").fetchCount(db)
                }
                
                // Risk bands (using riskScore)
                let lowRisk = try await db.read { db in
                    try Claim.filter(Column("riskScore") >= 0 && Column("riskScore") <= 30).fetchCount(db)
                }
                let moderateRisk = try await db.read { db in
                    try Claim.filter(Column("riskScore") > 30 && Column("riskScore") <= 60).fetchCount(db)
                }
                let elevatedRisk = try await db.read { db in
                    try Claim.filter(Column("riskScore") > 60 && Column("riskScore") <= 80).fetchCount(db)
                }
                let criticalRisk = try await db.read { db in
                    try Claim.filter(Column("riskScore") > 80).fetchCount(db)
                }
                
                // 24h activity
                let yesterday = Calendar.current.date(byAdding: .hour, value: -24, to: Date()) ?? Date()
                let last24HourActivity = try await db.read { db in
                    try Claim.filter(Column("updatedAt") > yesterday).fetchCount(db)
                }
                
                // Status breakdown
                var statusBreakdown: [ClaimStatus: Int] = [:]
                for status in ClaimStatus.allCases {
                    let count = try await db.read { db in
                        try Claim.filter(Column("status") == status.rawValue).fetchCount(db)
                    }
                    statusBreakdown[status] = count
                }
                
                metrics = DashboardMetrics(
                    totalClaims: totalClaims,
                    pendingSync: pendingSync,
                    aiApproved: aiApproved,
                    aiDenied: aiDenied,
                    aiPending: aiPending,
                    lowRisk: lowRisk,
                    moderateRisk: moderateRisk,
                    elevatedRisk: elevatedRisk,
                    criticalRisk: criticalRisk,
                    last24HourActivity: last24HourActivity,
                    statusBreakdown: statusBreakdown
                )
                
                lastUpdated = Date()
                isLoading = false
            } catch {
                print("Error loading dashboard metrics: \(error)")
                isLoading = false
            }
        }
    }
    
    func refresh() {
        loadMetrics()
    }
    
    func refreshAsync() async {
        loadMetrics()
    }
}

// MARK: - Preview

#Preview {
    ExecutiveDashboardView()
}
