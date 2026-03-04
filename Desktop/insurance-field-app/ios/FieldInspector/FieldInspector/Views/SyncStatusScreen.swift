// SyncStatusScreen.swift
// Real sync queue display using queued_operations as source of truth
// FieldInspector

import SwiftUI

struct SyncStatusScreen: View {
    @EnvironmentObject var syncService: SyncService
    @StateObject private var viewModel = SyncStatusViewModel()
    @State private var selectedTab: SyncTab = .operations
    
    enum SyncTab: String, CaseIterable {
        case operations = "QUEUE"
        case claims = "CLAIMS"
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Online/offline status bar
            OfflineBanner(isOnline: syncService.isOnline)
            
            // Tab switcher
            HStack(spacing: 0) {
                ForEach(SyncTab.allCases, id: \.self) { tab in
                    Button {
                        withAnimation(.easeInOut(duration: 0.15)) { selectedTab = tab }
                    } label: {
                        Text(tab.rawValue)
                            .font(.caption.weight(.bold))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(selectedTab == tab
                                ? DeevoColors.accent.opacity(0.15) : Color.clear)
                            .foregroundStyle(selectedTab == tab
                                ? DeevoColors.accent : Color.secondary)
                    }
                }
            }
            .background(DeevoColors.backgroundDark)
            .overlay(alignment: .bottom) {
                Rectangle().fill(DeevoColors.border).frame(height: 1)
            }
            
            // Content based on tab
            ScrollView {
                LazyVStack(spacing: 1) {
                    switch selectedTab {
                    case .operations:
                        operationsContent
                    case .claims:
                        claimsContent
                    }
                }
                .padding(.top, 1)
            }
            
            // Summary footer
            summaryFooter
        }
        .background(DeevoColors.backgroundDark)
        .navigationTitle("Sync Status")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    Task { await viewModel.syncAll() }
                } label: {
                    if viewModel.isSyncing {
                        ProgressView().scaleEffect(0.8)
                    } else {
                        Label("Sync All", systemImage: "arrow.triangle.2.circlepath")
                            .foregroundStyle(DeevoColors.accent)
                    }
                }
                .disabled(viewModel.isSyncing || !syncService.isOnline)
            }
        }
        .task {
            await viewModel.loadData()
        }
        .refreshable {
            await viewModel.loadData()
        }
    }
    
    // MARK: - Operations Content
    
    @ViewBuilder
    private var operationsContent: some View {
        if viewModel.operations.isEmpty {
            emptyStateView(
                icon: "checkmark.circle.fill",
                title: "All Synced",
                message: "No pending operations"
            )
        } else {
            ForEach(viewModel.operations) { operation in
                OperationRow(
                    operation: operation,
                    onRetry: {
                        Task { await viewModel.retryOperation(id: operation.id) }
                    }
                )
            }
        }
    }
    
    // MARK: - Claims Content
    
    @ViewBuilder
    private var claimsContent: some View {
        if viewModel.claimStatuses.isEmpty {
            emptyStateView(
                icon: "doc.text",
                title: "No Claims",
                message: "No claims with sync status"
            )
        } else {
            ForEach(viewModel.claimStatuses) { status in
                ClaimSyncRow(status: status)
            }
        }
    }
    
    // MARK: - Summary Footer
    
    private var summaryFooter: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text("Pending: \(viewModel.pendingCount)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text("Failed: \(viewModel.failedCount)")
                    .font(.caption)
                    .foregroundStyle(viewModel.failedCount > 0 ? .red : .secondary)
            }
            
            Spacer()
            
            if viewModel.failedCount > 0 {
                Button("Retry All Failed") {
                    Task { await viewModel.retryAllFailed() }
                }
                .font(.caption.weight(.medium))
                .foregroundStyle(DeevoColors.accent)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(DeevoColors.accent.opacity(0.15))
                .cornerRadius(6)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(DeevoColors.surface)
    }
    
    // MARK: - Empty State
    
    private func emptyStateView(icon: String, title: String, message: String) -> some View {
        VStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 48))
                .foregroundStyle(DeevoColors.success)
            Text(title)
                .font(.headline)
            Text(message)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 60)
    }
}

// MARK: - Offline Banner

struct OfflineBanner: View {
    let isOnline: Bool
    
    var body: some View {
        HStack(spacing: 8) {
            Circle()
                .fill(isOnline ? DeevoColors.success : DeevoColors.error)
                .frame(width: 8, height: 8)
            Text(isOnline ? "Online · Auto-sync enabled" : "Offline · Will sync when connected")
                .font(.caption)
                .foregroundStyle(.secondary)
            Spacer()
            if !isOnline {
                Image(systemName: "wifi.slash")
                    .foregroundStyle(DeevoColors.error)
                    .font(.caption)
            }
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 10)
        .background(isOnline ? DeevoColors.surface : DeevoColors.error.opacity(0.1))
    }
}

// MARK: - Operation Row

struct OperationRow: View {
    let operation: QueuedOperation
    let onRetry: () -> Void
    
    var body: some View {
        HStack(spacing: 12) {
            // Icon
            RoundedRectangle(cornerRadius: 8)
                .fill(DeevoColors.surfaceElevated)
                .frame(width: 52, height: 52)
                .overlay(
                    Image(systemName: iconName)
                        .foregroundStyle(iconColor)
                )
            
            // Details
            VStack(alignment: .leading, spacing: 4) {
                Text(operation.operationType.rawValue.replacingOccurrences(of: "_", with: " ").capitalized)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.white)
                Text("Entity: \(operation.entityId.prefix(8))...")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text("Attempts: \(operation.attempts)/\(operation.maxAttempts)")
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
                if let error = operation.lastError {
                    Text(error)
                        .font(.caption2)
                        .foregroundStyle(.red)
                        .lineLimit(1)
                }
            }
            
            Spacer()
            
            // Status & Actions
            VStack(alignment: .trailing, spacing: 6) {
                statusBadge
                
                if operation.status == .failed && operation.canRetry {
                    Button("Retry") {
                        onRetry()
                    }
                    .font(.caption.weight(.medium))
                    .foregroundStyle(DeevoColors.accent)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 4)
                    .background(DeevoColors.accent.opacity(0.15))
                    .cornerRadius(6)
                }
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(DeevoColors.surface)
    }
    
    private var iconName: String {
        switch operation.operationType {
        case .submitForm: return "doc.text.fill"
        case .uploadEvidence: return "photo.fill"
        case .updateClaim: return "pencil.circle.fill"
        case .createInspection: return "plus.circle.fill"
        case .updateInspection: return "arrow.triangle.2.circlepath"
        case .deleteMedia: return "trash.fill"
        }
    }
    
    private var iconColor: Color {
        switch operation.status {
        case .pending: return DeevoColors.accent
        case .processing: return DeevoColors.info
        case .completed: return DeevoColors.success
        case .failed: return DeevoColors.error
        }
    }
    
    @ViewBuilder
    private var statusBadge: some View {
        switch operation.status {
        case .pending:
            Label("Pending", systemImage: "clock.fill")
                .font(.caption.weight(.medium))
                .foregroundStyle(DeevoColors.accent)
        case .processing:
            Label("Processing", systemImage: "arrow.clockwise")
                .font(.caption.weight(.medium))
                .foregroundStyle(DeevoColors.info)
        case .completed:
            Label("Completed", systemImage: "checkmark.circle.fill")
                .font(.caption.weight(.medium))
                .foregroundStyle(DeevoColors.success)
        case .failed:
            Label("Failed", systemImage: "exclamationmark.circle.fill")
                .font(.caption.weight(.medium))
                .foregroundStyle(DeevoColors.error)
        }
    }
}

// MARK: - Claim Sync Row

struct ClaimSyncRow: View {
    let status: ClaimSyncStatus
    
    var body: some View {
        HStack(spacing: 12) {
            RoundedRectangle(cornerRadius: 8)
                .fill(DeevoColors.surfaceElevated)
                .frame(width: 52, height: 52)
                .overlay(
                    Image(systemName: "car.fill")
                        .foregroundStyle(DeevoColors.accent)
                )
            
            VStack(alignment: .leading, spacing: 4) {
                Text("Claim: \(status.id.prefix(8))...")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.white)
                Text("Pending ops: \(status.pendingOperations)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                if let lastSync = status.lastSuccess {
                    Text("Last sync: \(lastSync.formatted(.relative(presentation: .named)))")
                        .font(.caption2)
                        .foregroundStyle(.tertiary)
                }
            }
            
            Spacer()
            
            Image(systemName: status.syncState.iconName)
                .foregroundStyle(colorForState(status.syncState))
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(DeevoColors.surface)
    }
    
    private func colorForState(_ state: ClaimSyncState) -> Color {
        switch state {
        case .synced: return DeevoColors.success
        case .pending: return DeevoColors.accent
        case .syncing: return DeevoColors.info
        case .conflict: return .yellow
        case .failed: return DeevoColors.error
        }
    }
}

// MARK: - View Model

@MainActor
class SyncStatusViewModel: ObservableObject {
    @Published var operations: [QueuedOperation] = []
    @Published var claimStatuses: [ClaimSyncStatus] = []
    @Published var pendingCount: Int = 0
    @Published var failedCount: Int = 0
    @Published var isSyncing: Bool = false
    
    private let operationRepository = OperationRepository.shared
    private let operationProcessor = OperationProcessor.shared
    
    func loadData() async {
        do {
            operations = try await operationRepository.fetchAll()
            let counts = try await operationRepository.countByStatus()
            pendingCount = counts[.pending] ?? 0
            failedCount = counts[.failed] ?? 0
            
            // Load claim statuses from SyncService
            claimStatuses = Array(SyncService.shared.claimSyncStatuses.values)
        } catch {
            AppLogger.error("Failed to load sync data", error: error, category: AppLogger.sync)
        }
    }
    
    func syncAll() async {
        isSyncing = true
        await operationProcessor.processQueue()
        await loadData()
        isSyncing = false
    }
    
    func retryOperation(id: String) async {
        await operationProcessor.retryOperation(id: id)
        await loadData()
    }
    
    func retryAllFailed() async {
        await operationProcessor.retryAllFailed()
        await loadData()
    }
}

#Preview {
    NavigationStack {
        SyncStatusScreen()
            .environmentObject(SyncService.shared)
    }
}
