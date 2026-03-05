//
//  AsyncTimeout.swift
//  FieldInspector
//
//  Timeout wrapper for async operations
//

import Foundation

enum TimeoutError: Error {
    case timedOut
}

func withTimeout<T: Sendable>(
    _ seconds: TimeInterval,
    operation: @escaping @Sendable () async throws -> T
) async throws -> T {
    try await withThrowingTaskGroup(of: T.self) { group in
        // Add the actual operation
        group.addTask {
            try await operation()
        }
        
        // Add timeout task
        group.addTask {
            try await Task.sleep(nanoseconds: UInt64(seconds * 1_000_000_000))
            throw TimeoutError.timedOut
        }
        
        // Wait for first to complete
        guard let result = try await group.next() else {
            throw TimeoutError.timedOut
        }
        
        // Cancel remaining tasks
        group.cancelAll()
        
        return result
    }
}
