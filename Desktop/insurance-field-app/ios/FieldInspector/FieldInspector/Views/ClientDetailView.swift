// ClientDetailView.swift
// ClaimWizard-style client and contact management
// DEEVO Field Inspector

import SwiftUI

struct ClientDetailView: View {
    let claimNumber: String
    let claimantName: String
    @State private var selectedTab = 0

    private let contacts = [
        ("DR", "Damian Roofer",    "Roofing Contractor", DeevoColors.info),
        ("RP", "Robert Plumber",   "Plumber",            DeevoColors.success),
        ("CC", "Carlos Contractor","General Contractor",  DeevoColors.accent),
    ]

    var body: some View {
        VStack(spacing: 0) {

            // Client header
            VStack(alignment: .leading, spacing: 12) {
                HStack(spacing: 16) {
                    Circle()
                        .fill(DeevoColors.accent)
                        .frame(width: 60, height: 60)
                        .overlay(
                            Text(initials(from: claimantName))
                                .font(.title3.weight(.bold))
                                .foregroundStyle(.black)
                        )

                    VStack(alignment: .leading, spacing: 4) {
                        Text(claimantName)
                            .font(.title3.weight(.semibold)).foregroundStyle(.white)
                        Label("Policyholder", systemImage: "person.badge.shield.checkmark.fill")
                            .font(.caption).foregroundStyle(DeevoColors.success)
                        Text("Claim: \(claimNumber)")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    Spacer()
                    Button {
                        // Call
                    } label: {
                        Image(systemName: "phone.fill")
                            .foregroundStyle(DeevoColors.success)
                            .padding(10)
                            .background(DeevoColors.success.opacity(0.15))
                            .cornerRadius(8)
                    }
                    Button {
                        // Email
                    } label: {
                        Image(systemName: "envelope.fill")
                            .foregroundStyle(DeevoColors.info)
                            .padding(10)
                            .background(DeevoColors.info.opacity(0.15))
                            .cornerRadius(8)
                    }
                }
            }
            .padding(20)
            .background(DeevoColors.surface)

            // Tab bar
            Picker("", selection: $selectedTab) {
                Text("Contacts").tag(0)
                Text("Properties").tag(1)
                Text("Documents").tag(2)
                Text("Notes").tag(3)
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 16).padding(.vertical, 10)
            .background(DeevoColors.surfaceElevated)

            // Content
            ScrollView {
                if selectedTab == 0 {
                    VStack(spacing: 0) {
                        ForEach(contacts, id: \.0) { initials, name, role, color in
                            HStack(spacing: 12) {
                                Circle().fill(color).frame(width: 44, height: 44)
                                    .overlay(Text(initials).font(.caption.weight(.bold)).foregroundStyle(.white))
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(name).font(.subheadline.weight(.medium)).foregroundStyle(.white)
                                    Text(role).font(.caption).foregroundStyle(.secondary)
                                }
                                Spacer()
                                Image(systemName: "chevron.right").font(.caption).foregroundStyle(.tertiary)
                            }
                            .padding(.horizontal, 16).padding(.vertical, 14)
                            .background(DeevoColors.surface)
                            Divider().padding(.leading, 72)
                        }
                        Button {
                        } label: {
                            Label("Add Contact", systemImage: "plus.circle.fill")
                                .foregroundStyle(DeevoColors.accent)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding(16)
                        }
                        .background(DeevoColors.surface)
                    }
                    .cornerRadius(12)
                    .padding(16)
                } else {
                    ContentUnavailableView(
                        selectedTab == 1 ? "No Properties" : selectedTab == 2 ? "No Documents" : "No Notes",
                        systemImage: selectedTab == 1 ? "house.fill" : selectedTab == 2 ? "doc.fill" : "note.text"
                    )
                    .padding(40)
                }
            }
        }
        .background(DeevoColors.backgroundDark)
        .navigationTitle("Client Profile")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func initials(from name: String) -> String {
        name.components(separatedBy: " ").prefix(2)
            .compactMap { $0.first }.map(String.init).joined().uppercased()
    }
}

#Preview {
    NavigationStack {
        ClientDetailView(claimNumber: "FI-260227-A001", claimantName: "Ahmed Al-Rashidi")
    }
}
