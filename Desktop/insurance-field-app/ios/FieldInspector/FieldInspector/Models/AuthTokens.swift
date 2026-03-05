//
//  AuthTokens.swift
//  FieldInspector
//
//  Authentication tokens model
//

import Foundation

struct AuthTokens: Codable {
    let accessToken: String
    let refreshToken: String
    let expiresAt: Date
    
    var isExpired: Bool {
        Date() >= expiresAt
    }
    
    var isExpiringSoon: Bool {
        // Consider expired if within 5 minutes of expiry
        Date().addingTimeInterval(300) >= expiresAt
    }
}
