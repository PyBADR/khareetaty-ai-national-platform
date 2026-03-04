import Foundation
import GRDB
import Combine

/// ViewModel for managing claims list and operations
@MainActor
class ClaimsViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var claims: [Claim] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var selectedStatus: ClaimStatus?
    @Published var selectedPriority: ClaimPriority?
    @Published var searchText = ""
    
    // MARK: - Properties
    
    private let database: DatabaseManager
    private let api: APIService
    private let sync: SyncService
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(
        database: DatabaseManager = .shared,
        api: APIService = .shared,
        sync: SyncService = .shared
    ) {
        self.database = database
        self.api = api
        self.sync = sync
        
        setupObservers()
    }
    
    // MARK: - Setup
    
    private func setupObservers() {
        // Observe sync state changes to refresh claims
        sync.$syncState
            .sink { [weak self] state in
                if state.lastSyncTimestamp != nil && !state.isSyncing {
                    Task {
                        await self?.loadLocalClaims()
                    }
                }
            }
            .store(in: &cancellables)
    }
    
    // MARK: - Public Methods
    
    /// Load claims from local database
    func loadLocalClaims() async {
        do {
            let allClaims = try await database.database.read { db in
                try Claim.fetchAll(db)
            }
            
            claims = filterClaims(allClaims)
        } catch {
            errorMessage = "Failed to load local claims: \(error.localizedDescription)"
        }
    }
    
    /// Load claims from server and sync to local database
    func loadRemoteClaims(assignedToMe: Bool = false) async {
        isLoading = true
        errorMessage = nil
        
        do {
            let response = try await api.getClaims(
                status: selectedStatus,
                priority: selectedPriority,
                assignedToMe: assignedToMe
            )
            
            // Save to local database
            try await database.database.write { db in
                for claim in response.claims {
                    try claim.save(db)
                }
            }
            
            claims = filterClaims(response.claims)
            isLoading = false
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            
            // Fallback to local data
            await loadLocalClaims()
        }
    }
    
    /// Accept a claim assignment
    func acceptClaim(_ claim: Claim) async throws {
        let response = try await api.acceptClaim(id: claim.id)
        let updatedClaim = response.claim
        
        // Update local database
        try await database.database.write { db in
            try updatedClaim.save(db)
        }
        
        // Queue sync
        try await sync.queueSync(
            entityType: .claim,
            entityId: claim.id,
            operation: .update,
            payload: updatedClaim
        )
        
        // Refresh claims
        await loadLocalClaims()
    }
    
    /// Update claim status
    func updateClaimStatus(_ claim: Claim, status: ClaimStatus) async throws {
        var updatedClaim = claim
        updatedClaim.status = status
        updatedClaim.updatedAt = Date()
        
        let claimToSave = updatedClaim
        // Update local database
        try await database.database.write { db in
            try claimToSave.update(db)
        }
        
        // Queue sync
        try await sync.queueSync(
            entityType: .claim,
            entityId: claim.id,
            operation: .update,
            payload: claimToSave
        )
        
        // Refresh claims
        await loadLocalClaims()
    }
    
    /// Search claims
    func searchClaims(query: String) {
        searchText = query
        Task {
            await loadLocalClaims()
        }
    }
    
    /// Apply filters
    func applyFilters(status: ClaimStatus?, priority: ClaimPriority?) {
        selectedStatus = status
        selectedPriority = priority
        Task {
            await loadLocalClaims()
        }
    }
    
    /// Clear filters
    func clearFilters() {
        selectedStatus = nil
        selectedPriority = nil
        searchText = ""
        Task {
            await loadLocalClaims()
        }
    }
    
    // MARK: - Private Methods
    
    private func filterClaims(_ allClaims: [Claim]) -> [Claim] {
        var filtered = allClaims
        
        // Apply status filter
        if let status = selectedStatus {
            filtered = filtered.filter { $0.status == status }
        }
        
        // Apply priority filter
        if let priority = selectedPriority {
            filtered = filtered.filter { $0.priority == priority }
        }
        
        // Apply search filter
        if !searchText.isEmpty {
            filtered = filtered.filter { claim in
                claim.claimNumber.localizedCaseInsensitiveContains(searchText) ||
                claim.customerName.localizedCaseInsensitiveContains(searchText) ||
                (claim.vehiclePlate?.localizedCaseInsensitiveContains(searchText) ?? false)
            }
        }
        
        // Sort by priority (desc) then created date (desc)
        return filtered.sorted { lhs, rhs in
            if lhs.priority != rhs.priority {
                return lhs.priority.rawValue > rhs.priority.rawValue
            }
            return lhs.createdAt > rhs.createdAt
        }
    }
}
