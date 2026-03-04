import SwiftUI

struct OutboxView: View {
    @StateObject private var syncService = SyncService.shared
    
    @State private var pendingItems: [SyncQueueItem] = []
    @State private var failedItems: [SyncQueueItem] = []
    @State private var isLoading = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Sync Status Header
            VStack(spacing: 16) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Sync Status")
                            .font(.headline)
                        
                        if syncService.syncState.isSyncing {
                            HStack {
                                ProgressView()
                                    .scaleEffect(0.8)
                                Text("Syncing...")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                        } else if !syncService.isOnline {
                            HStack {
                                Image(systemName: "wifi.slash")
                                    .foregroundColor(DeevoColors.accent)
                                Text("Offline - Changes will sync when online")
                                    .font(.subheadline)
                                    .foregroundColor(DeevoColors.accent)
                            }
                        } else {
                            HStack {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(DeevoColors.success)
                                Text("Online")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                    
                    Spacer()
                    
                    Button(action: {
                        Task {
                            await syncService.forceSync()
                            await loadItems()
                        }
                    }) {
                        Label("Sync Now", systemImage: "arrow.triangle.2.circlepath")
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(syncService.syncState.isSyncing || !syncService.isOnline)
                }
                
                // Stats
                HStack(spacing: 24) {
                    StatCard(
                        title: "Pending",
                        value: "\(syncService.syncState.pendingCount)",
                        icon: "clock",
                        color: DeevoColors.accent
                    )
                    
                    StatCard(
                        title: "Failed",
                        value: "\(syncService.syncState.failedCount)",
                        icon: "exclamationmark.triangle",
                        color: DeevoColors.error
                    )
                    
                    if let lastSync = syncService.syncState.lastSyncTimestamp {
                        StatCard(
                            title: "Last Sync",
                            value: lastSync.formatted(date: .omitted, time: .shortened),
                            icon: "clock.arrow.circlepath",
                            color: DeevoColors.secondary
                        )
                    }
                }
            }
            .padding()
            .background(Color(.systemGray6))
            
            Divider()
            
            // Items List
            if isLoading {
                SkeletonSyncQueue()
            } else if pendingItems.isEmpty && failedItems.isEmpty {
                EmptyStateView(
                    icon: "checkmark.circle",
                    title: "All synced!",
                    message: "No pending changes to upload.",
                    iconColor: DeevoColors.success
                )
            } else {
                List {
                    if !failedItems.isEmpty {
                        Section {
                            ForEach(failedItems) { item in
                                SyncQueueItemRow(item: item, isFailed: true)
                            }
                        } header: {
                            HStack {
                                Text("Failed (\(failedItems.count))")
                                Spacer()
                                Button("Retry All") {
                                    Task {
                                        await syncService.retryFailedItems()
                                        await loadItems()
                                    }
                                }
                                .font(.caption)
                            }
                        }
                    }
                    
                    if !pendingItems.isEmpty {
                        Section("Pending (\(pendingItems.count))") {
                            ForEach(pendingItems) { item in
                                SyncQueueItemRow(item: item, isFailed: false)
                            }
                        }
                    }
                }
                .listStyle(.insetGrouped)
            }
        }
        .navigationTitle("Outbox")
        .onAppear {
            Task {
                await loadItems()
            }
        }
        .refreshable {
            await loadItems()
        }
    }
    
    private func loadItems() async {
        isLoading = true
        do {
            pendingItems = try await syncService.getPendingItems().filter { $0.lastError == nil }
            failedItems = try await syncService.getFailedItems()
        } catch {
            print("Error loading sync items: \(error)")
        }
        isLoading = false
    }
}

// MARK: - Stat Card

struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
            
            Text(value)
                .font(.title2)
                .fontWeight(.bold)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
    }
}

// MARK: - Sync Queue Item Row

struct SyncQueueItemRow: View {
    let item: SyncQueueItem
    let isFailed: Bool
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: iconForEntityType(item.entityType))
                .font(.title3)
                .foregroundColor(isFailed ? DeevoColors.error : DeevoColors.accent)
                .frame(width: 32)
            
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(item.entityType.rawValue.capitalized)
                        .font(.subheadline)
                        .fontWeight(.medium)
                    
                    Text("•")
                        .foregroundColor(.secondary)
                    
                    Text(item.operation.rawValue.capitalized)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                
                Text(item.entityId)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
                
                if let error = item.lastError {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(DeevoColors.error)
                        .lineLimit(2)
                }
                
                HStack {
                    Text(item.createdAt.formatted(date: .abbreviated, time: .shortened))
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    
                    if item.attempts > 0 {
                        Text("• Attempts: \(item.attempts)/\(item.maxAttempts)")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            Spacer()
            
            if isFailed {
                Image(systemName: "exclamationmark.circle.fill")
                    .foregroundColor(DeevoColors.error)
            } else {
                Image(systemName: "clock")
                    .foregroundColor(DeevoColors.accent)
            }
        }
        .padding(.vertical, 4)
    }
    
    private func iconForEntityType(_ type: SyncEntityType) -> String {
        switch type {
        case .claim: return "doc.text"
        case .inspection: return "checklist"
        case .inspectionField: return "textformat"
        case .mediaAsset: return "photo"
        }
    }
}

#Preview {
    NavigationStack {
        OutboxView()
    }
}
