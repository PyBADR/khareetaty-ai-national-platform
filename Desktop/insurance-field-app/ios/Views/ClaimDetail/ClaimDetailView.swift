import SwiftUI

struct ClaimDetailView: View {
    let claim: Claim
    
    @State private var selectedTab = 0
    @State private var showAcceptAlert = false
    @State private var isAccepting = false
    @State private var currentClaim: Claim
    
    init(claim: Claim) {
        self.claim = claim
        self._currentClaim = State(initialValue: claim)
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Tab Bar
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 0) {
                    TabButton(title: "Summary", icon: "doc.text", isSelected: selectedTab == 0) {
                        selectedTab = 0
                    }
                    TabButton(title: "Inspection", icon: "checklist", isSelected: selectedTab == 1) {
                        selectedTab = 1
                    }
                    TabButton(title: "Evidence", icon: "photo.stack", isSelected: selectedTab == 2) {
                        selectedTab = 2
                    }
                    TabButton(title: "AI Suggest", icon: "brain", isSelected: selectedTab == 3) {
                        selectedTab = 3
                    }
                    TabButton(title: "Risk", icon: "exclamationmark.shield", isSelected: selectedTab == 4) {
                        selectedTab = 4
                    }
                    TabButton(title: "Audit Log", icon: "clock.arrow.circlepath", isSelected: selectedTab == 5) {
                        selectedTab = 5
                    }
                }
                .padding(.horizontal)
            }
            .background(Color(.systemGray6))
            
            Divider()
            
            // Content
            TabView(selection: $selectedTab) {
                ClaimSummaryTab(claim: currentClaim)
                    .tag(0)
                
                InspectionTab(claimId: currentClaim.id)
                    .tag(1)
                
                EvidenceTab(claimId: currentClaim.id)
                    .tag(2)
                
                AISuggestionTab(claimId: currentClaim.id)
                    .tag(3)
                
                RiskAssessmentView(claim: currentClaim)
                    .tag(4)
                
                AuditLogTab(claimId: currentClaim.id)
                    .tag(5)
            }
            .tabViewStyle(.page(indexDisplayMode: .never))
        }
        .navigationTitle(currentClaim.claimNumber)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                if currentClaim.status == .new || currentClaim.status == .assigned {
                    Button("Accept Claim") {
                        showAcceptAlert = true
                    }
                    .disabled(isAccepting)
                }
            }
            
            ToolbarItem(placement: .primaryAction) {
                Menu {
                    Button(action: {}) {
                        Label("Generate Report", systemImage: "doc.richtext")
                    }
                    Button(action: {}) {
                        Label("Share", systemImage: "square.and.arrow.up")
                    }
                } label: {
                    Image(systemName: "ellipsis.circle")
                }
            }
        }
        .alert("Accept Claim", isPresented: $showAcceptAlert) {
            Button("Cancel", role: .cancel) {}
            Button("Accept") {
                acceptClaim()
            }
        } message: {
            Text("Are you sure you want to accept this claim? It will be assigned to you.")
        }
    }
    
    private func acceptClaim() {
        isAccepting = true
        
        Task {
            do {
                let response = try await APIService.shared.acceptClaim(id: currentClaim.id)
                await MainActor.run {
                    currentClaim = response.claim
                    isAccepting = false
                }
            } catch {
                await MainActor.run {
                    isAccepting = false
                }
                print("Error accepting claim: \(error)")
            }
        }
    }
}

// MARK: - Tab Button

struct TabButton: View {
    let title: String
    let icon: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.title3)
                Text(title)
                    .font(.caption)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .foregroundColor(isSelected ? DeevoColors.accent : .secondary)
            .background(
                isSelected ? DeevoColors.accent.opacity(0.1) : Color.clear
            )
            .cornerRadius(8)
        }
    }
}

// MARK: - Claim Summary Tab

struct ClaimSummaryTab: View {
    let claim: Claim
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Status Card
                GroupBox {
                    HStack {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Status")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            ClaimDetailStatusBadge(status: claim.status)
                        }
                        
                        Spacer()
                        
                        VStack(alignment: .trailing, spacing: 8) {
                            Text("Priority")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            PriorityBadge(priority: claim.priority)
                        }
                    }
                } label: {
                    Label("Claim Status", systemImage: "flag")
                }
                
                // Customer Info
                GroupBox {
                    VStack(alignment: .leading, spacing: 12) {
                        ClaimInfoRow(label: "Name", value: claim.customerName)
                        if let phone = claim.customerPhone {
                            ClaimInfoRow(label: "Phone", value: phone)
                        }
                        if let email = claim.customerEmail {
                            ClaimInfoRow(label: "Email", value: email)
                        }
                    }
                } label: {
                    Label("Customer Information", systemImage: "person")
                }
                
                // Vehicle Info
                GroupBox {
                    VStack(alignment: .leading, spacing: 12) {
                        ClaimInfoRow(label: "Vehicle", value: claim.vehicleDescription)
                        if let vin = claim.vehicleVin {
                            ClaimInfoRow(label: "VIN", value: vin)
                        }
                        if let plate = claim.vehiclePlate {
                            ClaimInfoRow(label: "License Plate", value: plate)
                        }
                        if let color = claim.vehicleColor {
                            ClaimInfoRow(label: "Color", value: color)
                        }
                    }
                } label: {
                    Label("Vehicle Information", systemImage: "car")
                }
                
                // Incident Info
                GroupBox {
                    VStack(alignment: .leading, spacing: 12) {
                        if let date = claim.incidentDate {
                            ClaimInfoRow(label: "Date", value: date.formatted(date: .long, time: .shortened))
                        }
                        ClaimInfoRow(label: "Location", value: claim.fullAddress)
                        if let description = claim.incidentDescription {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Description")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                Text(description)
                                    .font(.body)
                            }
                        }
                        if let damage = claim.estimatedDamage {
                            ClaimInfoRow(label: "Estimated Damage", value: "$\(String(format: "%.2f", damage))")
                        }
                    }
                } label: {
                    Label("Incident Details", systemImage: "exclamationmark.triangle")
                }
            }
            .padding()
        }
    }
}

// MARK: - Claim Info Row (local to this view)

private struct ClaimInfoRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
                .frame(width: 100, alignment: .leading)
            Text(value)
                .font(.body)
            Spacer()
        }
    }
}

// MARK: - Priority Badge

struct PriorityBadge: View {
    let priority: ClaimPriority
    
    var body: some View {
        Text(priority.displayName)
            .font(.caption)
            .fontWeight(.medium)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(backgroundColor)
            .foregroundColor(foregroundColor)
            .cornerRadius(6)
    }
    
    private var backgroundColor: Color {
        switch priority {
        case .urgent: return DeevoColors.riskCritical.opacity(0.2)
        case .high: return DeevoColors.riskElevated.opacity(0.2)
        case .medium: return DeevoColors.riskModerate.opacity(0.2)
        case .low: return DeevoColors.riskLow.opacity(0.2)
        }
    }
    
    private var foregroundColor: Color {
        switch priority {
        case .urgent: return DeevoColors.riskCritical
        case .high: return DeevoColors.riskElevated
        case .medium: return DeevoColors.riskModerate
        case .low: return DeevoColors.riskLow
        }
    }
}

// MARK: - Claim Detail Status Badge (local to this view)

private struct ClaimDetailStatusBadge: View {
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
        ClaimDetailView(claim: Claim(
            claimNumber: "CLM-2026-001",
            customerName: "John Doe",
            vehicleMake: "Toyota",
            vehicleModel: "Camry",
            vehicleYear: 2022
        ))
    }
}
