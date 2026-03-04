import SwiftUI
import PencilKit

// MARK: - Equipment Inspection Form View (ION Reference)
/// Matches ION's Equipment Inspection form with Parts Requirements and Approval sections

struct EquipmentInspectionFormView: View {
    let claimId: String
    
    // MARK: - Equipment Information State
    @State private var equipmentInfo: String = "Type III Pump System w/Heat Extraction Valve"
    @State private var serialNumber: String = "M4120980VC"
    @State private var modelNumber: String = "123121619150DX"
    @State private var equipmentTypeCode: String = "VY121"
    @State private var accessoriesInstalled: String = "Wheels"
    @State private var certificateDocument: DocumentAttachment?
    
    // MARK: - Diagnostics State
    @State private var diagnosticsExpanded: Bool = true
    @State private var diagnosticPhotos: [CapturedPhoto] = []
    @State private var allChecksCompleted: Bool = false
    
    // MARK: - Parts Requirements State
    @State private var partsExpanded: Bool = true
    @State private var parts: [PartRequirement] = [
        PartRequirement(name: "Toolset", quantity: 5),
        PartRequirement(name: "Plug", quantity: 5),
        PartRequirement(name: "Milk", quantity: 5),
        PartRequirement(name: "Snout", quantity: 5),
        PartRequirement(name: "Torque", quantity: 5),
        PartRequirement(name: "Fanyo", quantity: 5),
        PartRequirement(name: "Adhesive Pad", quantity: 0),
        PartRequirement(name: "Scribe Pad", quantity: 0),
        PartRequirement(name: "", quantity: 0),
        PartRequirement(name: "", quantity: 0)
    ]
    
    // MARK: - Approval State
    @State private var approvalExpanded: Bool = true
    @State private var approverName: String = "Sam S."
    @State private var quoteRate: QuoteRate = .medium
    @State private var signatureImage: UIImage?
    @State private var showSignaturePad: Bool = false
    
    // MARK: - Submission
    @State private var isSubmitting: Bool = false
    @State private var showSubmitAlert: Bool = false
    
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        List {
            // SECTION 1: Equipment Information
            equipmentInformationSection
            
            // SECTION 2: Diagnostics
            diagnosticsSection
            
            // SECTION 3: Part Requirements
            partRequirementsSection
            
            // SECTION 4: Approval
            approvalSection
        }
        .listStyle(.insetGrouped)
        .navigationTitle("Equipment Inspection")
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
        .alert("Submit Inspection", isPresented: $showSubmitAlert) {
            Button("Cancel", role: .cancel) {}
            Button("Submit") {
                Task { await submit() }
            }
        } message: {
            Text("Are you sure you want to submit this equipment inspection?")
        }
        .sheet(isPresented: $showSignaturePad) {
            SignatureCaptureSheet(signatureImage: $signatureImage)
        }
    }
    
    // MARK: - Equipment Information Section
    
    private var equipmentInformationSection: some View {
        Section {
            CollapsibleSectionHeader(
                title: "Equipment Information",
                icon: "wrench.and.screwdriver",
                isExpanded: .constant(true)
            )
            
            // Equipment Information text area
            VStack(alignment: .leading, spacing: 4) {
                Text("Equipment Information:")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                
                TextEditor(text: $equipmentInfo)
                    .frame(minHeight: 60)
                    .padding(8)
                    .background(Color(.systemGray6))
                    .cornerRadius(8)
            }
            
            // Serial Number
            FormTextField(title: "Serial Number:", text: $serialNumber)
            
            // Model Number
            FormTextField(title: "Model Number:", text: $modelNumber)
            
            // Equipment Type Code
            FormTextField(title: "Equipment Type Code:", text: $equipmentTypeCode)
            
            // Equipment Accessories Installed
            FormTextField(title: "Equipment Accessories Installed:", text: $accessoriesInstalled)
            
            // Certificate Document Scan
            VStack(alignment: .leading, spacing: 8) {
                Text("Certificate Document Scan")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                
                if let doc = certificateDocument {
                    HStack {
                        Image(systemName: "doc.fill")
                            .foregroundStyle(.blue)
                        VStack(alignment: .leading) {
                            Text(doc.filename)
                                .font(.subheadline)
                            Text(doc.formattedSize)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        Spacer()
                        Button {
                            certificateDocument = nil
                        } label: {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundStyle(.secondary)
                        }
                    }
                    .padding(12)
                    .background(Color(.systemGray6))
                    .cornerRadius(8)
                } else {
                    Button {
                        // TODO: Show document picker
                        certificateDocument = DocumentAttachment(
                            filename: "certificate_scan.pdf",
                            sizeBytes: 75776
                        )
                    } label: {
                        HStack {
                            Image(systemName: "doc.badge.plus")
                            Text("Tap to attach document")
                                .font(.subheadline)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(12)
                        .background(Color(.systemGray6))
                        .foregroundStyle(.secondary)
                        .cornerRadius(8)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }
    
    // MARK: - Diagnostics Section
    
    private var diagnosticsSection: some View {
        Section {
            CollapsibleSectionHeader(
                title: "Diagnostics",
                icon: "waveform.path.ecg",
                isExpanded: $diagnosticsExpanded
            )
            
            if diagnosticsExpanded {
                // Diagnostic panel instruction
                VStack(alignment: .leading, spacing: 4) {
                    Text("Open diagnostic panel to access equipment testing panel")
                        .font(.subheadline)
                        .foregroundStyle(.primary)
                }
                .padding(.vertical, 4)
                
                // Diagnostic capture image panel
                VStack(alignment: .leading, spacing: 8) {
                    Text("Diagnostic capture image panel")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                    
                    FormPhotoGridRow(
                        title: "",
                        photos: $diagnosticPhotos,
                        maxPhotos: 4,
                        columns: 2
                    )
                }
                
                // All checks completed checkbox
                Button {
                    withAnimation {
                        allChecksCompleted.toggle()
                    }
                } label: {
                    HStack {
                        Text("All checks completed on the equipment?")
                            .font(.subheadline)
                            .foregroundStyle(.primary)
                        Spacer()
                        Image(systemName: allChecksCompleted ? "checkmark.square.fill" : "square")
                            .font(.title2)
                            .foregroundStyle(allChecksCompleted ? .blue : .secondary)
                    }
                }
                .buttonStyle(.plain)
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
            }
        }
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

// MARK: - Supporting Types

struct PartRequirement: Identifiable {
    let id = UUID()
    var name: String
    var quantity: Int
}

enum QuoteRate: Int, CaseIterable {
    case low = 0
    case medium = 1
    case high = 2
    
    var label: String {
        switch self {
        case .low: return "Low"
        case .medium: return "Medium"
        case .high: return "High"
        }
    }
    
    var color: Color {
        switch self {
        case .low: return .green
        case .medium: return .orange
        case .high: return .red
        }
    }
}

struct DocumentAttachment: Identifiable {
    let id = UUID()
    var filename: String
    var sizeBytes: Int
    var localPath: String?
    
    var formattedSize: String {
        ByteCountFormatter.string(fromByteCount: Int64(sizeBytes), countStyle: .file)
    }
}

// MARK: - Parts Requirements Table

struct PartsRequirementsTable: View {
    @Binding var parts: [PartRequirement]
    
    var totalQuantity: Int {
        parts.reduce(0) { $0 + $1.quantity }
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Table header
            HStack {
                Text("#")
                    .frame(width: 30, alignment: .leading)
                Text("Part")
                    .frame(maxWidth: .infinity, alignment: .leading)
                Text("Tables")
                    .frame(width: 60, alignment: .center)
            }
            .font(.caption.weight(.semibold))
            .foregroundStyle(.secondary)
            .padding(.vertical, 8)
            .padding(.horizontal, 12)
            .background(Color(.systemGray6))
            
            Divider()
            
            // Part rows
            ForEach(Array(parts.enumerated()), id: \.element.id) { index, _ in
                HStack {
                    Text("\(index + 1)")
                        .frame(width: 30, alignment: .leading)
                        .foregroundStyle(.secondary)
                        .font(.caption)
                    
                    TextField("Part name", text: $parts[index].name)
                        .font(.subheadline)
                    
                    TextField("Qty", value: $parts[index].quantity, format: .number)
                        .frame(width: 60)
                        .multilineTextAlignment(.center)
                        .font(.subheadline)
                        .keyboardType(.numberPad)
                }
                .padding(.vertical, 6)
                .padding(.horizontal, 12)
                
                Divider()
            }
            
            // Total row
            HStack {
                Spacer()
                Text("Total: \(totalQuantity)")
                    .font(.subheadline.weight(.semibold))
                Button("View All") {
                    // TODO: Show all parts
                }
                .font(.caption)
                .tint(.blue)
            }
            .padding(.vertical, 8)
            .padding(.horizontal, 12)
        }
        .background(Color(.systemBackground))
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color(.systemGray4), lineWidth: 1)
        )
    }
}

// MARK: - Signature Capture Sheet

struct SignatureCaptureSheet: View {
    @Binding var signatureImage: UIImage?
    @State private var canvasView = PKCanvasView()
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 16) {
                Text("Draw your signature below")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                
                SignatureCanvasView(canvasView: $canvasView)
                    .frame(height: 200)
                    .background(Color.white)
                    .cornerRadius(12)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color(.systemGray4), lineWidth: 1)
                    )
                    .padding(.horizontal)
                
                HStack(spacing: 20) {
                    Button("Clear") {
                        canvasView.drawing = PKDrawing()
                    }
                    .buttonStyle(.bordered)
                    
                    Button("Save Signature") {
                        saveSignature()
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(DeevoColors.accent)
                }
            }
            .padding()
            .navigationTitle("Signature")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }
    
    private func saveSignature() {
        let bounds = canvasView.bounds
        UIGraphicsBeginImageContextWithOptions(bounds.size, false, UIScreen.main.scale)
        canvasView.drawHierarchy(in: bounds, afterScreenUpdates: true)
        let image = UIGraphicsGetImageFromCurrentImageContext()
        UIGraphicsEndImageContext()
        
        signatureImage = image
        dismiss()
    }
}

struct SignatureCanvasView: UIViewRepresentable {
    @Binding var canvasView: PKCanvasView
    
    func makeUIView(context: Context) -> PKCanvasView {
        canvasView.tool = PKInkingTool(.pen, color: .black, width: 3)
        canvasView.backgroundColor = .white
        canvasView.isOpaque = false
        return canvasView
    }
    
    func updateUIView(_ uiView: PKCanvasView, context: Context) {}
}

#Preview {
    NavigationStack {
        EquipmentInspectionFormView(claimId: "test-claim-id")
    }
}
