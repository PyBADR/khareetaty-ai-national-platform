import SwiftUI

struct InspectionTab: View {
    let claimId: String
    
    @State private var inspections: [Inspection] = []
    @State private var isLoading = false
    @State private var showCreateInspection = false
    @State private var selectedInspection: Inspection?
    
    var body: some View {
        VStack {
            if isLoading {
                SkeletonClaimDetail()
            } else if inspections.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "checklist")
                        .font(.system(size: 60))
                        .foregroundColor(.secondary)
                    Text("No inspections yet")
                        .font(.headline)
                    Text("Start a new inspection to begin documenting this claim.")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                    Button(action: { showCreateInspection = true }) {
                        Label("Start Inspection", systemImage: "plus")
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding()
            } else {
                List {
                    ForEach(inspections) { inspection in
                        NavigationLink(value: inspection) {
                            InspectionRowView(inspection: inspection)
                        }
                    }
                }
                .listStyle(.plain)
            }
        }
        .navigationDestination(for: Inspection.self) { inspection in
            InspectionFormView(inspection: inspection)
        }
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                if !inspections.isEmpty {
                    Button(action: { showCreateInspection = true }) {
                        Image(systemName: "plus")
                    }
                }
            }
        }
        .sheet(isPresented: $showCreateInspection) {
            CreateInspectionSheet(claimId: claimId) { newInspection in
                inspections.append(newInspection)
            }
        }
        .onAppear {
            loadInspections()
        }
    }
    
    private func loadInspections() {
        isLoading = true
        Task {
            do {
                let response = try await APIService.shared.getInspections(claimId: claimId)
                await MainActor.run {
                    inspections = response.inspections
                    isLoading = false
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                }
            }
        }
    }
}

// MARK: - Inspection Row View

struct InspectionRowView: View {
    let inspection: Inspection
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Inspection")
                    .font(.headline)
                Text("Template: \(inspection.templateId)")
                    .font(.caption)
                    .foregroundColor(.secondary)
                if let startedAt = inspection.startedAt {
                    Text("Started: \(startedAt.formatted())")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
            
            InspectionStatusBadge(status: inspection.status)
        }
        .padding(.vertical, 8)
    }
}

// MARK: - Inspection Status Badge

struct InspectionStatusBadge: View {
    let status: InspectionStatus
    
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
        case .notStarted: return DeevoColors.textTertiary.opacity(0.2)
        case .inProgress: return DeevoColors.accent.opacity(0.2)
        case .completed: return DeevoColors.success.opacity(0.2)
        }
    }
    
    private var foregroundColor: Color {
        switch status {
        case .notStarted: return DeevoColors.textTertiary
        case .inProgress: return DeevoColors.accent
        case .completed: return DeevoColors.success
        }
    }
}

// MARK: - Create Inspection Sheet

struct CreateInspectionSheet: View {
    let claimId: String
    let onCreated: (Inspection) -> Void
    
    @Environment(\.dismiss) private var dismiss
    @State private var selectedTemplateId = "motor-inspection-v1"
    @State private var isCreating = false
    
    var body: some View {
        NavigationStack {
            Form {
                Section("Select Template") {
                    Picker("Template", selection: $selectedTemplateId) {
                        Text("Motor Vehicle Inspection").tag("motor-inspection-v1")
                    }
                }
                
                Section {
                    Text("This will create a new inspection using the selected template. You can fill out the form and capture evidence.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle("New Inspection")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Create") {
                        createInspection()
                    }
                    .disabled(isCreating)
                }
            }
        }
    }
    
    private func createInspection() {
        isCreating = true
        Task {
            do {
                let response = try await APIService.shared.createInspection(
                    claimId: claimId,
                    templateId: selectedTemplateId
                )
                await MainActor.run {
                    onCreated(response.inspection)
                    dismiss()
                }
            } catch {
                await MainActor.run {
                    isCreating = false
                }
            }
        }
    }
}
