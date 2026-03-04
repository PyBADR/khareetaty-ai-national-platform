import SwiftUI

// MARK: - Work Order Form View (ION Reference)
/// Matches ION's Job Execution / Work Order form

struct WorkOrderFormView: View {
    let claimId: String
    
    // MARK: - Work Order State
    @State private var workOrderNumber: String = "WO-2026-0304-001"
    @State private var jobDescription: String = ""
    @State private var laborHours: Double = 0
    @State private var materialsCost: Double = 0
    
    // MARK: - Parts Requirements
    @State private var partsExpanded: Bool = true
    @State private var parts: [PartRequirement] = [
        PartRequirement(name: "Toolset", quantity: 5),
        PartRequirement(name: "Plug", quantity: 5),
        PartRequirement(name: "Gasket", quantity: 3),
        PartRequirement(name: "Seal", quantity: 2),
        PartRequirement(name: "", quantity: 0),
        PartRequirement(name: "", quantity: 0)
    ]
    
    // MARK: - Approval
    @State private var approvalExpanded: Bool = true
    @State private var approverName: String = ""
    @State private var quoteRate: QuoteRate = .medium
    @State private var signatureImage: UIImage?
    @State private var showSignaturePad: Bool = false
    
    // MARK: - Submission
    @State private var isSubmitting: Bool = false
    @State private var showSubmitAlert: Bool = false
    
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        List {
            // SECTION 1: Work Order Details
            workOrderDetailsSection
            
            // SECTION 2: Part Requirements
            partRequirementsSection
            
            // SECTION 3: Approval
            approvalSection
        }
        .listStyle(.insetGrouped)
        .navigationTitle("Work Order")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button("Send") {
                    showSubmitAlert = true
                }
                .buttonStyle(.borderedProminent)
                .tint(DeevoColors.accent)
                .disabled(isSubmitting)
            }
        }
        .alert("Submit Work Order", isPresented: $showSubmitAlert) {
            Button("Cancel", role: .cancel) {}
            Button("Submit") {
                Task { await submit() }
            }
        } message: {
            Text("Are you sure you want to submit this work order?")
        }
        .sheet(isPresented: $showSignaturePad) {
            SignatureCaptureSheet(signatureImage: $signatureImage)
        }
    }
    
    // MARK: - Work Order Details Section
    
    private var workOrderDetailsSection: some View {
        Section {
            CollapsibleSectionHeader(
                title: "Job Execution",
                icon: "hammer.fill",
                isExpanded: .constant(true)
            )
            
            // Work Order Number
            HStack {
                Text("Work Order #")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                Spacer()
                Text(workOrderNumber)
                    .font(.subheadline.monospaced())
            }
            
            // Job Description
            VStack(alignment: .leading, spacing: 4) {
                Text("Job Description")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                
                TextEditor(text: $jobDescription)
                    .frame(minHeight: 80)
                    .padding(8)
                    .background(Color(.systemGray6))
                    .cornerRadius(8)
            }
            
            // Labor Hours
            HStack {
                Text("Labor Hours")
                    .font(.subheadline)
                Spacer()
                
                Button {
                    if laborHours > 0 { laborHours -= 0.5 }
                } label: {
                    Image(systemName: "minus.circle.fill")
                        .font(.title2)
                        .foregroundStyle(laborHours > 0 ? DeevoColors.accent : .gray)
                }
                .buttonStyle(.plain)
                
                Text(String(format: "%.1f", laborHours))
                    .font(.title3.monospacedDigit())
                    .frame(minWidth: 50)
                
                Button {
                    laborHours += 0.5
                } label: {
                    Image(systemName: "plus.circle.fill")
                        .font(.title2)
                        .foregroundStyle(DeevoColors.accent)
                }
                .buttonStyle(.plain)
            }
            
            // Materials Cost
            VStack(alignment: .leading, spacing: 4) {
                Text("Materials Cost (KWD)")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                
                HStack {
                    Text("KWD")
                        .foregroundStyle(.secondary)
                    TextField("0.00", value: $materialsCost, format: .number.precision(.fractionLength(2)))
                        .keyboardType(.decimalPad)
                        .textFieldStyle(.plain)
                }
                .padding(12)
                .background(Color(.systemGray6))
                .cornerRadius(8)
            }
        }
    }
    
    // MARK: - Part Requirements Section
    
    private var partRequirementsSection: some View {
        Section {
            CollapsibleSectionHeader(
                title: "Part Requirements",
                icon: "shippingbox",
                isExpanded: $partsExpanded
            )
            
            if partsExpanded {
                PartsRequirementsTable(parts: $parts)
            }
        }
    }
    
    // MARK: - Approval Section
    
    private var approvalSection: some View {
        Section {
            CollapsibleSectionHeader(
                title: "Approval",
                icon: "signature",
                isExpanded: $approvalExpanded
            )
            
            if approvalExpanded {
                // Approver
                FormTextField(title: "Approver:", text: $approverName)
                
                // Quote Rate slider
                VStack(alignment: .leading, spacing: 8) {
                    Text("Quote Rate")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                    
                    HStack {
                        Text("Low")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        
                        Slider(
                            value: Binding(
                                get: { Double(quoteRate.rawValue) },
                                set: { quoteRate = QuoteRate(rawValue: Int($0)) ?? .medium }
                            ),
                            in: 0...2,
                            step: 1
                        )
                        .tint(quoteRate.color)
                        
                        Text("High")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    
                    // Rate indicator badge
                    HStack {
                        Spacer()
                        Text(quoteRate.label)
                            .font(.caption.weight(.semibold))
                            .padding(.horizontal, 12)
                            .padding(.vertical, 4)
                            .background(quoteRate.color.opacity(0.2))
                            .foregroundStyle(quoteRate.color)
                            .cornerRadius(8)
                        Spacer()
                    }
                }
                
                // Signature pad
                VStack(alignment: .leading, spacing: 8) {
                    Text("Signature")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                    
                    Button {
                        showSignaturePad = true
                    } label: {
                        ZStack {
                            RoundedRectangle(cornerRadius: 8)
                                .fill(Color(.systemGray6))
                                .frame(height: 120)
                            
                            if let signature = signatureImage {
                                Image(uiImage: signature)
                                    .resizable()
                                    .scaledToFit()
                                    .padding(8)
                            } else {
                                VStack(spacing: 4) {
                                    Image(systemName: "signature")
                                        .font(.title)
                                        .foregroundStyle(.secondary)
                                    Text("Tap here to add signature")
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                            }
                        }
                    }
                    .buttonStyle(.plain)
                }
                
                // Total Cost Summary
                VStack(spacing: 8) {
                    Divider()
                    
                    HStack {
                        Text("Total Estimated Cost")
                            .font(.headline)
                        Spacer()
                        Text("KWD \(totalCost, specifier: "%.2f")")
                            .font(.headline)
                            .foregroundStyle(DeevoColors.accent)
                    }
                }
                .padding(.top, 8)
            }
        }
    }
    
    // MARK: - Computed Properties
    
    private var totalCost: Double {
        let laborCost = laborHours * 25.0 // KWD 25/hour
        let partsCost = Double(parts.reduce(0) { $0 + $1.quantity }) * 5.0 // KWD 5/part
        return laborCost + materialsCost + partsCost
    }
    
    // MARK: - Submit
    
    private func submit() async {
        isSubmitting = true
        
        // TODO: Submit to API
        try? await Task.sleep(nanoseconds: 1_000_000_000)
        
        await MainActor.run {
            isSubmitting = false
            dismiss()
        }
    }
}

#Preview {
    NavigationStack {
        WorkOrderFormView(claimId: "test-claim-id")
    }
}
