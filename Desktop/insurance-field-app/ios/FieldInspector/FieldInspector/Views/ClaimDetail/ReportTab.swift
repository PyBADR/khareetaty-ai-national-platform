import SwiftUI

/// Report tab for generating and viewing PDF reports
struct ReportTab: View {
    let claimId: String
    let claim: Claim
    
    @State private var isGenerating = false
    @State private var reports: [ClaimReport] = []
    @State private var showPDFPreview = false
    @State private var selectedReport: ClaimReport?
    @State private var completenessScore: Double = 0.75
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // AI Advisory Signals
                aiAdvisorySection
                
                // Completeness Score
                completenessSection
                
                // Generate Report Button
                generateReportSection
                
                // Previous Reports
                if !reports.isEmpty {
                    previousReportsSection
                }
                
                // Submit Claim Button
                if completenessScore >= 0.8 {
                    submitClaimSection
                }
            }
            .padding()
        }
        .onAppear {
            loadReports()
            calculateCompleteness()
        }
        .sheet(isPresented: $showPDFPreview) {
            if let report = selectedReport {
                PDFPreviewView(report: report)
            }
        }
    }
    
    // MARK: - AI Advisory Section
    private var aiAdvisorySection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "brain")
                    .foregroundStyle(DeevoColors.accent)
                Text("AI Advisory Signals")
                    .font(.headline)
                    .foregroundStyle(.white)
            }
            
            VStack(spacing: 8) {
                AISignalRow(
                    icon: "checkmark.circle.fill",
                    color: .green,
                    message: "All required evidence captured"
                )
                
                AISignalRow(
                    icon: "exclamationmark.triangle.fill",
                    color: .orange,
                    message: "1 photo may need better lighting"
                )
                
                AISignalRow(
                    icon: "info.circle.fill",
                    color: .blue,
                    message: "Damage estimate within expected range"
                )
            }
            
            // Disclaimer
            HStack(spacing: 8) {
                Image(systemName: "exclamationmark.triangle.fill")
                    .font(.caption)
                Text("AI signals are advisory only. Final decisions rest with the adjuster.")
                    .font(.caption)
            }
            .foregroundStyle(DeevoColors.warning)
            .padding(12)
            .background(DeevoColors.warning.opacity(0.1))
            .cornerRadius(8)
        }
        .padding(16)
        .background(DeevoColors.surface)
        .cornerRadius(12)
    }
    
    // MARK: - Completeness Section
    private var completenessSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Claim Completeness")
                    .font(.headline)
                    .foregroundStyle(.white)
                
                Spacer()
                
                Text("\(Int(completenessScore * 100))%")
                    .font(.title2.weight(.bold))
                    .foregroundStyle(completenessColor)
            }
            
            // Progress bar
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(DeevoColors.border)
                        .frame(height: 12)
                    
                    RoundedRectangle(cornerRadius: 8)
                        .fill(completenessColor)
                        .frame(width: geometry.size.width * completenessScore, height: 12)
                }
            }
            .frame(height: 12)
            
            // Checklist items
            VStack(alignment: .leading, spacing: 8) {
                CompletenessItem(title: "Vehicle photos captured", isComplete: true)
                CompletenessItem(title: "Damage assessment completed", isComplete: true)
                CompletenessItem(title: "Customer signature obtained", isComplete: true)
                CompletenessItem(title: "Odometer reading recorded", isComplete: false)
            }
        }
        .padding(16)
        .background(DeevoColors.surface)
        .cornerRadius(12)
    }
    
    private var completenessColor: Color {
        switch completenessScore {
        case 0..<0.5: return .red
        case 0.5..<0.8: return .orange
        default: return .green
        }
    }
    
    // MARK: - Generate Report Section
    private var generateReportSection: some View {
        Button(action: generateReport) {
            HStack {
                if isGenerating {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                } else {
                    Image(systemName: "doc.richtext.fill")
                }
                Text(isGenerating ? "Generating..." : "Generate PDF Report")
                    .fontWeight(.semibold)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(DeevoColors.accent)
            .foregroundStyle(.white)
            .cornerRadius(12)
        }
        .disabled(isGenerating)
    }
    
    // MARK: - Previous Reports Section
    private var previousReportsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Previous Reports")
                .font(.headline)
                .foregroundStyle(.white)
            
            ForEach(reports) { report in
                ReportRow(report: report) {
                    selectedReport = report
                    showPDFPreview = true
                }
            }
        }
        .padding(16)
        .background(DeevoColors.surface)
        .cornerRadius(12)
    }
    
    // MARK: - Submit Claim Section
    private var submitClaimSection: some View {
        Button(action: submitClaim) {
            HStack {
                Image(systemName: "paperplane.fill")
                Text("Submit Claim")
                    .fontWeight(.semibold)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(Color.green)
            .foregroundStyle(.white)
            .cornerRadius(12)
        }
    }
    
    // MARK: - Actions
    private func loadReports() {
        // Load previous reports from API
        Task {
            // Placeholder - would fetch from API
        }
    }
    
    private func calculateCompleteness() {
        // Calculate completeness based on evidence and checklist
        Task {
            // Placeholder - would calculate from claim data
        }
    }
    
    private func generateReport() {
        isGenerating = true
        
        Task {
            do {
                // Generate PDF report
                try await Task.sleep(nanoseconds: 2_000_000_000) // Simulate generation
                
                await MainActor.run {
                    isGenerating = false
                    // Add new report to list
                    let newReport = ClaimReport(
                        id: UUID().uuidString,
                        claimId: claimId,
                        generatedAt: Date(),
                        pageCount: 4,
                        fileSize: 1_250_000
                    )
                    reports.insert(newReport, at: 0)
                    selectedReport = newReport
                    showPDFPreview = true
                }
            } catch {
                await MainActor.run {
                    isGenerating = false
                }
            }
        }
    }
    
    private func submitClaim() {
        // Submit claim for review
        Task {
            // TODO: Implement submitClaim API call
            print("Submitting claim: \(claimId)")
        }
    }
}

// MARK: - Supporting Views

struct AISignalRow: View {
    let icon: String
    let color: Color
    let message: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundStyle(color)
            
            Text(message)
                .font(.subheadline)
                .foregroundStyle(DeevoColors.textSecondary)
            
            Spacer()
        }
        .padding(12)
        .background(DeevoColors.surfaceElevated)
        .cornerRadius(8)
    }
}

struct CompletenessItem: View {
    let title: String
    let isComplete: Bool
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: isComplete ? "checkmark.circle.fill" : "circle")
                .foregroundStyle(isComplete ? .green : DeevoColors.textTertiary)
            
            Text(title)
                .font(.subheadline)
                .foregroundStyle(isComplete ? DeevoColors.textSecondary : DeevoColors.textTertiary)
            
            Spacer()
            
            if !isComplete {
                Text("Required")
                    .font(.caption)
                    .foregroundStyle(.orange)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.orange.opacity(0.2))
                    .cornerRadius(4)
            }
        }
    }
}

struct ReportRow: View {
    let report: ClaimReport
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack {
                Image(systemName: "doc.fill")
                    .font(.title2)
                    .foregroundStyle(DeevoColors.accent)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("Report - \(report.generatedAt.formatted(date: .abbreviated, time: .shortened))")
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(.white)
                    
                    Text("\(report.pageCount) pages • \(report.fileSizeFormatted)")
                        .font(.caption)
                        .foregroundStyle(DeevoColors.textSecondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundStyle(DeevoColors.textTertiary)
            }
            .padding(12)
            .background(DeevoColors.surfaceElevated)
            .cornerRadius(8)
        }
    }
}

// MARK: - PDF Preview View

struct PDFPreviewView: View {
    let report: ClaimReport
    
    @Environment(\.dismiss) private var dismiss
    @State private var currentPage = 1
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Page indicator
                HStack {
                    Button(action: { currentPage = max(1, currentPage - 1) }) {
                        Image(systemName: "chevron.left")
                    }
                    .disabled(currentPage == 1)
                    
                    Text("Page \(currentPage) of \(report.pageCount)")
                        .font(.subheadline)
                    
                    Button(action: { currentPage = min(report.pageCount, currentPage + 1) }) {
                        Image(systemName: "chevron.right")
                    }
                    .disabled(currentPage == report.pageCount)
                }
                .padding()
                .background(Color(.systemGray6))
                
                // PDF preview placeholder
                ZStack {
                    Color(.systemGray5)
                    
                    VStack(spacing: 16) {
                        Image(systemName: "doc.richtext")
                            .font(.system(size: 60))
                            .foregroundStyle(.secondary)
                        
                        Text("PDF Preview")
                            .font(.headline)
                        
                        Text("Page \(currentPage)")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .navigationTitle("Report Preview")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") { dismiss() }
                }
                
                ToolbarItem(placement: .primaryAction) {
                    Menu {
                        Button(action: {}) {
                            Label("Share", systemImage: "square.and.arrow.up")
                        }
                        Button(action: {}) {
                            Label("Upload to Server", systemImage: "icloud.and.arrow.up")
                        }
                        Button(action: {}) {
                            Label("Save to Files", systemImage: "folder")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
        }
    }
}

// MARK: - Claim Report Model

struct ClaimReport: Identifiable {
    let id: String
    let claimId: String
    let generatedAt: Date
    let pageCount: Int
    let fileSize: Int
    
    var fileSizeFormatted: String {
        ByteCountFormatter.string(fromByteCount: Int64(fileSize), countStyle: .file)
    }
}

#Preview {
    ReportTab(
        claimId: "test-claim-id",
        claim: Claim(
            claimNumber: "CLM-2026-001",
            customerName: "John Doe",
            vehicleMake: "Toyota",
            vehicleModel: "Camry",
            vehicleYear: 2022
        )
    )
    .background(DeevoColors.backgroundDark)
}
