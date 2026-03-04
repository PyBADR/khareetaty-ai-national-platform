import Foundation
import GRDB
import CryptoKit

// MARK: - Audit Event Types

enum AuditEventType: String, Codable {
    // Auth
    case userLogin = "user.login"
    case userLogout = "user.logout"
    
    // Claims
    case claimCreated = "claim.created"
    case claimUpdated = "claim.updated"
    case claimAssigned = "claim.assigned"
    case claimAccepted = "claim.accepted"
    case claimStatusChanged = "claim.status_changed"
    
    // Inspections
    case inspectionStarted = "inspection.started"
    case inspectionFieldUpdated = "inspection.field_updated"
    case inspectionCompleted = "inspection.completed"
    
    // Media
    case mediaUploaded = "media.uploaded"
    case mediaTagged = "media.tagged"
    case mediaDeleted = "media.deleted"
    
    // AI
    case aiSuggestionRequested = "ai.suggestion_requested"
    case aiSuggestionReceived = "ai.suggestion_received"
    
    // Sync
    case syncStarted = "sync.started"
    case syncCompleted = "sync.completed"
    case syncFailed = "sync.failed"
    
    // Reports
    case reportGenerated = "report.generated"
    case reportExported = "report.exported"
}

// MARK: - Audit Event Model

struct AuditEvent: Identifiable, Codable, Equatable {
    var id: String
    var actorId: String
    var claimId: String?
    var eventType: String
    var eventPayloadJson: String
    var hashPrev: String
    var hashThis: String
    var createdAt: Date
    
    /// Memberwise initializer for direct property assignment
    init(
        id: String,
        actorId: String,
        claimId: String?,
        eventType: String,
        eventPayloadJson: String,
        hashPrev: String,
        hashThis: String,
        createdAt: Date
    ) {
        self.id = id
        self.actorId = actorId
        self.claimId = claimId
        self.eventType = eventType
        self.eventPayloadJson = eventPayloadJson
        self.hashPrev = hashPrev
        self.hashThis = hashThis
        self.createdAt = createdAt
    }
    
    /// Convenience initializer with AuditEventType enum
    init(
        id: String = UUID().uuidString,
        actorId: String,
        claimId: String? = nil,
        eventType: AuditEventType,
        eventPayload: [String: Any],
        hashPrev: String
    ) {
        self.id = id
        self.actorId = actorId
        self.claimId = claimId
        self.eventType = eventType.rawValue
        self.createdAt = Date()
        
        // Serialize payload
        if let jsonData = try? JSONSerialization.data(withJSONObject: eventPayload),
           let jsonString = String(data: jsonData, encoding: .utf8) {
            self.eventPayloadJson = jsonString
        } else {
            self.eventPayloadJson = "{}"
        }
        
        self.hashPrev = hashPrev
        self.hashThis = AuditEvent.generateHash(
            hashPrev: hashPrev,
            createdAt: self.createdAt,
            eventType: self.eventType,
            payloadJson: self.eventPayloadJson
        )
    }
    
    /// Generate SHA256 hash for audit chain
    static func generateHash(
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
    
    /// Verify the hash is correct
    func verifyHash() -> Bool {
        let expectedHash = AuditEvent.generateHash(
            hashPrev: hashPrev,
            createdAt: createdAt,
            eventType: eventType,
            payloadJson: eventPayloadJson
        )
        return hashThis == expectedHash
    }
}

extension AuditEvent: FetchableRecord, PersistableRecord {
    static let databaseTableName = "audit_events"
}

// MARK: - Computed Properties for PDFService Compatibility

extension AuditEvent {
    /// Alias for createdAt (used by PDFService)
    var timestamp: Date {
        return createdAt
    }
    
    /// Alias for hashThis (used by PDFService)
    var eventHash: String {
        return hashThis
    }
    
    /// Description derived from event payload (used by PDFService)
    var description: String? {
        guard let data = eventPayloadJson.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let desc = json["description"] as? String else {
            return nil
        }
        return desc
    }
}
