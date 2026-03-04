import Foundation
import GRDB
import Combine
import CryptoKit

/// ViewModel for managing audit events and chain verification
@MainActor
class AuditViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var auditEvents: [AuditEvent] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var chainValid = true
    @Published var verificationInProgress = false
    @Published var selectedEvent: AuditEvent?
    
    // MARK: - Computed Properties
    
    var eventsByType: [String: [AuditEvent]] {
        Dictionary(grouping: auditEvents) { $0.eventType }
    }
    
    var recentEvents: [AuditEvent] {
        Array(auditEvents.prefix(20))
    }
    
    // MARK: - Properties
    
    private let database: DatabaseManager
    private let api: APIService
    private var claimId: String?
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(
        database: DatabaseManager = .shared,
        api: APIService = .shared
    ) {
        self.database = database
        self.api = api
    }
    
    // MARK: - Public Methods
    
    /// Load audit events
    func loadEvents(claimId: String? = nil) async {
        self.claimId = claimId
        isLoading = true
        errorMessage = nil
        
        do {
            auditEvents = try await database.database.read { db in
                var query = AuditEvent.order(Column("createdAt").desc)
                
                if let claimId = claimId {
                    query = query.filter(Column("claimId") == claimId)
                }
                
                return try query.limit(100).fetchAll(db)
            }
            
            isLoading = false
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
        }
    }
    
    /// Create a new audit event
    func createEvent(
        actorId: String,
        claimId: String?,
        eventType: String,
        eventPayload: [String: Any]
    ) async throws {
        // Get the most recent event to chain from
        let lastEvent = try await database.database.read { db in
            try AuditEvent
                .order(Column("createdAt").desc)
                .fetchOne(db)
        }
        
        let hashPrev = lastEvent?.hashThis ?? "GENESIS"
        let createdAt = Date()
        
        // Convert payload to JSON string
        let payloadData = try JSONSerialization.data(withJSONObject: eventPayload)
        let payloadJson = String(data: payloadData, encoding: .utf8) ?? "{}"
        
        // Generate hash
        let hashThis = generateAuditHash(
            hashPrev: hashPrev,
            createdAt: createdAt,
            eventType: eventType,
            payloadJson: payloadJson
        )
        
        // Create event
        let event = AuditEvent(
            id: UUID().uuidString,
            actorId: actorId,
            claimId: claimId,
            eventType: eventType,
            eventPayloadJson: payloadJson,
            hashPrev: hashPrev,
            hashThis: hashThis,
            createdAt: createdAt
        )
        
        // Save to database
        try await database.database.write { db in
            try event.insert(db)
        }
        
        // Reload events
        await loadEvents(claimId: self.claimId)
    }
    
    /// Verify the integrity of the audit chain
    func verifyChain() async {
        verificationInProgress = true
        chainValid = true
        
        do {
            let events = try await database.database.read { db in
                try AuditEvent
                    .order(Column("createdAt").asc)
                    .limit(1000)
                    .fetchAll(db)
            }
            
            var prevHash = "GENESIS"
            
            for event in events {
                // Verify hashPrev matches
                if event.hashPrev != prevHash {
                    chainValid = false
                    errorMessage = "Chain broken at event \(event.id): hashPrev mismatch"
                    break
                }
                
                // Verify hashThis is correct
                let expectedHash = generateAuditHash(
                    hashPrev: event.hashPrev,
                    createdAt: event.createdAt,
                    eventType: event.eventType,
                    payloadJson: event.eventPayloadJson
                )
                
                if event.hashThis != expectedHash {
                    chainValid = false
                    errorMessage = "Chain broken at event \(event.id): hashThis mismatch (tampered data)"
                    break
                }
                
                prevHash = event.hashThis
            }
            
            if chainValid {
                errorMessage = nil
            }
            
            verificationInProgress = false
        } catch {
            errorMessage = "Verification failed: \(error.localizedDescription)"
            chainValid = false
            verificationInProgress = false
        }
    }
    
    /// Filter events by type
    func filterByType(_ type: String) async {
        isLoading = true
        let currentClaimId = self.claimId
        
        do {
            auditEvents = try await database.database.read { db in
                var query = AuditEvent
                    .filter(Column("eventType") == type)
                    .order(Column("createdAt").desc)
                
                if let claimId = currentClaimId {
                    query = query.filter(Column("claimId") == claimId)
                }
                
                return try query.limit(100).fetchAll(db)
            }
            
            isLoading = false
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
        }
    }
    
    /// Clear filters and reload all events
    func clearFilters() async {
        await loadEvents(claimId: claimId)
    }
    
    /// Export audit log as JSON
    func exportAuditLog() async throws -> Data {
        let currentClaimId = self.claimId
        let events = try await database.database.read { db in
            var query = AuditEvent.order(Column("createdAt").asc)
            
            if let claimId = currentClaimId {
                query = query.filter(Column("claimId") == claimId)
            }
            
            return try query.fetchAll(db)
        }
        
        let exportData: [[String: Any]] = events.map { event in
            [
                "id": event.id,
                "actorId": event.actorId,
                "claimId": event.claimId ?? NSNull(),
                "eventType": event.eventType,
                "eventPayload": event.eventPayloadJson,
                "hashPrev": event.hashPrev,
                "hashThis": event.hashThis,
                "createdAt": ISO8601DateFormatter().string(from: event.createdAt)
            ]
        }
        
        return try JSONSerialization.data(withJSONObject: exportData, options: .prettyPrinted)
    }
    
    // MARK: - Private Methods
    
    /// Generate SHA256 hash for audit chain
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
}

// AuditEventType is defined in Models/AuditEvent.swift
