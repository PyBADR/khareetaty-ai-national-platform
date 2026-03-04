import XCTest
@testable import DeevoSentinel

final class SchemaValidationTests: XCTestCase {
    
    // MARK: - AI Decision Schema Tests
    
    func testValidAIDecision() {
        // Given
        let decision = AIDecision(
            recommendedAction: "approve",
            confidence: 0.85,
            reasonCodes: ["DAMAGE_CONSISTENT", "DOCS_COMPLETE"],
            keyFindings: ["Front bumper damage matches reported incident"],
            missingInfo: [],
            nextSteps: ["Proceed with settlement calculation"],
            policyNotes: ["Deductible applies: $500"],
            auditSummary: "AI analysis completed with high confidence"
        )
        
        // When
        let (isValid, errors) = validateAIDecision(decision)
        
        // Then
        XCTAssertTrue(isValid)
        XCTAssertTrue(errors.isEmpty)
    }
    
    func testInvalidRecommendedAction() {
        // Given
        let decision = AIDecision(
            recommendedAction: "invalid_action",
            confidence: 0.85,
            reasonCodes: ["TEST"],
            keyFindings: ["Test finding"],
            missingInfo: [],
            nextSteps: ["Test step"],
            policyNotes: [],
            auditSummary: "Test summary"
        )
        
        // When
        let (isValid, errors) = validateAIDecision(decision)
        
        // Then
        XCTAssertFalse(isValid)
        XCTAssertTrue(errors.contains { $0.contains("Invalid recommended_action") })
    }
    
    func testInvalidConfidenceRange() {
        // Given - Confidence > 1.0
        let decision1 = AIDecision(
            recommendedAction: "approve",
            confidence: 1.5,
            reasonCodes: ["TEST"],
            keyFindings: ["Test"],
            missingInfo: [],
            nextSteps: ["Test"],
            policyNotes: [],
            auditSummary: "Test"
        )
        
        // When
        let (isValid1, errors1) = validateAIDecision(decision1)
        
        // Then
        XCTAssertFalse(isValid1)
        XCTAssertTrue(errors1.contains { $0.contains("Confidence must be between 0.0 and 1.0") })
        
        // Given - Confidence < 0.0
        let decision2 = AIDecision(
            recommendedAction: "approve",
            confidence: -0.5,
            reasonCodes: ["TEST"],
            keyFindings: ["Test"],
            missingInfo: [],
            nextSteps: ["Test"],
            policyNotes: [],
            auditSummary: "Test"
        )
        
        // When
        let (isValid2, errors2) = validateAIDecision(decision2)
        
        // Then
        XCTAssertFalse(isValid2)
        XCTAssertTrue(errors2.contains { $0.contains("Confidence must be between 0.0 and 1.0") })
    }
    
    func testEmptyRequiredArrays() {
        // Given - Empty reason_codes
        let decision = AIDecision(
            recommendedAction: "approve",
            confidence: 0.85,
            reasonCodes: [],
            keyFindings: ["Test"],
            missingInfo: [],
            nextSteps: ["Test"],
            policyNotes: [],
            auditSummary: "Test"
        )
        
        // When
        let (isValid, errors) = validateAIDecision(decision)
        
        // Then
        XCTAssertFalse(isValid)
        XCTAssertTrue(errors.contains { $0.contains("reason_codes cannot be empty") })
    }
    
    func testEmptyAuditSummary() {
        // Given
        let decision = AIDecision(
            recommendedAction: "approve",
            confidence: 0.85,
            reasonCodes: ["TEST"],
            keyFindings: ["Test"],
            missingInfo: [],
            nextSteps: ["Test"],
            policyNotes: [],
            auditSummary: ""
        )
        
        // When
        let (isValid, errors) = validateAIDecision(decision)
        
        // Then
        XCTAssertFalse(isValid)
        XCTAssertTrue(errors.contains { $0.contains("audit_summary cannot be empty") })
    }
    
    func testAllRecommendedActions() {
        // Given - Test all valid actions
        let validActions = ["approve", "reject", "need_more_info", "refer"]
        
        for action in validActions {
            // When
            let decision = AIDecision(
                recommendedAction: action,
                confidence: 0.85,
                reasonCodes: ["TEST"],
                keyFindings: ["Test"],
                missingInfo: [],
                nextSteps: ["Test"],
                policyNotes: [],
                auditSummary: "Test"
            )
            
            let (isValid, errors) = validateAIDecision(decision)
            
            // Then
            XCTAssertTrue(isValid, "Action '\(action)' should be valid")
            XCTAssertTrue(errors.isEmpty, "Action '\(action)' should have no errors")
        }
    }
    
    // MARK: - Inspection Template Schema Tests
    
    func testValidInspectionTemplate() {
        // Given
        let template = InspectionTemplate.motorInspection
        
        // When
        let (isValid, errors) = validateInspectionTemplate(template)
        
        // Then
        XCTAssertTrue(isValid)
        XCTAssertTrue(errors.isEmpty)
    }
    
    func testTemplateHasRequiredSections() {
        // Given
        let template = InspectionTemplate.motorInspection
        
        // When
        let sectionKeys = template.sections.map { $0.key }
        
        // Then
        XCTAssertTrue(sectionKeys.contains("vehicle_info"))
        XCTAssertTrue(sectionKeys.contains("damage_areas"))
        XCTAssertTrue(sectionKeys.contains("photos_checklist"))
        XCTAssertTrue(sectionKeys.contains("approval"))
    }
    
    func testTemplateFieldTypes() {
        // Given
        let template = InspectionTemplate.motorInspection
        
        // When - Get all field types
        let fieldTypes = template.sections.flatMap { section in
            section.fields.map { $0.type }
        }
        
        // Then - Should have various field types
        XCTAssertTrue(fieldTypes.contains(.text))
        XCTAssertTrue(fieldTypes.contains(.number))
        XCTAssertTrue(fieldTypes.contains(.dropdown))
        XCTAssertTrue(fieldTypes.contains(.toggle))
        XCTAssertTrue(fieldTypes.contains(.date))
        XCTAssertTrue(fieldTypes.contains(.signature))
        XCTAssertTrue(fieldTypes.contains(.photo))
    }
    
    func testTemplateRequiredFields() {
        // Given
        let template = InspectionTemplate.motorInspection
        
        // When - Get all required fields
        let requiredFields = template.sections.flatMap { section in
            section.fields.filter { $0.required }
        }
        
        // Then - Should have required fields
        XCTAssertFalse(requiredFields.isEmpty)
        XCTAssertTrue(requiredFields.count > 5)
    }
    
    func testTemplateSectionOrdering() {
        // Given
        let template = InspectionTemplate.motorInspection
        
        // When - Check section ordering
        let orders = template.sections.map { $0.order }
        
        // Then - Orders should be sequential
        XCTAssertEqual(orders, orders.sorted())
        XCTAssertEqual(orders.first, 1)
    }
    
    // MARK: - JSON Encoding/Decoding Tests
    
    func testAIDecisionJSONEncoding() throws {
        // Given
        let decision = AIDecision(
            recommendedAction: "approve",
            confidence: 0.85,
            reasonCodes: ["DAMAGE_CONSISTENT"],
            keyFindings: ["Test finding"],
            missingInfo: [],
            nextSteps: ["Test step"],
            policyNotes: ["Test note"],
            auditSummary: "Test summary"
        )
        
        // When
        let encoder = JSONEncoder()
        let data = try encoder.encode(decision)
        
        // Then
        XCTAssertFalse(data.isEmpty)
        
        // Decode back
        let decoder = JSONDecoder()
        let decoded = try decoder.decode(AIDecision.self, from: data)
        
        XCTAssertEqual(decoded.recommendedAction, decision.recommendedAction)
        XCTAssertEqual(decoded.confidence, decision.confidence)
        XCTAssertEqual(decoded.reasonCodes, decision.reasonCodes)
    }
    
    func testInspectionTemplateJSONEncoding() throws {
        // Given
        let template = InspectionTemplate.motorInspection
        
        // When
        let encoder = JSONEncoder()
        let data = try encoder.encode(template)
        
        // Then
        XCTAssertFalse(data.isEmpty)
        
        // Decode back
        let decoder = JSONDecoder()
        let decoded = try decoder.decode(InspectionTemplate.self, from: data)
        
        XCTAssertEqual(decoded.id, template.id)
        XCTAssertEqual(decoded.name, template.name)
        XCTAssertEqual(decoded.sections.count, template.sections.count)
    }
    
    // MARK: - Helper Methods
    
    private func validateAIDecision(_ decision: AIDecision) -> (valid: Bool, errors: [String]) {
        var errors: [String] = []
        
        // Validate recommended_action
        let validActions = ["approve", "reject", "need_more_info", "refer"]
        if !validActions.contains(decision.recommendedAction) {
            errors.append("Invalid recommended_action: \(decision.recommendedAction)")
        }
        
        // Validate confidence
        if decision.confidence < 0.0 || decision.confidence > 1.0 {
            errors.append("Confidence must be between 0.0 and 1.0")
        }
        
        // Validate required arrays
        if decision.reasonCodes.isEmpty {
            errors.append("reason_codes cannot be empty")
        }
        
        if decision.keyFindings.isEmpty {
            errors.append("key_findings cannot be empty")
        }
        
        if decision.nextSteps.isEmpty {
            errors.append("next_steps cannot be empty")
        }
        
        // Validate audit_summary
        if decision.auditSummary.isEmpty {
            errors.append("audit_summary cannot be empty")
        }
        
        return (errors.isEmpty, errors)
    }
    
    private func validateInspectionTemplate(_ template: InspectionTemplate) -> (valid: Bool, errors: [String]) {
        var errors: [String] = []
        
        // Validate template has sections
        if template.sections.isEmpty {
            errors.append("Template must have at least one section")
        }
        
        // Validate each section has fields
        for section in template.sections {
            if section.fields.isEmpty {
                errors.append("Section '\(section.key)' must have at least one field")
            }
        }
        
        return (errors.isEmpty, errors)
    }
}
