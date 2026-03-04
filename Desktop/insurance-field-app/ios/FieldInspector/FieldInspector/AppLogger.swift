//
//  AppLogger.swift
//  FieldInspector
//
//  Created for Production Readiness
//  Unified logging with Sentry integration
//

import Foundation
import os.log

// MARK: - Log Level

enum LogLevel: String {
    case debug = "DEBUG"
    case info = "INFO"
    case warning = "WARNING"
    case error = "ERROR"
    case critical = "CRITICAL"
    
    var osLogType: OSLogType {
        switch self {
        case .debug: return .debug
        case .info: return .info
        case .warning: return .default
        case .error: return .error
        case .critical: return .fault
        }
    }
}

// MARK: - App Logger

final class AppLogger {
    
    // MARK: - Singleton
    
    static let shared = AppLogger()
    
    // MARK: - Properties
    
    private let subsystem: String
    private var loggers: [String: Logger] = [:]
    private let queue = DispatchQueue(label: "com.fieldinsector.logger", qos: .utility)
    
    #if DEBUG
    private let isDebugMode = true
    #else
    private let isDebugMode = false
    #endif
    
    // MARK: - Initialization
    
    private init() {
        self.subsystem = Bundle.main.bundleIdentifier ?? "com.fieldinsector"
        setupSentry()
    }
    
    // MARK: - Sentry Setup
    
    private func setupSentry() {
        #if !DEBUG
        // Sentry initialization - uncomment when Sentry SDK is added
        /*
        import Sentry
        
        SentrySDK.start { options in
            options.dsn = Config.sentryDSN
            options.environment = Config.environment
            options.enableAutoSessionTracking = true
            options.sessionTrackingIntervalMillis = 30000
            options.attachStacktrace = true
            options.enableCaptureFailedRequests = true
            
            // Performance monitoring
            options.tracesSampleRate = 0.2
            
            // Set user info if available
            if let userId = UserDefaults.standard.string(forKey: "userId") {
                let user = User()
                user.userId = userId
                SentrySDK.setUser(user)
            }
        }
        */
        #endif
    }
    
    // MARK: - Logger Factory
    
    private func logger(for category: String) -> Logger {
        if let existing = loggers[category] {
            return existing
        }
        let newLogger = Logger(subsystem: subsystem, category: category)
        loggers[category] = newLogger
        return newLogger
    }
    
    // MARK: - Public Logging Methods
    
    /// Log a debug message (only in DEBUG builds)
    func debug(_ message: String, category: String = "General", file: String = #file, function: String = #function, line: Int = #line) {
        guard isDebugMode else { return }
        log(message, level: .debug, category: category, file: file, function: function, line: line)
    }
    
    /// Log an info message
    func info(_ message: String, category: String = "General", file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .info, category: category, file: file, function: function, line: line)
    }
    
    /// Log a warning message
    func warning(_ message: String, category: String = "General", file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .warning, category: category, file: file, function: function, line: line)
    }
    
    /// Log an error message
    func error(_ message: String, error: Error? = nil, category: String = "General", file: String = #file, function: String = #function, line: Int = #line) {
        var fullMessage = message
        if let error = error {
            fullMessage += " | Error: \(error.localizedDescription)"
        }
        log(fullMessage, level: .error, category: category, file: file, function: function, line: line)
        
        // Send to Sentry in production
        #if !DEBUG
        captureError(message: message, error: error, category: category)
        #endif
    }
    
    /// Log a critical error (app-breaking issues)
    func critical(_ message: String, error: Error? = nil, category: String = "General", file: String = #file, function: String = #function, line: Int = #line) {
        var fullMessage = message
        if let error = error {
            fullMessage += " | Error: \(error.localizedDescription)"
        }
        log(fullMessage, level: .critical, category: category, file: file, function: function, line: line)
        
        // Always send critical errors to Sentry
        #if !DEBUG
        captureError(message: message, error: error, category: category, isCritical: true)
        #endif
    }
    
    // MARK: - Private Methods
    
    private func log(_ message: String, level: LogLevel, category: String, file: String, function: String, line: Int) {
        let fileName = (file as NSString).lastPathComponent
        let formattedMessage = "[\(level.rawValue)] [\(fileName):\(line)] \(function) - \(message)"
        
        queue.async { [weak self] in
            guard let self = self else { return }
            let logger = self.logger(for: category)
            
            switch level {
            case .debug:
                logger.debug("\(formattedMessage)")
            case .info:
                logger.info("\(formattedMessage)")
            case .warning:
                logger.warning("\(formattedMessage)")
            case .error:
                logger.error("\(formattedMessage)")
            case .critical:
                logger.critical("\(formattedMessage)")
            }
        }
    }
    
    private func captureError(message: String, error: Error?, category: String, isCritical: Bool = false) {
        // Sentry error capture - uncomment when Sentry SDK is added
        /*
        import Sentry
        
        if let error = error {
            SentrySDK.capture(error: error) { scope in
                scope.setTag(value: category, key: "category")
                scope.setLevel(isCritical ? .fatal : .error)
                scope.setExtra(value: message, key: "message")
            }
        } else {
            SentrySDK.capture(message: message) { scope in
                scope.setTag(value: category, key: "category")
                scope.setLevel(isCritical ? .fatal : .error)
            }
        }
        */
    }
    
    // MARK: - User Identification
    
    func setUser(id: String, email: String? = nil, username: String? = nil) {
        // Sentry user identification - uncomment when Sentry SDK is added
        /*
        import Sentry
        
        let user = User()
        user.userId = id
        user.email = email
        user.username = username
        SentrySDK.setUser(user)
        */
        
        info("User identified: \(id)", category: "Auth")
    }
    
    func clearUser() {
        // Sentry clear user - uncomment when Sentry SDK is added
        /*
        import Sentry
        SentrySDK.setUser(nil)
        */
        
        info("User cleared", category: "Auth")
    }
    
    // MARK: - Breadcrumbs
    
    func addBreadcrumb(_ message: String, category: String = "General", data: [String: Any]? = nil) {
        // Sentry breadcrumb - uncomment when Sentry SDK is added
        /*
        import Sentry
        
        let crumb = Breadcrumb()
        crumb.message = message
        crumb.category = category
        crumb.level = .info
        if let data = data {
            crumb.data = data
        }
        SentrySDK.addBreadcrumb(crumb)
        */
        
        debug("Breadcrumb: \(message)", category: category)
    }
}

// MARK: - Convenience Global Functions

/// Global convenience function for debug logging
func logDebug(_ message: String, category: String = "General", file: String = #file, function: String = #function, line: Int = #line) {
    AppLogger.shared.debug(message, category: category, file: file, function: function, line: line)
}

/// Global convenience function for info logging
func logInfo(_ message: String, category: String = "General", file: String = #file, function: String = #function, line: Int = #line) {
    AppLogger.shared.info(message, category: category, file: file, function: function, line: line)
}

/// Global convenience function for warning logging
func logWarning(_ message: String, category: String = "General", file: String = #file, function: String = #function, line: Int = #line) {
    AppLogger.shared.warning(message, category: category, file: file, function: function, line: line)
}

/// Global convenience function for error logging
func logError(_ message: String, error: Error? = nil, category: String = "General", file: String = #file, function: String = #function, line: Int = #line) {
    AppLogger.shared.error(message, error: error, category: category, file: file, function: function, line: line)
}

/// Global convenience function for critical logging
func logCritical(_ message: String, error: Error? = nil, category: String = "General", file: String = #file, function: String = #function, line: Int = #line) {
    AppLogger.shared.critical(message, error: error, category: category, file: file, function: function, line: line)
}
