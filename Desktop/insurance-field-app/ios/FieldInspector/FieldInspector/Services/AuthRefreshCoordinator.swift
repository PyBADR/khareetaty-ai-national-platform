//
//  AuthRefreshCoordinator.swift
//  FieldInspector
//
//  Single-flight token refresh coordinator (prevents race conditions)
//

import Foundation

actor AuthRefreshCoordinator {
    
    private let keychainStore: KeychainStore
    private let apiBaseURL: String
    private var refreshTask: Task<AuthTokens, Error>?
    
    private let tokensKey = "auth_tokens"
    
    init(keychainStore: KeychainStore, apiBaseURL: String) {
        self.keychainStore = keychainStore
        self.apiBaseURL = apiBaseURL
    }
    
    // MARK: - Public API
    
    func validAccessToken() async throws -> String {
        let tokens = try getTokens()
        
        // If token is expired or expiring soon, refresh it
        if tokens.isExpiringSoon {
            let newTokens = try await refreshIfNeeded()
            return newTokens.accessToken
        }
        
        return tokens.accessToken
    }
    
    func setTokens(_ tokens: AuthTokens) async throws {
        try keychainStore.store(tokens, forKey: tokensKey)
    }
    
    func clearTokens() async throws {
        try keychainStore.delete(forKey: tokensKey)
        refreshTask?.cancel()
        refreshTask = nil
    }
    
    // MARK: - Single-Flight Refresh
    
    func refreshIfNeeded() async throws -> AuthTokens {
        // If refresh is already in progress, wait for it
        if let existingTask = refreshTask {
            return try await existingTask.value
        }
        
        // Start new refresh task
        let task = Task<AuthTokens, Error> {
            try await performRefresh()
        }
        
        refreshTask = task
        
        do {
            let newTokens = try await task.value
            refreshTask = nil
            return newTokens
        } catch {
            refreshTask = nil
            throw error
        }
    }
    
    // MARK: - Private Helpers
    
    private func getTokens() throws -> AuthTokens {
        try keychainStore.read(forKey: tokensKey, as: AuthTokens.self)
    }
    
    private func performRefresh() async throws -> AuthTokens {
        let currentTokens = try getTokens()
        
        guard let url = URL(string: "\(apiBaseURL)/auth/refresh") else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 30
        
        let body = ["refreshToken": currentTokens.refreshToken]
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        
        guard httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        let refreshResponse = try JSONDecoder().decode(RefreshResponse.self, from: data)
        
        let newTokens = AuthTokens(
            accessToken: refreshResponse.accessToken,
            refreshToken: refreshResponse.refreshToken ?? currentTokens.refreshToken,
            expiresAt: Date().addingTimeInterval(TimeInterval(refreshResponse.expiresIn))
        )
        
        // Store new tokens
        try await setTokens(newTokens)
        
        return newTokens
    }
}

// MARK: - Response Models

private struct RefreshResponse: Decodable {
    let accessToken: String
    let refreshToken: String?
    let expiresIn: Int
}
