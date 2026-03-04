import SwiftUI

/// Per-claim sync status indicator component
struct ClaimSyncIndicator: View {
    let claimId: String
    @ObservedObject private var syncService = SyncService.shared
    
    private var status: ClaimSyncStatus {
        syncService.getSyncStatus(for: claimId)
    }
    
    var body: some View {
        HStack(spacing: 4) {
            statusIcon
            
            if status.pendingOperations > 0 {
                Text("\(status.pendingOperations)")
                    .font(DeevoTypography.caption)
                    .foregroundColor(statusColor)
            }
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(statusColor.opacity(0.1))
        .cornerRadius(12)
    }
    
    @ViewBuilder
    private var statusIcon: some View {
        switch status.syncState {
        case .synced:
            Image(systemName: "checkmark.circle.fill")
                .foregroundColor(.green)
                .font(.system(size: 14))
        case .pending:
            Image(systemName: "clock.fill")
                .foregroundColor(.orange)
                .font(.system(size: 14))
        case .syncing:
            ProgressView()
                .scaleEffect(0.7)
        case .conflict:
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundColor(.yellow)
                .font(.system(size: 14))
        case .failed:
            Image(systemName: "xmark.circle.fill")
                .foregroundColor(.red)
                .font(.system(size: 14))
        }
    }
    
    private var statusColor: Color {
        switch status.syncState {
        case .synced: return .green
        case .pending: return .orange
        case .syncing: return .blue
        case .conflict: return .yellow
        case .failed: return .red
        }
    }
}

/// Detailed sync status view for claim detail screen
struct ClaimSyncDetailView: View {
    let claimId: String
    @ObservedObject private var syncService = SyncService.shared
    @State private var showingConflictResolution = false
    
    private var status: ClaimSyncStatus {
        syncService.getSyncStatus(for: claimId)
    }
    
    private var conflicts: [SyncConflict] {
        syncService.pendingConflicts.filter { $0.entityId == claimId }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Status header
            HStack {
                ClaimSyncIndicator(claimId: claimId)
                
                Spacer()
                
                Text(statusText)
                    .font(DeevoTypography.bodySmall)
                    .foregroundColor(DeevoColors.textSecondary)
            }
            
            // Last sync info
            if let lastSuccess = status.lastSuccess {
                HStack {
                    Image(systemName: "clock")
                        .foregroundColor(DeevoColors.textSecondary)
                    Text("Last synced: \(lastSuccess.formatted(date: .abbreviated, time: .shortened))")
                        .font(DeevoTypography.caption)
                        .foregroundColor(DeevoColors.textSecondary)
                }
            }
            
            // Error message
            if let error = status.lastError {
                HStack {
                    Image(systemName: "exclamationmark.circle")
                        .foregroundColor(DeevoColors.error)
                    Text(error)
                        .font(DeevoTypography.caption)
                        .foregroundColor(DeevoColors.error)
                }
            }
            
            // Retry info
            if status.syncState == .failed, let nextRetry = status.nextRetryAt {
                HStack {
                    Image(systemName: "arrow.clockwise")
                        .foregroundColor(DeevoColors.textSecondary)
                    Text("Retry scheduled: \(nextRetry.formatted(date: .omitted, time: .shortened))")
                        .font(DeevoTypography.caption)
                        .foregroundColor(DeevoColors.textSecondary)
                }
            }
            
            // Conflict resolution button
            if !conflicts.isEmpty {
                Button(action: { showingConflictResolution = true }) {
                    HStack {
                        Image(systemName: "exclamationmark.triangle.fill")
                        Text("\(conflicts.count) conflict(s) need resolution")
                    }
                    .font(DeevoTypography.bodySmall)
                    .foregroundColor(.white)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                    .background(DeevoColors.accent)
                    .cornerRadius(8)
                }
            }
            
            // Action buttons
            HStack(spacing: 12) {
                if status.syncState == .failed {
                    Button(action: retrySync) {
                        HStack {
                            Image(systemName: "arrow.clockwise")
                            Text("Retry Now")
                        }
                        .font(DeevoTypography.bodySmall)
                        .foregroundColor(DeevoColors.primary)
                    }
                }
                
                if status.pendingOperations > 0 && syncService.isOnline {
                    Button(action: forceSync) {
                        HStack {
                            Image(systemName: "arrow.up.circle")
                            Text("Sync Now")
                        }
                        .font(DeevoTypography.bodySmall)
                        .foregroundColor(DeevoColors.secondary)
                    }
                }
            }
        }
        .padding()
        .background(DeevoColors.backgroundDark.opacity(0.5))
        .cornerRadius(12)
        .sheet(isPresented: $showingConflictResolution) {
            ConflictResolutionSheet(conflicts: conflicts)
        }
    }
    
    private var statusText: String {
        switch status.syncState {
        case .synced: return "All changes synced"
        case .pending: return "\(status.pendingOperations) pending"
        case .syncing: return "Syncing..."
        case .conflict: return "Conflicts detected"
        case .failed: return "Sync failed (retry \(status.retryCount))"
        }
    }
    
    private func retrySync() {
        Task {
            await syncService.retryFailedItems()
        }
    }
    
    private func forceSync() {
        Task {
            await syncService.forceSync()
        }
    }
}

/// Sheet for resolving sync conflicts
struct ConflictResolutionSheet: View {
    let conflicts: [SyncConflict]
    @Environment(\.dismiss) private var dismiss
    @ObservedObject private var syncService = SyncService.shared
    
    var body: some View {
        NavigationView {
            List(conflicts) { conflict in
                ConflictResolutionRow(conflict: conflict)
            }
            .navigationTitle("Resolve Conflicts")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

/// Row for individual conflict resolution
struct ConflictResolutionRow: View {
    let conflict: SyncConflict
    @ObservedObject private var syncService = SyncService.shared
    @State private var isResolving = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Field name
            Text(conflict.field.capitalized)
                .font(DeevoTypography.labelMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            // Values comparison
            HStack(spacing: 16) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Your Value")
                        .font(DeevoTypography.caption)
                        .foregroundColor(DeevoColors.textSecondary)
                    Text(conflict.localValue)
                        .font(DeevoTypography.bodySmall)
                        .foregroundColor(DeevoColors.textPrimary)
                        .padding(8)
                        .background(DeevoColors.secondary.opacity(0.1))
                        .cornerRadius(6)
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("Server Value")
                        .font(DeevoTypography.caption)
                        .foregroundColor(DeevoColors.textSecondary)
                    Text(conflict.serverValue)
                        .font(DeevoTypography.bodySmall)
                        .foregroundColor(DeevoColors.textPrimary)
                        .padding(8)
                        .background(DeevoColors.accent.opacity(0.1))
                        .cornerRadius(6)
                }
            }
            
            // Resolution buttons
            if isResolving {
                ProgressView()
                    .frame(maxWidth: .infinity)
            } else {
                HStack(spacing: 12) {
                    Button(action: { resolveConflict(.acceptLocal) }) {
                        Text("Keep Mine")
                            .font(DeevoTypography.labelSmall)
                            .foregroundColor(.white)
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(DeevoColors.secondary)
                            .cornerRadius(6)
                    }
                    
                    Button(action: { resolveConflict(.acceptServer) }) {
                        Text("Use Server")
                            .font(DeevoTypography.labelSmall)
                            .foregroundColor(.white)
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(DeevoColors.accent)
                            .cornerRadius(6)
                    }
                }
            }
        }
        .padding(.vertical, 8)
    }
    
    private func resolveConflict(_ resolution: ConflictResolution) {
        isResolving = true
        Task {
            do {
                try await syncService.resolveConflict(conflict, resolution: resolution, resolvedBy: "user")
            } catch {
                print("❌ Error resolving conflict: \(error)")
            }
            await MainActor.run {
                isResolving = false
            }
        }
    }
}

#Preview {
    VStack(spacing: 20) {
        ClaimSyncIndicator(claimId: "test-claim-1")
        ClaimSyncDetailView(claimId: "test-claim-1")
    }
    .padding()
    .background(DeevoColors.backgroundDark)
}
