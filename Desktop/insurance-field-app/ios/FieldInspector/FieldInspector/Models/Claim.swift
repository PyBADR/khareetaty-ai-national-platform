import Foundation
import GRDB
import SwiftUI

// MARK: - Claim Status

enum ClaimStatus: String, Codable, CaseIterable, DatabaseValueConvertible {
    case new = "new"
    case assigned = "assigned"
    case inProgress = "in_progress"
    case pendingReview = "pending_review"
    case approved = "approved"
    case rejected = "rejected"
    case closed = "closed"
    
    var displayName: String {
        switch self {
        case .new: return "New"
        case .assigned: return "Assigned"
        case .inProgress: return "In Progress"
        case .pendingReview: return "Pending Review"
        case .approved: return "Approved"
        case .rejected: return "Rejected"
        case .closed: return "Closed"
        }
    }
    
    var color: Color {
        switch self {
        case .new: return DeevoColors.info
        case .assigned: return Color.orange
        case .inProgress: return DeevoColors.warning
        case .pendingReview: return DeevoColors.secondary
        case .approved: return DeevoColors.success
        case .rejected: return DeevoColors.error
        case .closed: return DeevoColors.textTertiary
        }
    }
}

// MARK: - Claim Priority

enum ClaimPriority: String, Codable, CaseIterable, DatabaseValueConvertible {
    case low = "low"
    case medium = "medium"
    case high = "high"
    case urgent = "urgent"
    
    var displayName: String {
        switch self {
        case .low: return "Low"
        case .medium: return "Medium"
        case .high: return "High"
        case .urgent: return "Urgent"
        }
    }
    
    var sortOrder: Int {
        switch self {
        case .urgent: return 0
        case .high: return 1
        case .medium: return 2
        case .low: return 3
        }
    }
}

// MARK: - Claim Model

struct Claim: Identifiable, Codable, Equatable, Hashable {
    var id: String
    var claimNumber: String
    var policyNumber: String?
    var status: ClaimStatus
    var priority: ClaimPriority
    var customerName: String
    var customerPhone: String?
    var customerEmail: String?
    
    // Vehicle Info
    var vehicleMake: String?
    var vehicleModel: String?
    var vehicleYear: Int?
    var vehicleVin: String?
    var vehiclePlate: String?
    var vehicleColor: String?
    
    // Location
    var locationAddress: String?
    var locationCity: String?
    var locationState: String?
    var locationZip: String?
    var locationLat: Double?
    var locationLng: Double?
    
    // Incident
    var incidentDate: Date?
    var incidentDescription: String?
    var estimatedDamage: Double?
    
    // AI & Risk
    var aiDecision: String?
    var aiConfidence: Double?
    var riskScore: Int?
    var claimAmount: Double
    
    // Assignment
    var assignedToId: String?
    var assignedAt: Date?
    
    // Multi-tenancy
    var tenantId: String
    
    // Timestamps
    var createdAt: Date
    var updatedAt: Date
    
    // Sync
    var syncStatus: SyncStatus
    var lastSyncedAt: Date?
    
    init(
        id: String = UUID().uuidString,
        claimNumber: String,
        policyNumber: String? = nil,
        status: ClaimStatus = .new,
        priority: ClaimPriority = .medium,
        customerName: String,
        customerPhone: String? = nil,
        customerEmail: String? = nil,
        vehicleMake: String? = nil,
        vehicleModel: String? = nil,
        vehicleYear: Int? = nil,
        vehicleVin: String? = nil,
        vehiclePlate: String? = nil,
        vehicleColor: String? = nil,
        locationAddress: String? = nil,
        locationCity: String? = nil,
        locationState: String? = nil,
        locationZip: String? = nil,
        locationLat: Double? = nil,
        locationLng: Double? = nil,
        incidentDate: Date? = nil,
        incidentDescription: String? = nil,
        estimatedDamage: Double? = nil,
        aiDecision: String? = nil,
        aiConfidence: Double? = nil,
        riskScore: Int? = nil,
        claimAmount: Double = 0,
        assignedToId: String? = nil,
        assignedAt: Date? = nil,
        tenantId: String = "default",
        createdAt: Date = Date(),
        updatedAt: Date = Date(),
        syncStatus: SyncStatus = .pending,
        lastSyncedAt: Date? = nil
    ) {
        self.id = id
        self.claimNumber = claimNumber
        self.policyNumber = policyNumber
        self.status = status
        self.priority = priority
        self.customerName = customerName
        self.customerPhone = customerPhone
        self.customerEmail = customerEmail
        self.vehicleMake = vehicleMake
        self.vehicleModel = vehicleModel
        self.vehicleYear = vehicleYear
        self.vehicleVin = vehicleVin
        self.vehiclePlate = vehiclePlate
        self.vehicleColor = vehicleColor
        self.locationAddress = locationAddress
        self.locationCity = locationCity
        self.locationState = locationState
        self.locationZip = locationZip
        self.locationLat = locationLat
        self.locationLng = locationLng
        self.incidentDate = incidentDate
        self.incidentDescription = incidentDescription
        self.estimatedDamage = estimatedDamage
        self.aiDecision = aiDecision
        self.aiConfidence = aiConfidence
        self.riskScore = riskScore
        self.claimAmount = claimAmount
        self.assignedToId = assignedToId
        self.assignedAt = assignedAt
        self.tenantId = tenantId
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.syncStatus = syncStatus
        self.lastSyncedAt = lastSyncedAt
    }
    
    var vehicleDescription: String {
        var parts: [String] = []
        if let year = vehicleYear { parts.append(String(year)) }
        if let make = vehicleMake { parts.append(make) }
        if let model = vehicleModel { parts.append(model) }
        return parts.isEmpty ? "Unknown Vehicle" : parts.joined(separator: " ")
    }
    
    var fullAddress: String {
        var parts: [String] = []
        if let address = locationAddress { parts.append(address) }
        if let city = locationCity { parts.append(city) }
        if let state = locationState { parts.append(state) }
        if let zip = locationZip { parts.append(zip) }
        return parts.isEmpty ? "No address" : parts.joined(separator: ", ")
    }
    
    /// Alias for incidentDescription (used by PDFService)
    var claimDescription: String? {
        return incidentDescription
    }
}

// MARK: - GRDB Record

extension Claim: FetchableRecord, PersistableRecord {
    static let databaseTableName = "claims"
    
    enum Columns {
        static let id = Column(CodingKeys.id)
        static let claimNumber = Column(CodingKeys.claimNumber)
        static let status = Column(CodingKeys.status)
        static let priority = Column(CodingKeys.priority)
        static let customerName = Column(CodingKeys.customerName)
        static let tenantId = Column(CodingKeys.tenantId)
        static let createdAt = Column(CodingKeys.createdAt)
        static let updatedAt = Column(CodingKeys.updatedAt)
        static let syncStatus = Column(CodingKeys.syncStatus)
    }
}
