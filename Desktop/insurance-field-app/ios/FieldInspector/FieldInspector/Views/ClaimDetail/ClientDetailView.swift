// ClientDetailView.swift
// ClaimWizard-style client and contact management
// DEEVO Field Inspector

import SwiftUI

struct ClientDetailView: View {
    let claimNumber: String
    let claimantName: String
    @State private var selectedTab = 0

    private let contacts = [
        ("DR", "Damian Roofer",    "Roofing Contractor", Color(hex: "3B82F6")),
        ("RP", "Robert Plumber",   "Plumber",            Color(hex: "22C55E")),
        ("CC", "Carlos Contractor","General Contractor",  Color(hex: "8B5CF6")),
    ]

    var body: some View {
        VStack(spacing: 0) {

            // Client header
            VStack(alignment: .leading, spacing: 12) {
                HStack(spacing: 16) {
                    Circle()
                        .fill(Color(hex: "F59E0B"))
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
                            .font(.caption).foregroundStyle(Color(hex: "22C55E"))
                        Text("Claim: \(claimNumber)")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    Spacer()
                    Button {
                        // Call
                    } label: {
                        Image(systemName: "phone.fill")
                            .foregroundStyle(Color(hex: "22C55E"))
                            .padding(10)
                            .background(Color(hex: "22C55E").opacity(0.15))
                            .cornerRadius(8)
                    }
                    Button {
                        // Email
                    } label: {
                        Image(systemName: "envelope.fill")
                            .foregroundStyle(Color(hex: "3B82F6"))
                            .padding(10)
                            .background(Color(hex: "3B82F6").opacity(0.15))
                            .cornerRadius(8)
                    }
                }
            }
            .padding(20)
            .background(Color(hex: "112238"))

            // Tab bar
            Picker("", selection: $selectedTab) {
                Text("Contacts").tag(0)
                Text("Properties").tag(1)
                Text("Documents").tag(2)
                Text("Notes").tag(3)
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 16).padding(.vertical, 10)
            .background(Color(hex: "0D1B2A"))

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
                            .background(Color(hex: "112238"))
                            Divider().padding(.leading, 72)
                        }
                        Button {
                        } label: {
                            Label("Add Contact", systemImage: "plus.circle.fill")
                                .foregroundStyle(Color(hex: "F59E0B"))
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding(16)
                        }
                        .background(Color(hex: "112238"))
                    }
                    .cornerRadius(12)
                    .padding(16)
                } else {
                    ContentUnavailableView(
                        selectedTab == 1 ? "No Properties" : selectedTab == 2 ? "No Documents" : "No Notes",
                        systemImage: ["house.fill", "doc.fill", "note.text"][selectedTab - 1]
                    )
                    .padding(40)
                }
            }
        }
        .background(Color(hex: "0B1829"))
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
