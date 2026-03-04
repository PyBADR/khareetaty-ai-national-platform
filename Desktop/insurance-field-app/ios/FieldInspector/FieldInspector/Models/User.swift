import Foundation
import GRDB

// MARK: - User Role

enum UserRole: String, Codable, DatabaseValueConvertible {
    case admin = "admin"
    case inspector = "inspector"
    case reviewer = "reviewer"
    
    var displayName: String {
        switch self {
        case .admin: return "Administrator"
        case .inspector: return "Inspector"
        case .reviewer: return "Reviewer"
        }
    }
}

// MARK: - User Model

struct User: Identifiable, Codable, Equatable {
    var id: String
    var email: String
    var firstName: String
    var lastName: String
    var role: UserRole
    var isActive: Bool
    var tenantId: String
    var createdAt: Date
    
    var fullName: String {
        "\(firstName) \(lastName)"
    }
    
    var initials: String {
        let first = firstName.first.map { String($0) } ?? ""
        let last = lastName.first.map { String($0) } ?? ""
        return "\(first)\(last)".uppercased()
    }
}

// MARK: - Tenant Model

struct Tenant: Identifiable, Codable, Equatable {
    var id: String
    var name: String
    var slug: String
    var isActive: Bool
}

extension User: FetchableRecord, PersistableRecord {
    static let databaseTableName = "users"
}

// MARK: - Auth Token

struct AuthToken: Codable {
    let token: String
    let expiresAt: Date?
    
    var isExpired: Bool {
        guard let expiresAt = expiresAt else { return false }
        return Date() > expiresAt
    }
}

// MARK: - Login Response

struct LoginResponse: Codable {
    let token: String
    let user: User
    let tenant: Tenant?
}
