import SwiftUI
import PDFKit

/// PDF generation service with Deevo Sentinel branding
/// Generates professional PDF reports for claims, inspections, and audits
final class PDFService {
    
    // MARK: - Brand Constants
    
    private struct Brand {
        static let companyName = "Deevo Sentinel"
        static let tagline = "Sovereign Claims Decision Infrastructure"
        static let footer = "Powered by Deevo Analytics"
        static let confidential = "CONFIDENTIAL - For Authorized Use Only"
        
        // Colors (CGColor for PDF rendering)
        static let primaryColor = CGColor(red: 11/255, green: 31/255, blue: 58/255, alpha: 1) // #0B1F3A
        static let secondaryColor = CGColor(red: 31/255, green: 60/255, blue: 136/255, alpha: 1) // #1F3C88
        static let accentColor = CGColor(red: 201/255, green: 162/255, blue: 39/255, alpha: 1) // #C9A227
        static let textColor = CGColor(red: 0.1, green: 0.1, blue: 0.1, alpha: 1)
        static let lightGray = CGColor(red: 0.6, green: 0.6, blue: 0.6, alpha: 1)
    }
    
    // MARK: - Page Layout
    
    private struct PageLayout {
        static let pageWidth: CGFloat = 612 // US Letter
        static let pageHeight: CGFloat = 792
        static let margin: CGFloat = 50
        static let headerHeight: CGFloat = 80
        static let footerHeight: CGFloat = 50
        static let contentWidth: CGFloat = pageWidth - (margin * 2)
        static let contentStartY: CGFloat = pageHeight - margin - headerHeight
    }
    
    // MARK: - Shared Instance
    
    static let shared = PDFService()
    private init() {}
    
    // MARK: - Public Methods
    
    /// Generate a claim summary PDF
    func generateClaimSummaryPDF(claim: Claim, inspections: [Inspection] = [], mediaAssets: [MediaAsset] = []) -> Data? {
        let pdfMetaData = [
            kCGPDFContextCreator: Brand.companyName,
            kCGPDFContextAuthor: Brand.companyName,
            kCGPDFContextTitle: "Claim Summary - \(claim.claimNumber)",
            kCGPDFContextSubject: "Insurance Claim Documentation"
        ]
        
        let format = UIGraphicsPDFRendererFormat()
        format.documentInfo = pdfMetaData as [String: Any]
        
        let pageRect = CGRect(x: 0, y: 0, width: PageLayout.pageWidth, height: PageLayout.pageHeight)
        let renderer = UIGraphicsPDFRenderer(bounds: pageRect, format: format)
        
        let data = renderer.pdfData { context in
            context.beginPage()
            
            var yPosition = drawHeader(context: context.cgContext, title: "Claim Summary Report")
            
            // Claim Information Section
            yPosition = drawSectionHeader(context: context.cgContext, title: "Claim Information", yPosition: yPosition)
            yPosition = drawKeyValue(context: context.cgContext, key: "Claim Number", value: claim.claimNumber, yPosition: yPosition)
            yPosition = drawKeyValue(context: context.cgContext, key: "Policy Number", value: claim.policyNumber ?? "N/A", yPosition: yPosition)
            yPosition = drawKeyValue(context: context.cgContext, key: "Status", value: claim.status.rawValue.capitalized, yPosition: yPosition)
            yPosition = drawKeyValue(context: context.cgContext, key: "Priority", value: claim.priority.rawValue.capitalized, yPosition: yPosition)
            yPosition = drawKeyValue(context: context.cgContext, key: "Created", value: formatDate(claim.createdAt), yPosition: yPosition)
            
            if let description = claim.claimDescription {
                yPosition -= 10
                yPosition = drawSectionHeader(context: context.cgContext, title: "Description", yPosition: yPosition)
                yPosition = drawParagraph(context: context.cgContext, text: description, yPosition: yPosition)
            }
            
            // Inspections Section
            if !inspections.isEmpty {
                yPosition -= 10
                yPosition = drawSectionHeader(context: context.cgContext, title: "Inspections (\(inspections.count))", yPosition: yPosition)
                for inspection in inspections {
                    yPosition = drawKeyValue(context: context.cgContext, key: inspection.templateName ?? "Unknown Template", value: inspection.status.rawValue.capitalized, yPosition: yPosition)
                }
            }
            
            // Media Assets Section
            if !mediaAssets.isEmpty {
                yPosition -= 10
                yPosition = drawSectionHeader(context: context.cgContext, title: "Evidence Attachments (\(mediaAssets.count))", yPosition: yPosition)
                for asset in mediaAssets {
                    let typeIcon = asset.type == .photo ? "📷" : "🎥"
                    yPosition = drawKeyValue(context: context.cgContext, key: "\(typeIcon) \(asset.filename)", value: formatDate(asset.capturedAt), yPosition: yPosition)
                }
            }
            
            drawFooter(context: context.cgContext, pageNumber: 1, totalPages: 1)
        }
        
        return data
    }
    
    /// Generate an inspection report PDF
    func generateInspectionReportPDF(inspection: Inspection, claim: Claim, responses: [String: Any] = [:]) -> Data? {
        let pdfMetaData = [
            kCGPDFContextCreator: Brand.companyName,
            kCGPDFContextAuthor: Brand.companyName,
            kCGPDFContextTitle: "Inspection Report - \(inspection.templateName ?? "Unknown")",
            kCGPDFContextSubject: "Field Inspection Documentation"
        ]
        
        let format = UIGraphicsPDFRendererFormat()
        format.documentInfo = pdfMetaData as [String: Any]
        
        let pageRect = CGRect(x: 0, y: 0, width: PageLayout.pageWidth, height: PageLayout.pageHeight)
        let renderer = UIGraphicsPDFRenderer(bounds: pageRect, format: format)
        
        let data = renderer.pdfData { context in
            context.beginPage()
            
            var yPosition = drawHeader(context: context.cgContext, title: "Inspection Report")
            
            // Inspection Details
            yPosition = drawSectionHeader(context: context.cgContext, title: "Inspection Details", yPosition: yPosition)
            yPosition = drawKeyValue(context: context.cgContext, key: "Template", value: inspection.templateName ?? "Unknown Template", yPosition: yPosition)
            yPosition = drawKeyValue(context: context.cgContext, key: "Status", value: inspection.status.rawValue.capitalized, yPosition: yPosition)
            yPosition = drawKeyValue(context: context.cgContext, key: "Started", value: formatDate(inspection.startedAt), yPosition: yPosition)
            if let completedAt = inspection.completedAt {
                yPosition = drawKeyValue(context: context.cgContext, key: "Completed", value: formatDate(completedAt), yPosition: yPosition)
            }
            
            // Associated Claim
            yPosition -= 10
            yPosition = drawSectionHeader(context: context.cgContext, title: "Associated Claim", yPosition: yPosition)
            yPosition = drawKeyValue(context: context.cgContext, key: "Claim Number", value: claim.claimNumber, yPosition: yPosition)
            yPosition = drawKeyValue(context: context.cgContext, key: "Policy Number", value: claim.policyNumber ?? "N/A", yPosition: yPosition)
            
            // Inspection Responses
            if !responses.isEmpty {
                yPosition -= 10
                yPosition = drawSectionHeader(context: context.cgContext, title: "Inspection Responses", yPosition: yPosition)
                for (key, value) in responses {
                    yPosition = drawKeyValue(context: context.cgContext, key: key, value: String(describing: value), yPosition: yPosition)
                }
            }
            
            drawFooter(context: context.cgContext, pageNumber: 1, totalPages: 1)
        }
        
        return data
    }
    
    /// Generate an audit trail PDF
    func generateAuditTrailPDF(events: [AuditEvent], claimNumber: String) -> Data? {
        let pdfMetaData = [
            kCGPDFContextCreator: Brand.companyName,
            kCGPDFContextAuthor: Brand.companyName,
            kCGPDFContextTitle: "Audit Trail - \(claimNumber)",
            kCGPDFContextSubject: "Regulatory Audit Documentation"
        ]
        
        let format = UIGraphicsPDFRendererFormat()
        format.documentInfo = pdfMetaData as [String: Any]
        
        let pageRect = CGRect(x: 0, y: 0, width: PageLayout.pageWidth, height: PageLayout.pageHeight)
        let renderer = UIGraphicsPDFRenderer(bounds: pageRect, format: format)
        
        let data = renderer.pdfData { context in
            var pageNumber = 1
            let totalPages = 1 // Single page for now
            
            context.beginPage()
            var yPosition = drawHeader(context: context.cgContext, title: "Audit Trail Report")
            
            // Report Info
            yPosition = drawSectionHeader(context: context.cgContext, title: "Report Information", yPosition: yPosition)
            yPosition = drawKeyValue(context: context.cgContext, key: "Claim Number", value: claimNumber, yPosition: yPosition)
            yPosition = drawKeyValue(context: context.cgContext, key: "Generated", value: formatDate(Date()), yPosition: yPosition)
            yPosition = drawKeyValue(context: context.cgContext, key: "Total Events", value: "\(events.count)", yPosition: yPosition)
            
            // Audit Events
            yPosition -= 10
            yPosition = drawSectionHeader(context: context.cgContext, title: "Audit Events", yPosition: yPosition)
            
            for event in events {
                // Check if we need a new page
                if yPosition < PageLayout.footerHeight + 80 {
                    drawFooter(context: context.cgContext, pageNumber: pageNumber, totalPages: totalPages)
                    context.beginPage()
                    pageNumber += 1
                    yPosition = drawHeader(context: context.cgContext, title: "Audit Trail Report (continued)")
                }
                
                yPosition = drawAuditEvent(context: context.cgContext, event: event, yPosition: yPosition)
            }
            
            drawFooter(context: context.cgContext, pageNumber: pageNumber, totalPages: pageNumber)
        }
        
        return data
    }
    
    // MARK: - Private Drawing Methods
    
    private func drawHeader(context: CGContext, title: String) -> CGFloat {
        let headerRect = CGRect(
            x: 0,
            y: PageLayout.pageHeight - PageLayout.margin - PageLayout.headerHeight,
            width: PageLayout.pageWidth,
            height: PageLayout.headerHeight
        )
        
        // Header background bar
        context.setFillColor(Brand.primaryColor)
        context.fill(CGRect(x: 0, y: headerRect.minY, width: PageLayout.pageWidth, height: 4))
        
        // Company name
        let companyAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 24, weight: .bold),
            .foregroundColor: UIColor(cgColor: Brand.primaryColor)
        ]
        let companyString = NSAttributedString(string: Brand.companyName, attributes: companyAttributes)
        companyString.draw(at: CGPoint(x: PageLayout.margin, y: PageLayout.pageHeight - PageLayout.margin - 30))
        
        // Tagline
        let taglineAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 10, weight: .medium),
            .foregroundColor: UIColor(cgColor: Brand.accentColor)
        ]
        let taglineString = NSAttributedString(string: Brand.tagline.uppercased(), attributes: taglineAttributes)
        taglineString.draw(at: CGPoint(x: PageLayout.margin, y: PageLayout.pageHeight - PageLayout.margin - 45))
        
        // Report title
        let titleAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 18, weight: .semibold),
            .foregroundColor: UIColor(cgColor: Brand.secondaryColor)
        ]
        let titleString = NSAttributedString(string: title, attributes: titleAttributes)
        titleString.draw(at: CGPoint(x: PageLayout.margin, y: PageLayout.pageHeight - PageLayout.margin - 70))
        
        // Accent line under header
        context.setFillColor(Brand.accentColor)
        context.fill(CGRect(x: PageLayout.margin, y: headerRect.minY - 5, width: PageLayout.contentWidth, height: 2))
        
        return headerRect.minY - 25
    }
    
    private func drawFooter(context: CGContext, pageNumber: Int, totalPages: Int) {
        let footerY: CGFloat = PageLayout.margin
        
        // Footer line
        context.setFillColor(Brand.lightGray)
        context.fill(CGRect(x: PageLayout.margin, y: footerY + 35, width: PageLayout.contentWidth, height: 1))
        
        // Powered by text
        let footerAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 9, weight: .regular),
            .foregroundColor: UIColor.gray
        ]
        let footerString = NSAttributedString(string: Brand.footer, attributes: footerAttributes)
        footerString.draw(at: CGPoint(x: PageLayout.margin, y: footerY + 15))
        
        // Confidential notice
        let confidentialAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 8, weight: .medium),
            .foregroundColor: UIColor.darkGray
        ]
        let confidentialString = NSAttributedString(string: Brand.confidential, attributes: confidentialAttributes)
        let confidentialSize = confidentialString.size()
        confidentialString.draw(at: CGPoint(x: (PageLayout.pageWidth - confidentialSize.width) / 2, y: footerY))
        
        // Page number
        let pageAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 9, weight: .regular),
            .foregroundColor: UIColor.gray
        ]
        let pageString = NSAttributedString(string: "Page \(pageNumber) of \(totalPages)", attributes: pageAttributes)
        let pageSize = pageString.size()
        pageString.draw(at: CGPoint(x: PageLayout.pageWidth - PageLayout.margin - pageSize.width, y: footerY + 15))
    }
    
    private func drawSectionHeader(context: CGContext, title: String, yPosition: CGFloat) -> CGFloat {
        let attributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 14, weight: .bold),
            .foregroundColor: UIColor(cgColor: Brand.primaryColor)
        ]
        let string = NSAttributedString(string: title, attributes: attributes)
        string.draw(at: CGPoint(x: PageLayout.margin, y: yPosition))
        
        // Underline
        context.setFillColor(Brand.accentColor)
        context.fill(CGRect(x: PageLayout.margin, y: yPosition - 5, width: 60, height: 2))
        
        return yPosition - 25
    }
    
    private func drawKeyValue(context: CGContext, key: String, value: String?, yPosition: CGFloat) -> CGFloat {
        let displayValue = value ?? "N/A"
        let keyAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 11, weight: .medium),
            .foregroundColor: UIColor.darkGray
        ]
        let keyString = NSAttributedString(string: "\(key):", attributes: keyAttributes)
        keyString.draw(at: CGPoint(x: PageLayout.margin + 10, y: yPosition))
        
        let valueAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 11, weight: .regular),
            .foregroundColor: UIColor.black
        ]
        let valueString = NSAttributedString(string: displayValue, attributes: valueAttributes)
        valueString.draw(at: CGPoint(x: PageLayout.margin + 150, y: yPosition))
        
        return yPosition - 18
    }
    
    private func drawParagraph(context: CGContext, text: String, yPosition: CGFloat) -> CGFloat {
        let attributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 11, weight: .regular),
            .foregroundColor: UIColor.black
        ]
        
        let paragraphStyle = NSMutableParagraphStyle()
        paragraphStyle.lineBreakMode = .byWordWrapping
        
        let attributedString = NSAttributedString(string: text, attributes: attributes)
        let textRect = CGRect(
            x: PageLayout.margin + 10,
            y: yPosition - 60,
            width: PageLayout.contentWidth - 20,
            height: 60
        )
        attributedString.draw(in: textRect)
        
        return yPosition - 70
    }
    
    private func drawAuditEvent(context: CGContext, event: AuditEvent, yPosition: CGFloat) -> CGFloat {
        // Event type badge
        let badgeAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 9, weight: .bold),
            .foregroundColor: UIColor(cgColor: Brand.accentColor)
        ]
        let badgeString = NSAttributedString(string: event.eventType.uppercased(), attributes: badgeAttributes)
        badgeString.draw(at: CGPoint(x: PageLayout.margin + 10, y: yPosition))
        
        // Timestamp
        let timeAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 9, weight: .regular),
            .foregroundColor: UIColor.gray
        ]
        let timeString = NSAttributedString(string: formatDate(event.timestamp), attributes: timeAttributes)
        let timeSize = timeString.size()
        timeString.draw(at: CGPoint(x: PageLayout.pageWidth - PageLayout.margin - timeSize.width, y: yPosition))
        
        // Description
        if let description = event.description {
            let descAttributes: [NSAttributedString.Key: Any] = [
                .font: UIFont.systemFont(ofSize: 10, weight: .regular),
                .foregroundColor: UIColor.darkGray
            ]
            let descString = NSAttributedString(string: description, attributes: descAttributes)
            descString.draw(at: CGPoint(x: PageLayout.margin + 10, y: yPosition - 15))
        }
        
        // Hash (truncated)
        let hashAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.monospacedSystemFont(ofSize: 8, weight: .regular),
            .foregroundColor: UIColor.lightGray
        ]
        let truncatedHash = String(event.eventHash.prefix(32)) + "..."
        let hashString = NSAttributedString(string: "Hash: \(truncatedHash)", attributes: hashAttributes)
        hashString.draw(at: CGPoint(x: PageLayout.margin + 10, y: yPosition - 30))
        
        // Separator line
        context.setFillColor(CGColor(gray: 0.9, alpha: 1))
        context.fill(CGRect(x: PageLayout.margin + 10, y: yPosition - 45, width: PageLayout.contentWidth - 20, height: 1))
        
        return yPosition - 55
    }
    
    // MARK: - Helpers
    
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
    
    private func formatDate(_ date: Date?) -> String {
        guard let date = date else { return "N/A" }
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

// MARK: - PDF Export Extension

extension PDFService {
    /// Export PDF data to a temporary file and return the URL
    func exportToFile(data: Data, filename: String) -> URL? {
        let tempDir = FileManager.default.temporaryDirectory
        let fileURL = tempDir.appendingPathComponent(filename).appendingPathExtension("pdf")
        
        do {
            try data.write(to: fileURL)
            return fileURL
        } catch {
            print("[PDFService] Failed to write PDF: \(error)")
            return nil
        }
    }
}
