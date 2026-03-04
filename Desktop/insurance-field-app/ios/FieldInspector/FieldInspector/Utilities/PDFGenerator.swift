import Foundation
import PDFKit
import UIKit

/// Generates PDF reports for claims and inspections
class PDFGenerator {
    
    // MARK: - Properties
    
    private let pageWidth: CGFloat = 612 // US Letter width in points
    private let pageHeight: CGFloat = 792 // US Letter height in points
    private let margin: CGFloat = 50
    
    // MARK: - Public Methods
    
    /// Generate a PDF report for a claim
    func generateClaimReport(
        claim: Claim,
        inspection: Inspection?,
        fields: [InspectionField],
        mediaAssets: [MediaAsset]
    ) -> Data? {
        let pdfMetaData = [
            kCGPDFContextCreator: "Deevo Sentinel",
            kCGPDFContextAuthor: "Deevo Analytics",
            kCGPDFContextTitle: "Claim Report - \(claim.claimNumber)"
        ]
        
        let format = UIGraphicsPDFRendererFormat()
        format.documentInfo = pdfMetaData as [String: Any]
        
        let pageRect = CGRect(x: 0, y: 0, width: pageWidth, height: pageHeight)
        let renderer = UIGraphicsPDFRenderer(bounds: pageRect, format: format)
        
        let data = renderer.pdfData { context in
            // Page 1: Cover and Summary
            context.beginPage()
            var yPosition = drawHeader(context: context, title: "Claim Inspection Report")
            yPosition = drawClaimSummary(context: context, claim: claim, startY: yPosition)
            
            // Page 2: Vehicle and Incident Details
            context.beginPage()
            yPosition = drawHeader(context: context, title: "Vehicle & Incident Details")
            yPosition = drawVehicleInfo(context: context, claim: claim, startY: yPosition)
            yPosition = drawIncidentInfo(context: context, claim: claim, startY: yPosition)
            
            // Page 3: Inspection Details
            if !fields.isEmpty {
                context.beginPage()
                yPosition = drawHeader(context: context, title: "Inspection Details")
                yPosition = drawInspectionFields(context: context, fields: fields, startY: yPosition)
            }
            
            // Page 4: Evidence Summary
            if !mediaAssets.isEmpty {
                context.beginPage()
                yPosition = drawHeader(context: context, title: "Evidence Summary")
                yPosition = drawEvidenceSummary(context: context, assets: mediaAssets, startY: yPosition)
            }
            
            // Final Page: Footer
            drawFooter(context: context, claimNumber: claim.claimNumber)
        }
        
        return data
    }
    
    // MARK: - Private Drawing Methods
    
    private func drawHeader(context: UIGraphicsPDFRendererContext, title: String) -> CGFloat {
        let titleFont = UIFont.boldSystemFont(ofSize: 24)
        let titleAttributes: [NSAttributedString.Key: Any] = [
            .font: titleFont,
            .foregroundColor: UIColor.black
        ]
        
        let titleRect = CGRect(x: margin, y: margin, width: pageWidth - 2 * margin, height: 40)
        title.draw(in: titleRect, withAttributes: titleAttributes)
        
        // Draw line under header
        let linePath = UIBezierPath()
        linePath.move(to: CGPoint(x: margin, y: margin + 45))
        linePath.addLine(to: CGPoint(x: pageWidth - margin, y: margin + 45))
        UIColor.blue.setStroke()
        linePath.lineWidth = 2
        linePath.stroke()
        
        // Date
        let dateFont = UIFont.systemFont(ofSize: 10)
        let dateAttributes: [NSAttributedString.Key: Any] = [
            .font: dateFont,
            .foregroundColor: UIColor.gray
        ]
        let dateString = "Generated: \(Date().formatted(date: .long, time: .shortened))"
        let dateRect = CGRect(x: margin, y: margin + 50, width: pageWidth - 2 * margin, height: 20)
        dateString.draw(in: dateRect, withAttributes: dateAttributes)
        
        return margin + 80
    }
    
    private func drawClaimSummary(context: UIGraphicsPDFRendererContext, claim: Claim, startY: CGFloat) -> CGFloat {
        var yPosition = startY
        
        yPosition = drawSectionTitle("Claim Information", at: yPosition)
        yPosition = drawLabelValue("Claim Number:", claim.claimNumber, at: yPosition)
        yPosition = drawLabelValue("Status:", claim.status.displayName, at: yPosition)
        yPosition = drawLabelValue("Priority:", claim.priority.displayName, at: yPosition)
        yPosition = drawLabelValue("Customer:", claim.customerName, at: yPosition)
        
        if let phone = claim.customerPhone {
            yPosition = drawLabelValue("Phone:", phone, at: yPosition)
        }
        if let email = claim.customerEmail {
            yPosition = drawLabelValue("Email:", email, at: yPosition)
        }
        
        return yPosition + 20
    }
    
    private func drawVehicleInfo(context: UIGraphicsPDFRendererContext, claim: Claim, startY: CGFloat) -> CGFloat {
        var yPosition = startY
        
        yPosition = drawSectionTitle("Vehicle Information", at: yPosition)
        yPosition = drawLabelValue("Vehicle:", claim.vehicleDescription, at: yPosition)
        
        if let vin = claim.vehicleVin {
            yPosition = drawLabelValue("VIN:", vin, at: yPosition)
        }
        if let plate = claim.vehiclePlate {
            yPosition = drawLabelValue("License Plate:", plate, at: yPosition)
        }
        if let color = claim.vehicleColor {
            yPosition = drawLabelValue("Color:", color, at: yPosition)
        }
        
        return yPosition + 20
    }
    
    private func drawIncidentInfo(context: UIGraphicsPDFRendererContext, claim: Claim, startY: CGFloat) -> CGFloat {
        var yPosition = startY
        
        yPosition = drawSectionTitle("Incident Details", at: yPosition)
        
        if let date = claim.incidentDate {
            yPosition = drawLabelValue("Date:", date.formatted(date: .long, time: .shortened), at: yPosition)
        }
        yPosition = drawLabelValue("Location:", claim.fullAddress, at: yPosition)
        
        if let description = claim.incidentDescription {
            yPosition = drawLabelValue("Description:", "", at: yPosition)
            yPosition = drawParagraph(description, at: yPosition)
        }
        
        if let damage = claim.estimatedDamage {
            yPosition = drawLabelValue("Estimated Damage:", String(format: "$%.2f", damage), at: yPosition)
        }
        
        return yPosition + 20
    }
    
    private func drawInspectionFields(context: UIGraphicsPDFRendererContext, fields: [InspectionField], startY: CGFloat) -> CGFloat {
        var yPosition = startY
        
        // Group fields by section
        let grouped = Dictionary(grouping: fields) { $0.sectionKey }
        
        for (section, sectionFields) in grouped.sorted(by: { $0.key < $1.key }) {
            yPosition = drawSectionTitle(formatSectionName(section), at: yPosition)
            
            for field in sectionFields.sorted(by: { $0.displayOrder < $1.displayOrder }) {
                let value = field.value ?? "Not provided"
                yPosition = drawLabelValue("\(formatFieldName(field.fieldKey)):", value, at: yPosition)
                
                // Check if we need a new page
                if yPosition > pageHeight - 100 {
                    context.beginPage()
                    yPosition = margin + 20
                }
            }
            
            yPosition += 10
        }
        
        return yPosition
    }
    
    private func drawEvidenceSummary(context: UIGraphicsPDFRendererContext, assets: [MediaAsset], startY: CGFloat) -> CGFloat {
        var yPosition = startY
        
        let photoCount = assets.filter { $0.type == .photo }.count
        let videoCount = assets.filter { $0.type == .video }.count
        let docCount = assets.filter { $0.type == .document }.count
        
        yPosition = drawSectionTitle("Evidence Summary", at: yPosition)
        yPosition = drawLabelValue("Total Photos:", "\(photoCount)", at: yPosition)
        yPosition = drawLabelValue("Total Videos:", "\(videoCount)", at: yPosition)
        yPosition = drawLabelValue("Total Documents:", "\(docCount)", at: yPosition)
        
        yPosition += 20
        yPosition = drawSectionTitle("Evidence List", at: yPosition)
        
        for (index, asset) in assets.enumerated() {
            let info = "\(index + 1). \(asset.filename) (\(asset.type.displayName)) - \(asset.fileSizeFormatted)"
            yPosition = drawParagraph(info, at: yPosition)
            
            if !asset.tags.isEmpty {
                yPosition = drawParagraph("   Tags: \(asset.tags.joined(separator: ", "))", at: yPosition)
            }
            
            // Check if we need a new page
            if yPosition > pageHeight - 100 {
                context.beginPage()
                yPosition = margin + 20
            }
        }
        
        return yPosition
    }
    
    private func drawFooter(context: UIGraphicsPDFRendererContext, claimNumber: String) {
        let footerFont = UIFont.systemFont(ofSize: 10)
        let footerAttributes: [NSAttributedString.Key: Any] = [
            .font: footerFont,
            .foregroundColor: UIColor.gray
        ]
        
        let footerText = "Deevo Sentinel - Claim \(claimNumber) - Confidential"
        let footerRect = CGRect(x: margin, y: pageHeight - 40, width: pageWidth - 2 * margin, height: 20)
        footerText.draw(in: footerRect, withAttributes: footerAttributes)
    }
    
    // MARK: - Helper Methods
    
    private func drawSectionTitle(_ title: String, at yPosition: CGFloat) -> CGFloat {
        let font = UIFont.boldSystemFont(ofSize: 14)
        let attributes: [NSAttributedString.Key: Any] = [
            .font: font,
            .foregroundColor: UIColor.darkGray
        ]
        
        let rect = CGRect(x: margin, y: yPosition, width: pageWidth - 2 * margin, height: 25)
        title.draw(in: rect, withAttributes: attributes)
        
        return yPosition + 25
    }
    
    private func drawLabelValue(_ label: String, _ value: String, at yPosition: CGFloat) -> CGFloat {
        let labelFont = UIFont.boldSystemFont(ofSize: 11)
        let valueFont = UIFont.systemFont(ofSize: 11)
        
        let labelAttributes: [NSAttributedString.Key: Any] = [
            .font: labelFont,
            .foregroundColor: UIColor.black
        ]
        let valueAttributes: [NSAttributedString.Key: Any] = [
            .font: valueFont,
            .foregroundColor: UIColor.black
        ]
        
        let labelRect = CGRect(x: margin, y: yPosition, width: 150, height: 18)
        label.draw(in: labelRect, withAttributes: labelAttributes)
        
        let valueRect = CGRect(x: margin + 150, y: yPosition, width: pageWidth - 2 * margin - 150, height: 18)
        value.draw(in: valueRect, withAttributes: valueAttributes)
        
        return yPosition + 18
    }
    
    private func drawParagraph(_ text: String, at yPosition: CGFloat) -> CGFloat {
        let font = UIFont.systemFont(ofSize: 11)
        let attributes: [NSAttributedString.Key: Any] = [
            .font: font,
            .foregroundColor: UIColor.black
        ]
        
        let maxWidth = pageWidth - 2 * margin
        let textSize = text.boundingRect(
            with: CGSize(width: maxWidth, height: .greatestFiniteMagnitude),
            options: .usesLineFragmentOrigin,
            attributes: attributes,
            context: nil
        )
        
        let rect = CGRect(x: margin, y: yPosition, width: maxWidth, height: textSize.height + 5)
        text.draw(in: rect, withAttributes: attributes)
        
        return yPosition + textSize.height + 5
    }
    
    private func formatSectionName(_ key: String) -> String {
        key.split(separator: "_")
            .map { $0.capitalized }
            .joined(separator: " ")
    }
    
    private func formatFieldName(_ key: String) -> String {
        key.split(separator: "_")
            .map { $0.capitalized }
            .joined(separator: " ")
    }
}
