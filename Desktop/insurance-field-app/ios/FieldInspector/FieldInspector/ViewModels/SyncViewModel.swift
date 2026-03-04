import Foundation
import Combine

/// ViewModel for managing sync operations and status
@MainActor
class SyncViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var syncState: SyncState
    @Published var isOnline: Bool
    @Published var pendingItems: [SyncQueueItem] = []
    @Published var failedItems: [SyncQueueItem] = []
    @Published var isSyncing = false
    @Published var lastSyncDate: Date?
    @Published var errorMessage: String?
    
    // MARK: - Computed Properties
    
    var syncProgress: Double {
        let total = syncState.pendingCount + syncState.failedCount
        guard total > 0 else { return 1.0 }
        let synced = total - syncState.pendingCount
        return Double(synced) / Double(total)
    }
    
    var hasPendingItems: Bool {
        syncState.pendingCount > 0
    }
    
    var hasFailedItems: Bool {
        syncState.failedCount > 0
    }
    
    var statusText: String {
        if isSyncing {
            return "Syncing..."
        } else if !isOnline {
            return "Offline"
        } else if hasFailedItems {
            return "\(syncState.failedCount) failed"
        } else if hasPendingItems {
            return "\(syncState.pendingCount) pending"
        } else if let lastSync = lastSyncDate {
            return "Last synced \(formatRelativeTime(lastSync))"
        } else {
            return "Not synced"
        }
    }
    
    // MARK: - Properties
    
    private let syncService: SyncService
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(syncService: SyncService = .shared) {
        self.syncService = syncService
        self.syncState = syncService.syncState
        self.isOnline = syncService.isOnline
        
        setupObservers()
        
        // Initial load
        Task {
            await loadPendingItems()
        }
    }
    
    // MARK: - Setup
    
    private func setupObservers() {
        // Observe sync state changes
        syncService.$syncState
            .receive(on: DispatchQueue.main)
            .sink { [weak self] state in
                self?.syncState = state
                self?.isSyncing = state.isSyncing
                self?.lastSyncDate = state.lastSyncTimestamp
                self?.errorMessage = state.lastError
                
                Task {
                    await self?.loadPendingItems()
                }
            }
            .store(in: &cancellables)
        
        // Observe online status
        syncService.$isOnline
            .receive(on: DispatchQueue.main)
            .sink { [weak self] online in
                self?.isOnline = online
            }
            .store(in: &cancellables)
    }
    
    // MARK: - Public Methods
    
    /// Load pending sync items
    func loadPendingItems() async {
        do {
            pendingItems = try await syncService.getPendingItems()
            failedItems = try await syncService.getFailedItems()
        } catch {
            errorMessage = "Failed to load sync items: \(error.localizedDescription)"
        }
    }
    
    /// Trigger manual sync
    func sync() async {
        guard !isSyncing else { return }
        
        await syncService.forceSync()
        await loadPendingItems()
    }
    
    /// Retry failed items
    func retryFailedItems() async {
        await syncService.retryFailedItems()
        await loadPendingItems()
    }
    
    /// Clear old processed items
    func clearOldItems() async {
        do {
            try await syncService.clearOldProcessedItems(olderThanDays: 7)
            await loadPendingItems()
        } catch {
            errorMessage = "Failed to clear old items: \(error.localizedDescription)"
        }
    }
    
    /// Get sync progress for a specific claim
    func getClaimSyncProgress(claimId: String) -> Double {
        let claimItems = pendingItems.filter { $0.entityId == claimId || $0.payloadJson.contains(claimId) }
        guard !claimItems.isEmpty else { return 1.0 }
        
        let total = claimItems.count
        let pending = claimItems.filter { $0.processedAt == nil }.count
        let synced = total - pending
        
        return Double(synced) / Double(total)
    }
    
    // MARK: - Private Methods
    
    private func formatRelativeTime(_ date: Date) -> String {
        let interval = Date().timeIntervalSince(date)
        
        if interval < 60 {
            return "just now"
        } else if interval < 3600 {
            let minutes = Int(interval / 60)
            return "\(minutes)m ago"
        } else if interval < 86400 {
            let hours = Int(interval / 3600)
            return "\(hours)h ago"
        } else {
            let days = Int(interval / 86400)
            return "\(days)d ago"
        }
    }
}
