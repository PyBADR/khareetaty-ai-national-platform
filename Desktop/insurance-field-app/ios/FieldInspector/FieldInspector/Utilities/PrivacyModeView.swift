import SwiftUI

// MARK: - Privacy Mode Toggle View

struct PrivacyModeToggle: View {
    @State private var isPrivacyModeEnabled = SecurityManager.shared.isPrivacyModeEnabled
    
    var body: some View {
        Toggle(isOn: $isPrivacyModeEnabled) {
            HStack(spacing: 12) {
                Image(systemName: isPrivacyModeEnabled ? "eye.slash.fill" : "eye.fill")
                    .foregroundColor(isPrivacyModeEnabled ? DeevoColors.accent : DeevoColors.textSecondary)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text("Privacy Mode")
                        .font(DeevoTypography.labelMedium)
                        .foregroundColor(DeevoColors.textPrimary)
                    Text(isPrivacyModeEnabled ? "PII data is hidden" : "PII data is visible")
                        .font(DeevoTypography.labelSmall)
                        .foregroundColor(DeevoColors.textTertiary)
                }
            }
        }
        .toggleStyle(SwitchToggleStyle(tint: DeevoColors.accent))
        .onChange(of: isPrivacyModeEnabled) { _, newValue in
            if newValue {
                SecurityManager.shared.enablePrivacyMode()
            } else {
                SecurityManager.shared.disablePrivacyMode()
            }
        }
    }
}

// MARK: - Privacy Masked Text

struct PrivacyMaskedText: View {
    let text: String?
    let maskType: PIIMaskType
    
    @State private var isPrivacyModeEnabled = SecurityManager.shared.isPrivacyModeEnabled
    
    enum PIIMaskType {
        case email
        case phone
        case name
        case address
        case claimNumber
        case policyNumber
        case custom(mask: String)
    }
    
    var maskedText: String {
        let security = SecurityManager.shared
        
        switch maskType {
        case .email:
            return security.maskEmail(text)
        case .phone:
            return security.maskPhone(text)
        case .name:
            return security.maskName(text)
        case .address:
            return security.maskAddress(text)
        case .claimNumber:
            return security.maskClaimNumber(text)
        case .policyNumber:
            return security.maskPolicyNumber(text)
        case .custom(let mask):
            return isPrivacyModeEnabled ? mask : (text ?? mask)
        }
    }
    
    var body: some View {
        Text(maskedText)
    }
}

// MARK: - Privacy Settings View

struct PrivacySettingsView: View {
    @State private var isPrivacyModeEnabled = SecurityManager.shared.isPrivacyModeEnabled
    @State private var showingResetAlert = false
    
    var body: some View {
        List {
            Section {
                PrivacyModeToggle()
            } header: {
                Text("Display Settings")
            } footer: {
                Text("When enabled, personally identifiable information (PII) will be masked throughout the app. Useful for demos and screen sharing.")
            }
            
            Section {
                HStack {
                    Image(systemName: "lock.shield.fill")
                        .foregroundColor(DeevoColors.success)
                    Text("Database Encryption")
                    Spacer()
                    Text("AES-256")
                        .foregroundColor(DeevoColors.textSecondary)
                }
                
                HStack {
                    Image(systemName: "key.fill")
                        .foregroundColor(DeevoColors.success)
                    Text("Key Storage")
                    Spacer()
                    Text("Secure Enclave")
                        .foregroundColor(DeevoColors.textSecondary)
                }
                
                HStack {
                    Image(systemName: "network.badge.shield.half.filled")
                        .foregroundColor(DeevoColors.success)
                    Text("API Communication")
                    Spacer()
                    Text("TLS 1.3")
                        .foregroundColor(DeevoColors.textSecondary)
                }
            } header: {
                Text("Security Status")
            }
            
            Section {
                Button(role: .destructive) {
                    showingResetAlert = true
                } label: {
                    HStack {
                        Image(systemName: "trash")
                        Text("Clear Local Data")
                    }
                }
            } header: {
                Text("Data Management")
            } footer: {
                Text("This will remove all locally cached data. You will need to sync again to restore your claims.")
            }
        }
        .navigationTitle("Privacy & Security")
        .navigationBarTitleDisplayMode(.inline)
        .alert("Clear Local Data?", isPresented: $showingResetAlert) {
            Button("Cancel", role: .cancel) {}
            Button("Clear", role: .destructive) {
                // Clear local data
            }
        } message: {
            Text("This action cannot be undone. All locally stored claims and settings will be removed.")
        }
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        PrivacySettingsView()
    }
}
