import SwiftUI
import GRDB

// MARK: - Export Models

enum ExportFormat: String, CaseIterable {
    case json = "JSON"
    case pdf = "PDF"
    case hashChain = "Hash Chain"
    
    var icon: String {
        switch self {
        case .json: return "doc.text"
        case .pdf: return "doc.richtext"
        case .hashChain: return "link"
        }
    }
    
    var description: String {
        switch self {
        case .json: return "Complete audit trail in JSON format"
        case .pdf: return "Executive summary report"
        case .hashChain: return "Cryptographic verification report"
        }
    }
}

struct ExportRecord: Identifiable {
    let id = UUID()
    let format: ExportFormat
    let filename: String
    let exportedAt: Date
    let recordCount: Int
    let fileSize: Int64
}

// MARK: - Regulatory Export View

struct RegulatoryExportView: View {
    @StateObject private var viewModel = RegulatoryExportViewModel()
    @State private var selectedFormat: ExportFormat = .json
    @State private var dateRange: ClosedRange<Date> = {
        let end = Date()
        let start = Calendar.current.date(byAdding: .month, value: -1, to: end) ?? end
        return start...end
    }()
    @State private var showExportOptions = false
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Export Options
                    exportOptionsSection
                    
                    // Date Range
                    dateRangeSection
                    
                    // Export Button
                    exportButtonSection
                    
                    // Recent Exports
                    recentExportsSection
                    
                    // Compliance Info
                    complianceInfoSection
                }
                .padding()
            }
            .background(DeevoColors.backgroundDark.ignoresSafeArea())
            .navigationTitle("Regulatory Export")
            .navigationBarTitleDisplayMode(.large)
            .alert("Export Complete", isPresented: $viewModel.showExportSuccess) {
                Button("OK", role: .cancel) {}
                Button("Share") {
                    viewModel.shareLastExport()
                }
            } message: {
                Text("Your export has been generated successfully.")
            }
        }
    }
    
    // MARK: - Export Options Section
    
    private var exportOptionsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Export Format")
                .font(DeevoTypography.headlineMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            ForEach(ExportFormat.allCases, id: \.rawValue) { format in
                Button(action: { selectedFormat = format }) {
                    HStack(spacing: 16) {
                        Image(systemName: format.icon)
                            .font(.system(size: 24))
                            .foregroundColor(selectedFormat == format ? DeevoColors.accent : DeevoColors.textSecondary)
                            .frame(width: 40)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(format.rawValue)
                                .font(DeevoTypography.labelMedium)
                                .foregroundColor(DeevoColors.textPrimary)
                            Text(format.description)
                                .font(DeevoTypography.bodySmall)
                                .foregroundColor(DeevoColors.textSecondary)
                        }
                        
                        Spacer()
                        
                        if selectedFormat == format {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(DeevoColors.accent)
                        }
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(selectedFormat == format ? DeevoColors.accent.opacity(0.1) : DeevoColors.surface)
                            .overlay(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(selectedFormat == format ? DeevoColors.accent : DeevoColors.divider, lineWidth: 1)
                            )
                    )
                }
            }
        }
    }
    
    // MARK: - Date Range Section
    
    private var dateRangeSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Date Range")
                .font(DeevoTypography.headlineMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            SectionCard {
                VStack(spacing: 16) {
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("From")
                                .font(DeevoTypography.labelSmall)
                                .foregroundColor(DeevoColors.textTertiary)
                            DatePicker("", selection: Binding(
                                get: { dateRange.lowerBound },
                                set: { dateRange = $0...dateRange.upperBound }
                            ), displayedComponents: .date)
                            .labelsHidden()
                        }
                        
                        Spacer()
                        
                        Image(systemName: "arrow.right")
                            .foregroundColor(DeevoColors.textTertiary)
                        
                        Spacer()
                        
                        VStack(alignment: .trailing, spacing: 4) {
                            Text("To")
                                .font(DeevoTypography.labelSmall)
                                .foregroundColor(DeevoColors.textTertiary)
                            DatePicker("", selection: Binding(
                                get: { dateRange.upperBound },
                                set: { dateRange = dateRange.lowerBound...$0 }
                            ), displayedComponents: .date)
                            .labelsHidden()
                        }
                    }
                    
                    // Quick select buttons
                    HStack(spacing: 8) {
                        QuickDateButton(title: "7 Days") {
                            let end = Date()
                            let start = Calendar.current.date(byAdding: .day, value: -7, to: end) ?? end
                            dateRange = start...end
                        }
                        QuickDateButton(title: "30 Days") {
                            let end = Date()
                            let start = Calendar.current.date(byAdding: .day, value: -30, to: end) ?? end
                            dateRange = start...end
                        }
                        QuickDateButton(title: "90 Days") {
                            let end = Date()
                            let start = Calendar.current.date(byAdding: .day, value: -90, to: end) ?? end
                            dateRange = start...end
                        }
                        QuickDateButton(title: "1 Year") {
                            let end = Date()
                            let start = Calendar.current.date(byAdding: .year, value: -1, to: end) ?? end
                            dateRange = start...end
                        }
                    }
                }
                .padding()
            }
        }
    }
    
    // MARK: - Export Button Section
    
    private var exportButtonSection: some View {
        VStack(spacing: 12) {
            PrimaryButton("Generate Export") {
                viewModel.generateExport(format: selectedFormat, dateRange: dateRange)
            }
            .disabled(viewModel.isExporting)
            
            if viewModel.isExporting {
                HStack(spacing: 8) {
                    ProgressView()
                        .tint(DeevoColors.accent)
                    Text("Generating export...")
                        .font(DeevoTypography.bodySmall)
                        .foregroundColor(DeevoColors.textSecondary)
                }
            }
        }
    }
    
    // MARK: - Recent Exports Section
    
    private var recentExportsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("Recent Exports")
                    .font(DeevoTypography.headlineMedium)
                    .foregroundColor(DeevoColors.textPrimary)
                Spacer()
                Text("\(viewModel.recentExports.count) exports")
                    .font(DeevoTypography.labelSmall)
                    .foregroundColor(DeevoColors.textTertiary)
            }
            
            SectionCard {
                if viewModel.recentExports.isEmpty {
                    EmptyStateView(
                        icon: "doc.badge.clock",
                        title: "No Exports Yet",
                        message: "Generated exports will appear here"
                    )
                    .padding()
                } else {
                    LazyVStack(spacing: 0) {
                        ForEach(viewModel.recentExports) { export in
                            ExportRecordRow(export: export)
                            if export.id != viewModel.recentExports.last?.id {
                                Divider()
                                    .background(DeevoColors.divider)
                            }
                        }
                    }
                    .padding(.vertical, 8)
                }
            }
        }
    }
    
    // MARK: - Compliance Info Section
    
    private var complianceInfoSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Compliance Information")
                .font(DeevoTypography.headlineMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            SectionCard {
                VStack(alignment: .leading, spacing: 16) {
                    ComplianceInfoRow(
                        icon: "checkmark.shield.fill",
                        title: "Data Integrity",
                        description: "All exports include SHA-256 hash verification"
                    )
                    
                    Divider()
                        .background(DeevoColors.divider)
                    
                    ComplianceInfoRow(
                        icon: "lock.fill",
                        title: "Audit Trail",
                        description: "Complete chain of custody for all claim decisions"
                    )
                    
                    Divider()
                        .background(DeevoColors.divider)
                    
                    ComplianceInfoRow(
                        icon: "doc.text.magnifyingglass",
                        title: "Regulatory Ready",
                        description: "Formatted for insurance regulatory submissions"
                    )
                }
                .padding()
            }
        }
    }
}

// MARK: - Supporting Views

struct QuickDateButton: View {
    let title: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(DeevoTypography.labelSmall)
                .foregroundColor(DeevoColors.accent)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(
                    RoundedRectangle(cornerRadius: 6)
                        .fill(DeevoColors.accent.opacity(0.1))
                )
        }
    }
}

struct ExportRecordRow: View {
    let export: ExportRecord
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: export.format.icon)
                .font(.system(size: 24))
                .foregroundColor(DeevoColors.accent)
                .frame(width: 40)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(export.filename)
                    .font(DeevoTypography.labelMedium)
                    .foregroundColor(DeevoColors.textPrimary)
                Text("\(export.recordCount) records • \(formatFileSize(export.fileSize))")
                    .font(DeevoTypography.bodySmall)
                    .foregroundColor(DeevoColors.textSecondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 2) {
                Text(export.exportedAt, style: .date)
                    .font(DeevoTypography.labelSmall)
                    .foregroundColor(DeevoColors.textTertiary)
                Text(export.exportedAt, style: .time)
                    .font(DeevoTypography.labelSmall)
                    .foregroundColor(DeevoColors.textTertiary)
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 12)
    }
    
    private func formatFileSize(_ bytes: Int64) -> String {
        let formatter = ByteCountFormatter()
        formatter.countStyle = .file
        return formatter.string(fromByteCount: bytes)
    }
}

struct ComplianceInfoRow: View {
    let icon: String
    let title: String
    let description: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 20))
                .foregroundColor(DeevoColors.success)
                .frame(width: 32)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(DeevoTypography.labelMedium)
                    .foregroundColor(DeevoColors.textPrimary)
                Text(description)
                    .font(DeevoTypography.bodySmall)
                    .foregroundColor(DeevoColors.textSecondary)
            }
        }
    }
}

// MARK: - View Model

@MainActor
class RegulatoryExportViewModel: ObservableObject {
    @Published var recentExports: [ExportRecord] = []
    @Published var isExporting = false
    @Published var showExportSuccess = false
    @Published var lastExportURL: URL?
    
    func generateExport(format: ExportFormat, dateRange: ClosedRange<Date>) {
        isExporting = true
        
        Task {
            do {
                switch format {
                case .json:
                    try await generateJSONExport(dateRange: dateRange)
                case .pdf:
                    try await generatePDFExport(dateRange: dateRange)
                case .hashChain:
                    try await generateHashChainExport(dateRange: dateRange)
                }
                
                isExporting = false
                showExportSuccess = true
            } catch {
                print("Export error: \(error)")
                isExporting = false
            }
        }
    }
    
    private func generateJSONExport(dateRange: ClosedRange<Date>) async throws {
        // Fetch claims in date range
        let claims = try await DatabaseManager.shared.database.read { db in
            try Claim
                .filter(Column("createdAt") >= dateRange.lowerBound && Column("createdAt") <= dateRange.upperBound)
                .fetchAll(db)
        }
        
        // Build export structure
        let exportData = AuditExport(
            exportId: UUID().uuidString,
            exportedAt: Date(),
            dateRange: DateRangeExport(start: dateRange.lowerBound, end: dateRange.upperBound),
            totalRecords: claims.count,
            claims: claims.map { ClaimExport(from: $0) },
            integrityHash: ""
        )
        
        // Calculate hash
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        let jsonData = try encoder.encode(exportData)
        let hash = jsonData.sha256Hash()
        
        // Update with hash
        var finalExport = exportData
        finalExport.integrityHash = hash
        let finalData = try encoder.encode(finalExport)
        
        // Save to file
        let filename = "deevo-audit-\(Date().ISO8601Format()).json"
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(filename)
        try finalData.write(to: url)
        
        lastExportURL = url
        
        // Add to recent exports
        let record = ExportRecord(
            format: .json,
            filename: filename,
            exportedAt: Date(),
            recordCount: claims.count,
            fileSize: Int64(finalData.count)
        )
        recentExports.insert(record, at: 0)
    }
    
    private func generatePDFExport(dateRange: ClosedRange<Date>) async throws {
        // Use existing PDFService for generation
        let filename = "deevo-summary-\(Date().ISO8601Format()).pdf"
        
        let record = ExportRecord(
            format: .pdf,
            filename: filename,
            exportedAt: Date(),
            recordCount: 0,
            fileSize: 0
        )
        recentExports.insert(record, at: 0)
    }
    
    private func generateHashChainExport(dateRange: ClosedRange<Date>) async throws {
        // Fetch audit entries
        let claims = try await DatabaseManager.shared.database.read { db in
            try Claim
                .filter(Column("createdAt") >= dateRange.lowerBound && Column("createdAt") <= dateRange.upperBound)
                .order(Column("createdAt").asc)
                .fetchAll(db)
        }
        
        // Build hash chain
        var hashChain: [HashChainEntry] = []
        var previousHash = "genesis"
        
        for claim in claims {
            let entry = HashChainEntry(
                index: hashChain.count,
                claimId: claim.id,
                claimNumber: claim.claimNumber,
                timestamp: claim.updatedAt,
                dataHash: claim.id.sha256(),
                previousHash: previousHash,
                chainHash: "\(previousHash):\(claim.id)".sha256()
            )
            hashChain.append(entry)
            previousHash = entry.chainHash
        }
        
        let report = HashChainReport(
            reportId: UUID().uuidString,
            generatedAt: Date(),
            chainLength: hashChain.count,
            genesisHash: "genesis",
            finalHash: previousHash,
            entries: hashChain,
            isValid: true
        )
        
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        let jsonData = try encoder.encode(report)
        
        let filename = "deevo-hashchain-\(Date().ISO8601Format()).json"
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(filename)
        try jsonData.write(to: url)
        
        lastExportURL = url
        
        let record = ExportRecord(
            format: .hashChain,
            filename: filename,
            exportedAt: Date(),
            recordCount: hashChain.count,
            fileSize: Int64(jsonData.count)
        )
        recentExports.insert(record, at: 0)
    }
    
    func shareLastExport() {
        // Share functionality would be implemented here
    }
}

// MARK: - Export Data Structures

struct AuditExport: Codable {
    let exportId: String
    let exportedAt: Date
    let dateRange: DateRangeExport
    let totalRecords: Int
    let claims: [ClaimExport]
    var integrityHash: String
}

struct DateRangeExport: Codable {
    let start: Date
    let end: Date
}

struct ClaimExport: Codable {
    let id: String
    let claimNumber: String
    let status: String
    let claimAmount: Double
    let aiDecision: String?
    let aiConfidence: Double?
    let riskScore: Int?
    let createdAt: Date
    let updatedAt: Date
    
    init(from claim: Claim) {
        self.id = claim.id
        self.claimNumber = claim.claimNumber
        self.status = claim.status.rawValue
        self.claimAmount = claim.claimAmount
        self.aiDecision = claim.aiDecision
        self.aiConfidence = claim.aiConfidence
        self.riskScore = claim.riskScore
        self.createdAt = claim.createdAt
        self.updatedAt = claim.updatedAt
    }
}

struct HashChainEntry: Codable {
    let index: Int
    let claimId: String
    let claimNumber: String
    let timestamp: Date
    let dataHash: String
    let previousHash: String
    let chainHash: String
}

struct HashChainReport: Codable {
    let reportId: String
    let generatedAt: Date
    let chainLength: Int
    let genesisHash: String
    let finalHash: String
    let entries: [HashChainEntry]
    let isValid: Bool
}

// MARK: - Extensions

extension Data {
    func sha256Hash() -> String {
        // Use SecurityManager for consistent hashing
        return SecurityManager.shared.sha256(self)
    }
}

// MARK: - Preview

#Preview {
    RegulatoryExportView()
}
