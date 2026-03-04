//
// AppLogger.swift
// DeevoSentinel
//
// Unified logging wrapper using os.Logger for production-grade observability
// Replaces all print() statements with structured logging
//

import Foundation
import os

/// Centralized logging for DeevoSentinel
/// Uses Apple's unified logging system (os.Logger) for:
/// - Structured log levels
/// - Privacy-aware logging
/// - Console.app integration
/// - Performance (lazy evaluation)
enum AppLogger {
    
    // MARK: - Subsystem
    
    private static let subsystem = Bundle.main.bundleIdentifier ?? "com.deevo.sentinel"
    
    // MARK: - Category Loggers
    
    /// Sync operations (push/pull, queue management)
    static let sync = Logger(subsystem: subsystem, category: "sync")
    
    /// API network requests and responses
    static let api = Logger(subsystem: subsystem, category: "api")
    
    /// PDF generation and export
    static let pdf = Logger(subsystem: subsystem, category: "pdf")
    
    /// Database operations
    static let database = Logger(subsystem: subsystem, category: "database")
    
    /// Authentication and security
    static let auth = Logger(subsystem: subsystem, category: "auth")
    
    /// UI and view lifecycle
    static let ui = Logger(subsystem: subsystem, category: "ui")
    
    /// Performance metrics
    static let performance = Logger(subsystem: subsystem, category: "performance")
    
    /// General application events
    static let app = Logger(subsystem: subsystem, category: "app")
    
    // MARK: - Convenience Methods
    
    /// Log a debug message (only visible in Console.app with debug level enabled)
    static func debug(_ message: String, category: Logger = app) {
        category.debug("\(message, privacy: .public)")
    }
    
    /// Log an info message
    static func info(_ message: String, category: Logger = app) {
        category.info("\(message, privacy: .public)")
    }
    
    /// Log a warning message
    static func warning(_ message: String, category: Logger = app) {
        category.warning("⚠️ \(message, privacy: .public)")
    }
    
    /// Log an error message
    static func error(_ message: String, category: Logger = app) {
        category.error("❌ \(message, privacy: .public)")
    }
    
    /// Log an error with associated Error object
    static func error(_ message: String, error: Error, category: Logger = app) {
        category.error("❌ \(message, privacy: .public): \(error.localizedDescription, privacy: .public)")
    }
    
    /// Log a critical/fault message (indicates a bug)
    static func critical(_ message: String, category: Logger = app) {
        category.critical("🚨 \(message, privacy: .public)")
    }
}

// MARK: - Sync-Specific Logging

extension AppLogger {
    
    /// Log sync operation start
    static func syncStarted(itemCount: Int) {
        sync.info("🔄 Sync started with \(itemCount) pending items")
    }
    
    /// Log sync operation success
    static func syncCompleted(processedCount: Int, duration: TimeInterval) {
        sync.info("✅ Sync completed: \(processedCount) items in \(String(format: "%.2f", duration))s")
    }
    
    /// Log sync operation failure
    static func syncFailed(error: Error, attempt: Int, nextRetryIn: TimeInterval?) {
        if let retry = nextRetryIn {
            sync.error("❌ Sync failed (attempt \(attempt)): \(error.localizedDescription). Retrying in \(String(format: "%.1f", retry))s")
        } else {
            sync.error("❌ Sync failed (attempt \(attempt)): \(error.localizedDescription). Max retries reached.")
        }
    }
    
    /// Log conflict detected
    static func conflictDetected(entityType: String, entityId: String, field: String) {
        sync.warning("⚡ Conflict detected: \(entityType)/\(entityId) field '\(field)'")
    }
    
    /// Log item processed
    static func itemProcessed(entityType: String, entityId: String, operation: String) {
        sync.debug("📥 Processed: \(operation) \(entityType)/\(entityId)")
    }
}

// MARK: - API-Specific Logging

extension AppLogger {
    
    /// Log API request
    static func apiRequest(method: String, endpoint: String) {
        api.debug("➡️ \(method) \(endpoint)")
    }
    
    /// Log API response
    static func apiResponse(endpoint: String, statusCode: Int, duration: TimeInterval) {
        if statusCode >= 200 && statusCode < 300 {
            api.debug("✅ \(endpoint) -> \(statusCode) (\(String(format: "%.0f", duration * 1000))ms)")
        } else {
            api.warning("⚠️ \(endpoint) -> \(statusCode) (\(String(format: "%.0f", duration * 1000))ms)")
        }
    }
    
    /// Log API error
    static func apiError(endpoint: String, error: Error) {
        api.error("❌ \(endpoint) failed: \(error.localizedDescription)")
    }
    
    /// Log session expiry
    static func sessionExpired() {
        auth.warning("🔐 Session expired - user needs to re-authenticate")
    }
}

// MARK: - Performance Logging

extension AppLogger {
    
    /// Log performance metric
    static func metric(name: String, value: Double, unit: String) {
        performance.info("📊 \(name): \(String(format: "%.2f", value)) \(unit)")
    }
    
    /// Log memory warning
    static func memoryWarning() {
        performance.warning("⚠️ Memory warning received")
    }
}

// MARK: - Signpost Support (for Instruments)

extension AppLogger {
    
    private static let signpostLog = OSLog(subsystem: subsystem, category: .pointsOfInterest)
    
    /// Begin a signpost interval (for Instruments profiling)
    static func signpostBegin(name: StaticString, id: OSSignpostID = .exclusive) {
        os_signpost(.begin, log: signpostLog, name: name, signpostID: id)
    }
    
    /// End a signpost interval
    static func signpostEnd(name: StaticString, id: OSSignpostID = .exclusive) {
        os_signpost(.end, log: signpostLog, name: name, signpostID: id)
    }
}
