import Foundation
import Security
import CryptoKit
import os.log

// MARK: - Security Manager
/// Handles encryption, PII masking, and privacy features for Deevo Sentinel

final class SecurityManager {
    static let shared = SecurityManager()
    
    private let logger = Logger(subsystem: "com.deevo.sentinel", category: "Security")
    private let keychainService = "com.deevo.sentinel.keychain"
    
    // MARK: - Privacy Mode
    
    @Published private(set) var isPrivacyModeEnabled: Bool = false
    
    private init() {
        loadPrivacyModeState()
    }
    
    // MARK: - Database Encryption Key Management
    
    /// Retrieves or generates the database encryption key
    func getDatabaseEncryptionKey() throws -> Data {
        let keyTag = "com.deevo.sentinel.db.key"
        
        // Try to retrieve existing key
        if let existingKey = try? retrieveKeyFromKeychain(tag: keyTag) {
            return existingKey
        }
        
        // Generate new key
        let newKey = SymmetricKey(size: .bits256)
        let keyData = newKey.withUnsafeBytes { Data($0) }
        
        // Store in keychain
        try storeKeyInKeychain(key: keyData, tag: keyTag)
        
        logger.info("Generated new database encryption key")
        return keyData
    }
    
    /// Stores a key in the keychain
    private func storeKeyInKeychain(key: Data, tag: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrApplicationTag as String: tag.data(using: .utf8)!,
            kSecValueData as String: key,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        ]
        
        // Delete any existing key first
        SecItemDelete(query as CFDictionary)
        
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw SecurityError.keychainError(status)
        }
    }
    
    /// Retrieves a key from the keychain
    private func retrieveKeyFromKeychain(tag: String) throws -> Data {
        let query: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrApplicationTag as String: tag.data(using: .utf8)!,
            kSecReturnData as String: true
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        guard status == errSecSuccess, let keyData = result as? Data else {
            throw SecurityError.keychainError(status)
        }
        
        return keyData
    }
    
    // MARK: - Data Encryption
    
    /// Encrypts data using AES-GCM
    func encrypt(_ data: Data) throws -> Data {
        let key = try getDatabaseEncryptionKey()
        let symmetricKey = SymmetricKey(data: key)
        
        let sealedBox = try AES.GCM.seal(data, using: symmetricKey)
        guard let combined = sealedBox.combined else {
            throw SecurityError.encryptionFailed
        }
        
        return combined
    }
    
    /// Decrypts data using AES-GCM
    func decrypt(_ data: Data) throws -> Data {
        let key = try getDatabaseEncryptionKey()
        let symmetricKey = SymmetricKey(data: key)
        
        let sealedBox = try AES.GCM.SealedBox(combined: data)
        let decryptedData = try AES.GCM.open(sealedBox, using: symmetricKey)
        
        return decryptedData
    }
    
    // MARK: - Privacy Mode
    
    func enablePrivacyMode() {
        isPrivacyModeEnabled = true
        UserDefaults.standard.set(true, forKey: "privacyModeEnabled")
        logger.info("Privacy mode enabled")
    }
    
    func disablePrivacyMode() {
        isPrivacyModeEnabled = false
        UserDefaults.standard.set(false, forKey: "privacyModeEnabled")
        logger.info("Privacy mode disabled")
    }
    
    func togglePrivacyMode() {
        if isPrivacyModeEnabled {
            disablePrivacyMode()
        } else {
            enablePrivacyMode()
        }
    }
    
    private func loadPrivacyModeState() {
        isPrivacyModeEnabled = UserDefaults.standard.bool(forKey: "privacyModeEnabled")
    }
}

// MARK: - PII Masking

extension SecurityManager {
    
    /// Masks an email address for display
    func maskEmail(_ email: String?) -> String {
        guard let email = email, !email.isEmpty else { return "***@***.***" }
        
        if isPrivacyModeEnabled {
            return "***@***.***"
        }
        
        let components = email.split(separator: "@")
        guard components.count == 2 else { return "***@***.***" }
        
        let localPart = String(components[0])
        let domain = String(components[1])
        
        let maskedLocal = localPart.prefix(2) + "***"
        let domainParts = domain.split(separator: ".")
        let maskedDomain = domainParts.first.map { String($0.prefix(2)) + "***" } ?? "***"
        let tld = domainParts.last.map { String($0) } ?? "***"
        
        return "\(maskedLocal)@\(maskedDomain).\(tld)"
    }
    
    /// Masks a phone number for display
    func maskPhone(_ phone: String?) -> String {
        guard let phone = phone, !phone.isEmpty else { return "***-***-****" }
        
        if isPrivacyModeEnabled {
            return "***-***-****"
        }
        
        let digits = phone.filter { $0.isNumber }
        guard digits.count >= 4 else { return "***-***-****" }
        
        let lastFour = String(digits.suffix(4))
        return "***-***-\(lastFour)"
    }
    
    /// Masks a name for display
    func maskName(_ name: String?) -> String {
        guard let name = name, !name.isEmpty else { return "*****" }
        
        if isPrivacyModeEnabled {
            return "*****"
        }
        
        let parts = name.split(separator: " ")
        if parts.count >= 2 {
            let firstName = String(parts[0].prefix(1)) + "***"
            let lastName = String(parts[1].prefix(1)) + "***"
            return "\(firstName) \(lastName)"
        }
        
        return String(name.prefix(1)) + "***"
    }
    
    /// Masks an address for display
    func maskAddress(_ address: String?) -> String {
        guard let address = address, !address.isEmpty else { return "*** *** ***" }
        
        if isPrivacyModeEnabled {
            return "*** *** ***"
        }
        
        // Show only first few characters
        return String(address.prefix(5)) + "***"
    }
    
    /// Masks a claim number for logs (keeps format visible)
    func maskClaimNumber(_ claimNumber: String?) -> String {
        guard let claimNumber = claimNumber else { return "CLM-****-***" }
        
        if isPrivacyModeEnabled {
            return "CLM-****-***"
        }
        
        // Keep prefix, mask the rest
        if claimNumber.hasPrefix("CLM-") {
            return "CLM-****-" + String(claimNumber.suffix(3))
        }
        
        return String(claimNumber.prefix(4)) + "****"
    }
    
    /// Masks a policy number
    func maskPolicyNumber(_ policyNumber: String?) -> String {
        guard let policyNumber = policyNumber else { return "POL-******" }
        
        if isPrivacyModeEnabled {
            return "POL-******"
        }
        
        return String(policyNumber.prefix(4)) + "******"
    }
}

// MARK: - Secure Logging

extension SecurityManager {
    
    /// Logs a message with PII automatically masked
    func secureLog(_ message: String, level: OSLogType = .info, piiFields: [String: String?] = [:]) {
        var maskedMessage = message
        
        for (fieldName, value) in piiFields {
            let maskedValue: String
            switch fieldName.lowercased() {
            case "email":
                maskedValue = maskEmail(value)
            case "phone":
                maskedValue = maskPhone(value)
            case "name":
                maskedValue = maskName(value)
            case "address":
                maskedValue = maskAddress(value)
            case "claimnumber":
                maskedValue = maskClaimNumber(value)
            case "policynumber":
                maskedValue = maskPolicyNumber(value)
            default:
                maskedValue = value.map { String($0.prefix(3)) + "***" } ?? "***"
            }
            maskedMessage = maskedMessage.replacingOccurrences(of: "{\(fieldName)}", with: maskedValue)
        }
        
        logger.log(level: level, "\(maskedMessage, privacy: .public)")
    }
    
    /// Logs an error securely
    func secureLogError(_ error: Error, context: String) {
        logger.error("Error in \(context, privacy: .public): \(error.localizedDescription, privacy: .public)")
    }
}

// MARK: - Hash Utilities

extension SecurityManager {
    
    /// Generates SHA256 hash of data
    func sha256(_ data: Data) -> String {
        let hash = SHA256.hash(data: data)
        return hash.compactMap { String(format: "%02x", $0) }.joined()
    }
    
    /// Generates SHA256 hash of string
    func sha256(_ string: String) -> String {
        guard let data = string.data(using: .utf8) else { return "" }
        return sha256(data)
    }
    
    /// Generates HMAC for data integrity verification
    func hmac(_ data: Data, key: Data) -> Data {
        let symmetricKey = SymmetricKey(data: key)
        let authCode = HMAC<SHA256>.authenticationCode(for: data, using: symmetricKey)
        return Data(authCode)
    }
}

// MARK: - Security Error

enum SecurityError: LocalizedError {
    case keychainError(OSStatus)
    case encryptionFailed
    case decryptionFailed
    case invalidKey
    
    var errorDescription: String? {
        switch self {
        case .keychainError(let status):
            return "Keychain error: \(status)"
        case .encryptionFailed:
            return "Failed to encrypt data"
        case .decryptionFailed:
            return "Failed to decrypt data"
        case .invalidKey:
            return "Invalid encryption key"
        }
    }
}

// MARK: - String Extension for Hashing

extension String {
    func sha256() -> String {
        SecurityManager.shared.sha256(self)
    }
}
