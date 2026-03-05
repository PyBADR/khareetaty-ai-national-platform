import SwiftUI

struct LoginView: View {
    @EnvironmentObject var appState: AppState
    
    @State private var email = ""
    @State private var password = ""
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var showError = false
    
    var body: some View {
        GeometryReader { geometry in
            HStack(spacing: 0) {
                // Left side - Branding
                VStack {
                    Spacer()
                    
                    Image(systemName: "shield.checkered")
                        .font(.system(size: 80))
                        .foregroundColor(DeevoColors.accent)
                    
                    Text("Deevo Sentinel")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .padding(.top, 20)
                    
                    Text("Sovereign Claims Decision Infrastructure")
                        .font(.title3)
                        .foregroundColor(.white.opacity(0.8))
                        .padding(.top, 8)
                    
                    Spacer()
                    
                    VStack(spacing: 4) {
                        Text("Powered by")
                            .font(.caption2)
                            .foregroundColor(.white.opacity(0.5))
                        Text("Deevo Analytics")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(DeevoColors.accent)
                    }
                    .padding(.bottom, 40)
                }
                .frame(width: geometry.size.width * 0.4)
                .background(
                    LinearGradient(
                        colors: [DeevoColors.primary, DeevoColors.secondary],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                
                // Right side - Login Form
                VStack(spacing: 30) {
                    Spacer()
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Welcome Back")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                        
                        Text("Sign in to continue to your dashboard")
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    
                    VStack(spacing: 20) {
                        // Email Field
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Email")
                                .font(.subheadline)
                                .fontWeight(.medium)
                            
                            TextField("Enter your email", text: $email)
                                .textFieldStyle(.plain)
                                .padding()
                                .background(Color(.systemGray6))
                                .cornerRadius(10)
                                .textContentType(.emailAddress)
                                .autocapitalization(.none)
                                .keyboardType(.emailAddress)
                        }
                        
                        // Password Field
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Password")
                                .font(.subheadline)
                                .fontWeight(.medium)
                            
                            SecureField("Enter your password", text: $password)
                                .textFieldStyle(.plain)
                                .padding()
                                .background(Color(.systemGray6))
                                .cornerRadius(10)
                                .textContentType(.password)
                        }
                    }
                    
                    // Login Button
                    Button(action: login) {
                        HStack {
                            if isLoading {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            } else {
                                Text("Sign In")
                                    .fontWeight(.semibold)
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(isFormValid ? DeevoColors.accent : Color.gray)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }
                    .disabled(!isFormValid || isLoading)
                    
                    // Demo Credentials
                    VStack(spacing: 8) {
                        Text("Demo Credentials")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        HStack(spacing: 20) {
                            Button("Admin") {
                                email = "admin@deevo.ai"
                                password = "admin123456"
                            }
                            .font(.caption)
                            .foregroundColor(DeevoColors.secondary)
                            
                            Button("Inspector") {
                                email = "john.smith@deevo.ai"
                                password = "inspector123"
                            }
                            .font(.caption)
                            .foregroundColor(DeevoColors.secondary)
                        }
                    }
                    .padding(.top, 10)
                    
                    Spacer()
                }
                .padding(60)
                .frame(width: geometry.size.width * 0.6)
                .background(Color(.systemBackground))
            }
        }
        .ignoresSafeArea()
        .alert("Login Error", isPresented: $showError) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(errorMessage ?? "An error occurred")
        }
    }
    
    private var isFormValid: Bool {
        !email.isEmpty && !password.isEmpty && password.count >= 8
    }
    
    private func login() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                let response = try await APIService.shared.login(email: email, password: password)
                
                await MainActor.run {
                    appState.login(token: response.token, user: response.user)
                    isLoading = false
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    showError = true
                    isLoading = false
                }
            }
        }
    }
}

#Preview {
    LoginView()
        .environmentObject(AppState())
}
