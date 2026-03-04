import XCTest
import CryptoKit
@testable import DeevoSentinel

final class AuditChainTests: XCTestCase {
    
    // MARK: - Test Cases
    
    func testGenerateAuditHash() {
        // Given
        let hashPrev = "GENESIS"
        let createdAt = Date(timeIntervalSince1970: 1709164800) // 2024-02-28 12:00:00 UTC
        let eventType = "claim.created"
        let payloadJson = "{\"claimNumber\":\"CLM-001\"}"
        
        // When
        let hash = generateAuditHash(
            hashPrev: hashPrev,
            createdAt: createdAt,
            eventType: eventType,
            payloadJson: payloadJson
        )
        
        // Then
        XCTAssertEqual(hash.count, 64) // SHA256 produces 64 hex characters
        XCTAssertTrue(hash.allSatisfy { $0.isHexDigit })
    }
    
    func testHashConsistency() {
        // Given
        let hashPrev = "GENESIS"
        let createdAt = Date(timeIntervalSince1970: 1709164800)
        let eventType = "claim.created"
        let payloadJson = "{\"claimNumber\":\"CLM-001\"}"
        
        // When - Generate hash twice with same inputs
        let hash1 = generateAuditHash(
            hashPrev: hashPrev,
            createdAt: createdAt,
            eventType: eventType,
            payloadJson: payloadJson
        )
        
        let hash2 = generateAuditHash(
            hashPrev: hashPrev,
            createdAt: createdAt,
            eventType: eventType,
            payloadJson: payloadJson
        )
        
        // Then - Hashes should be identical
        XCTAssertEqual(hash1, hash2)
    }
    
    func testHashDifferentInputs() {
        // Given
        let createdAt = Date(timeIntervalSince1970: 1709164800)
        let eventType = "claim.created"
        let payloadJson = "{\"claimNumber\":\"CLM-001\"}"
        
        // When - Generate hashes with different hashPrev
        let hash1 = generateAuditHash(
            hashPrev: "GENESIS",
            createdAt: createdAt,
            eventType: eventType,
            payloadJson: payloadJson
        )
        
        let hash2 = generateAuditHash(
            hashPrev: "different-prev-hash",
            createdAt: createdAt,
            eventType: eventType,
            payloadJson: payloadJson
        )
        
        // Then - Hashes should be different
        XCTAssertNotEqual(hash1, hash2)
    }
    
    func testHashSensitiveToPayload() {
        // Given
        let hashPrev = "GENESIS"
        let createdAt = Date(timeIntervalSince1970: 1709164800)
        let eventType = "claim.created"
        
        // When - Generate hashes with different payloads
        let hash1 = generateAuditHash(
            hashPrev: hashPrev,
            createdAt: createdAt,
            eventType: eventType,
            payloadJson: "{\"claimNumber\":\"CLM-001\"}"
        )
        
        let hash2 = generateAuditHash(
            hashPrev: hashPrev,
            createdAt: createdAt,
            eventType: eventType,
            payloadJson: "{\"claimNumber\":\"CLM-002\"}"
        )
        
        // Then - Hashes should be different
        XCTAssertNotEqual(hash1, hash2)
    }
    
    func testAuditChainIntegrity() {
        // Given - Create a chain of 3 events
        let event1 = createAuditEvent(
            hashPrev: "GENESIS",
            eventType: "claim.created",
            payload: "{\"claimNumber\":\"CLM-001\"}"
        )
        
        let event2 = createAuditEvent(
            hashPrev: event1.hashThis,
            eventType: "claim.updated",
            payload: "{\"status\":\"assigned\"}"
        )
        
        let event3 = createAuditEvent(
            hashPrev: event2.hashThis,
            eventType: "inspection.started",
            payload: "{\"inspectionId\":\"INS-001\"}"
        )
        
        let events = [event1, event2, event3]
        
        // When - Verify chain
        let (isValid, errors) = verifyAuditChain(events)
        
        // Then - Chain should be valid
        XCTAssertTrue(isValid)
        XCTAssertTrue(errors.isEmpty)
    }
    
    func testDetectBrokenChain() {
        // Given - Create a chain with a broken link
        let event1 = createAuditEvent(
            hashPrev: "GENESIS",
            eventType: "claim.created",
            payload: "{\"claimNumber\":\"CLM-001\"}"
        )
        
        var event2 = createAuditEvent(
            hashPrev: event1.hashThis,
            eventType: "claim.updated",
            payload: "{\"status\":\"assigned\"}"
        )
        
        // Break the chain by changing hashPrev
        event2.hashPrev = "INVALID-HASH"
        
        let event3 = createAuditEvent(
            hashPrev: event2.hashThis,
            eventType: "inspection.started",
            payload: "{\"inspectionId\":\"INS-001\"}"
        )
        
        let events = [event1, event2, event3]
        
        // When - Verify chain
        let (isValid, errors) = verifyAuditChain(events)
        
        // Then - Chain should be invalid
        XCTAssertFalse(isValid)
        XCTAssertFalse(errors.isEmpty)
        XCTAssertTrue(errors.first?.contains("hashPrev mismatch") ?? false)
    }
    
    func testDetectTamperedData() {
        // Given - Create a chain and tamper with event data
        let event1 = createAuditEvent(
            hashPrev: "GENESIS",
            eventType: "claim.created",
            payload: "{\"claimNumber\":\"CLM-001\"}"
        )
        
        var event2 = createAuditEvent(
            hashPrev: event1.hashThis,
            eventType: "claim.updated",
            payload: "{\"status\":\"assigned\"}"
        )
        
        // Tamper with the payload but keep the hash
        event2.eventPayloadJson = "{\"status\":\"rejected\"}"
        
        let event3 = createAuditEvent(
            hashPrev: event2.hashThis,
            eventType: "inspection.started",
            payload: "{\"inspectionId\":\"INS-001\"}"
        )
        
        let events = [event1, event2, event3]
        
        // When - Verify chain
        let (isValid, errors) = verifyAuditChain(events)
        
        // Then - Chain should be invalid due to tampered data
        XCTAssertFalse(isValid)
        XCTAssertFalse(errors.isEmpty)
        XCTAssertTrue(errors.first?.contains("hashThis mismatch") ?? false)
    }
    
    // MARK: - Helper Methods
    
    private func generateAuditHash(
        hashPrev: String,
        createdAt: Date,
        eventType: String,
        payloadJson: String
    ) -> String {
        let formatter = ISO8601DateFormatter()
        let dateString = formatter.string(from: createdAt)
        let data = "\(hashPrev)|\(dateString)|\(eventType)|\(payloadJson)"
        
        let hash = SHA256.hash(data: Data(data.utf8))
        return hash.compactMap { String(format: "%02x", $0) }.joined()
    }
    
    private func createAuditEvent(
        hashPrev: String,
        eventType: String,
        payload: String
    ) -> AuditEvent {
        let createdAt = Date()
        let hashThis = generateAuditHash(
            hashPrev: hashPrev,
            createdAt: createdAt,
            eventType: eventType,
            payloadJson: payload
        )
        
        return AuditEvent(
            id: UUID().uuidString,
            actorId: "test-user",
            claimId: "test-claim",
            eventType: eventType,
            eventPayloadJson: payload,
            hashPrev: hashPrev,
            hashThis: hashThis,
            createdAt: createdAt
        )
    }
    
    private func verifyAuditChain(_ events: [AuditEvent]) -> (valid: Bool, errors: [String]) {
        var errors: [String] = []
        var prevHash = "GENESIS"
        
        for event in events {
            // Verify hashPrev matches
            if event.hashPrev != prevHash {
                errors.append("Event \(event.id): hashPrev mismatch. Expected \(prevHash), got \(event.hashPrev)")
            }
            
            // Verify hashThis is correct
            let expectedHash = generateAuditHash(
                hashPrev: event.hashPrev,
                createdAt: event.createdAt,
                eventType: event.eventType,
                payloadJson: event.eventPayloadJson
            )
            
            if event.hashThis != expectedHash {
                errors.append("Event \(event.id): hashThis mismatch (tampered data)")
            }
            
            prevHash = event.hashThis
        }
        
        return (errors.isEmpty, errors)
    }
}
