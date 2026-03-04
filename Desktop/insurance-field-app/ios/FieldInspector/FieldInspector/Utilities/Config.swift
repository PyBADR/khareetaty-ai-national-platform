//
// Config.swift
// DeevoSentinel
//
// Centralized configuration management reading from Info.plist
// Values are populated via xcconfig files at build time
//

import Foundation

/// Application configuration loaded from Info.plist
/// All values are populated via xcconfig files (Debug.xcconfig / Release.xcconfig)
enum Config {
    
    // MARK: - API Configuration
    
    /// Base URL for API requests
    /// Configured via API_BASE_URL in xcconfig
    static var apiBaseURL: URL {
        guard let urlString = Bundle.main.infoDictionary?["API_BASE_URL"] as? String,
              !urlString.isEmpty,
              let url = URL(string: urlString) else {
            // Fallback for development - should never happen in production
            #if DEBUG
            return URL(string: "http://127.0.0.1:3000/api")!
            #else
            fatalError("API_BASE_URL not configured in Info.plist. Check xcconfig files.")
            #endif
        }
        return url
    }
    
    /// API request timeout in seconds
    static var apiTimeoutSeconds: TimeInterval {
        guard let value = Bundle.main.infoDictionary?["API_TIMEOUT_SECONDS"] as? String,
              let timeout = TimeInterval(value) else {
            return 30 // Default timeout
        }
        return timeout
    }
    
    // MARK: - Feature Flags
    
    /// Whether debug logging is enabled
    static var isDebugLoggingEnabled: Bool {
        guard let value = Bundle.main.infoDictionary?["ENABLE_DEBUG_LOGGING"] as? String else {
            #if DEBUG
            return true
            #else
            return false
            #endif
        }
        return value.uppercased() == "YES" || value == "1" || value.uppercased() == "TRUE"
    }
    
    /// Whether mock data is enabled (for testing/demos)
    static var isMockDataEnabled: Bool {
        guard let value = Bundle.main.infoDictionary?["ENABLE_MOCK_DATA"] as? String else {
            return false
        }
        return value.uppercased() == "YES" || value == "1" || value.uppercased() == "TRUE"
    }
    
    // MARK: - App Info
    
    /// Application version string
    static var appVersion: String {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.0"
    }
    
    /// Application build number
    static var buildNumber: String {
        Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "1"
    }
    
    /// Full version string (e.g., "1.0.0 (42)")
    static var fullVersionString: String {
        "\(appVersion) (\(buildNumber))"
    }
    
    /// Bundle identifier
    static var bundleIdentifier: String {
        Bundle.main.bundleIdentifier ?? "com.deevo.sentinel"
    }
    
    // MARK: - Environment
    
    /// Current build environment
    static var environment: Environment {
        #if DEBUG
        return .debug
        #else
        if apiBaseURL.host?.contains("staging") == true {
            return .staging
        }
        return .production
        #endif
    }
    
    enum Environment: String {
        case debug = "Debug"
        case staging = "Staging"
        case production = "Production"
        
        var isProduction: Bool {
            self == .production
        }
    }
    
    // MARK: - Validation
    
    /// Validates that all required configuration is present
    /// Call this at app launch to fail fast if misconfigured
    static func validate() {
        #if !DEBUG
        // In release builds, ensure API URL is configured
        guard Bundle.main.infoDictionary?["API_BASE_URL"] as? String != nil else {
            fatalError("Missing required configuration: API_BASE_URL")
        }
        #endif
    }
}

// MARK: - Debug Description

extension Config {
    /// Prints current configuration (only in debug builds)
    static func printConfiguration() {
        #if DEBUG
        print(
        """
        ╔══════════════════════════════════════════╗
        ║       DeevoSentinel Configuration        ║
        ╠══════════════════════════════════════════╣
        ║ Environment: \(environment.rawValue.padding(toLength: 25, withPad: " ", startingAt: 0)) ║
        ║ API URL: \(apiBaseURL.absoluteString.prefix(28).padding(toLength: 28, withPad: " ", startingAt: 0)) ║
        ║ Version: \(fullVersionString.padding(toLength: 28, withPad: " ", startingAt: 0)) ║
        ║ Debug Logging: \(isDebugLoggingEnabled ? "Enabled" : "Disabled".padding(toLength: 22, withPad: " ", startingAt: 0)) ║
        ╚══════════════════════════════════════════╝
        """)
        #endif
    }
}
