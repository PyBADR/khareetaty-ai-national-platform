import SwiftUI

struct ClaimInboxView: View {
    let showAssignedOnly: Bool
    
    @State private var claims: [Claim] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var searchText = ""
    @State private var selectedStatus: ClaimStatus?
    @State private var selectedPriority: ClaimPriority?
    @State private var selectedClaim: Claim?
    
    var body: some View {
        mainContent
            .navigationTitle(showAssignedOnly ? "My Claims" : "Claim Inbox")
            .searchable(text: $searchText, prompt: "Search claims...")
            .navigationDestination(for: Claim.self) { claim in
                ClaimDetailView(claim: claim)
            }
            .onAppear {
                if claims.isEmpty {
                    loadClaims()
                }
            }
            .onChange(of: selectedStatus) { _, _ in
                loadClaims()
            }
            .onChange(of: selectedPriority) { _, _ in
                loadClaims()
            }
    }
    
    @ViewBuilder
    private var mainContent: some View {
        VStack(spacing: 0) {
            filterBar
            Divider()
            claimsListContent
        }
    }
    
    @ViewBuilder
    private var filterBar: some View {
        HStack(spacing: 16) {
            statusFilterMenu
            priorityFilterMenu
            Spacer()
            refreshButton
        }
        .padding()
        .background(Color(.systemBackground))
    }
    
    @ViewBuilder
    private var statusFilterMenu: some View {
        Menu {
            Button("All Statuses") {
                selectedStatus = nil
            }
            Divider()
            ForEach(ClaimStatus.allCases, id: \.self) { status in
                Button(status.displayName) {
                    selectedStatus = status
                }
            }
        } label: {
            HStack {
                Text(selectedStatus?.displayName ?? "All Statuses")
                Image(systemName: "chevron.down")
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color(.systemGray6))
            .cornerRadius(8)
        }
    }
    
    @ViewBuilder
    private var priorityFilterMenu: some View {
        Menu {
            Button("All Priorities") {
                selectedPriority = nil
            }
            Divider()
            ForEach(ClaimPriority.allCases, id: \.self) { priority in
                Button(priority.displayName) {
                    selectedPriority = priority
                }
            }
        } label: {
            HStack {
                Text(selectedPriority?.displayName ?? "All Priorities")
                Image(systemName: "chevron.down")
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color(.systemGray6))
            .cornerRadius(8)
        }
    }
    
    @ViewBuilder
    private var refreshButton: some View {
        Button(action: loadClaims) {
            Image(systemName: "arrow.clockwise")
        }
        .disabled(isLoading)
    }
    
    @ViewBuilder
    private var claimsListContent: some View {
        if isLoading && claims.isEmpty {
            SkeletonClaimsList()
        } else if let error = errorMessage {
            ErrorStateView.networkError(message: error) {
                loadClaims()
            }
        } else if filteredClaims.isEmpty {
            EmptyStateView.noClaims
        } else {
            claimsList
        }
    }
    
    @ViewBuilder
    private var claimsList: some View {
        List(filteredClaims, selection: $selectedClaim) { claim in
            NavigationLink(value: claim) {
                ClaimRowView(claim: claim)
            }
        }
        .listStyle(.plain)
        .refreshable {
            loadClaims()
        }
    }
    
    private var filteredClaims: [Claim] {
        if searchText.isEmpty {
            return claims
        }
        return claims.filter { claim in
            claim.claimNumber.localizedCaseInsensitiveContains(searchText) ||
            claim.customerName.localizedCaseInsensitiveContains(searchText) ||
            (claim.vehiclePlate?.localizedCaseInsensitiveContains(searchText) ?? false)
        }
    }
    
    private func loadClaims() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                let response = try await APIService.shared.getClaims(
                    status: selectedStatus,
                    priority: selectedPriority,
                    assignedToMe: showAssignedOnly
                )
                
                await MainActor.run {
                    claims = response.claims
                    isLoading = false
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isLoading = false
                }
            }
        }
    }
}

// MARK: - Claim Row View

struct ClaimRowView: View {
    let claim: Claim
    
    var body: some View {
        HStack(spacing: 16) {
            priorityIndicator
            claimDetails
            syncStatusIndicator
        }
        .padding(.vertical, 8)
    }
    
    @ViewBuilder
    private var priorityIndicator: some View {
        Circle()
            .fill(priorityColor)
            .frame(width: 12, height: 12)
    }
    
    @ViewBuilder
    private var claimDetails: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(claim.claimNumber)
                    .font(.headline)
                
                Spacer()
                
                ClaimStatusBadge(status: claim.status)
            }
            
            Text(claim.customerName)
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            vehicleInfo
        }
    }
    
    @ViewBuilder
    private var vehicleInfo: some View {
        HStack {
            Text(claim.vehicleDescription)
                .font(.caption)
                .foregroundColor(.secondary)
            
            if let plate = claim.vehiclePlate {
                Text("•")
                    .foregroundColor(.secondary)
                Text(plate)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }
    
    @ViewBuilder
    private var syncStatusIndicator: some View {
        if claim.syncStatus != .synced {
            Image(systemName: claim.syncStatus.iconName)
                .foregroundColor(claim.syncStatus == .failed ? DeevoColors.error : DeevoColors.accent)
        }
    }
    
    private var priorityColor: Color {
        switch claim.priority {
        case .urgent: return DeevoColors.riskCritical
        case .high: return DeevoColors.riskElevated
        case .medium: return DeevoColors.riskModerate
        case .low: return DeevoColors.riskLow
        }
    }
}

// MARK: - Claim Status Badge (local to this view)

private struct ClaimStatusBadge: View {
    let status: ClaimStatus
    
    var body: some View {
        Text(status.displayName)
            .font(.caption)
            .fontWeight(.medium)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(backgroundColor)
            .foregroundColor(foregroundColor)
            .cornerRadius(6)
    }
    
    private var backgroundColor: Color {
        switch status {
        case .new: return DeevoColors.secondary.opacity(0.2)
        case .assigned: return DeevoColors.accent.opacity(0.2)
        case .inProgress: return DeevoColors.riskModerate.opacity(0.2)
        case .pendingReview: return DeevoColors.secondary.opacity(0.15)
        case .approved: return DeevoColors.success.opacity(0.2)
        case .rejected: return DeevoColors.error.opacity(0.2)
        case .closed: return DeevoColors.textTertiary.opacity(0.2)
        }
    }
    
    private var foregroundColor: Color {
        switch status {
        case .new: return DeevoColors.secondary
        case .assigned: return DeevoColors.accent
        case .inProgress: return DeevoColors.riskModerate
        case .pendingReview: return DeevoColors.secondary
        case .approved: return DeevoColors.success
        case .rejected: return DeevoColors.error
        case .closed: return DeevoColors.textTertiary
        }
    }
}

#Preview {
    NavigationStack {
        ClaimInboxView(showAssignedOnly: false)
    }
}
