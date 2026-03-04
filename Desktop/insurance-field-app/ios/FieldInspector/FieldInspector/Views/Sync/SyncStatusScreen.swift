// SyncStatusScreen.swift
// Livegenic-style sync queue display
// DEEVO Field Inspector

import SwiftUI

struct SyncStatusScreen: View {
    @EnvironmentObject var syncService: SyncService
    @State private var selectedTab: SyncTab = .claims
    @State private var isSyncingAll = false

    enum SyncTab: String, CaseIterable {
        case claims = "CLAIMS"
        case files  = "FILES"
    }

    var body: some View {
        VStack(spacing: 0) {

            // Online/offline status bar
            HStack(spacing: 8) {
                Circle()
                    .fill(syncService.isOnline ? Color(hex: "22C55E") : Color(hex: "6B7280"))
                    .frame(width: 8, height: 8)
                Text(syncService.isOnline ? "Online · Auto-sync every 30s" : "Offline · Will sync when connected")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Spacer()
                Toggle("", isOn: .constant(true))
                    .labelsHidden()
                    .tint(Color(hex: "F59E0B"))
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 10)
            .background(Color(hex: "112238"))

            // CLAIMS / FILES tab switcher
            HStack(spacing: 0) {
                ForEach(SyncTab.allCases, id: \.self) { tab in
                    Button {
                        withAnimation(.easeInOut(duration: 0.15)) { selectedTab = tab }
                    } label: {
                        Text(tab.rawValue)
                            .font(.caption.weight(.bold))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(selectedTab == tab
                                ? Color(hex: "F59E0B").opacity(0.15) : Color.clear)
                            .foregroundStyle(selectedTab == tab
                                ? Color(hex: "F59E0B") : Color.secondary)
                    }
                }
            }
            .background(Color(hex: "0D1B2A"))
            .overlay(alignment: .bottom) {
                Rectangle().fill(Color(hex: "1E3A5F")).frame(height: 1)
            }

            // Claim rows
            ScrollView {
                LazyVStack(spacing: 1) {
                    ForEach(0..<5) { i in
                        SyncRow(
                            claimNumber: "FI-26022\(i)-A00\(i+1)",
                            adjuster: ["Ahmed Al-Rashidi","Fatima Al-Ali","Omar Al-Mahmoud","Sara Al-Hassan","Khalid Al-Mutairi"][i],
                            status: ["synced","pending","failed","syncing","synced"][i],
                            fileSize: ["304 KB","420 KB","266 KB","188 KB","360 KB"][i],
                            showFileSize: selectedTab == .files
                        )
                    }
                }
                .padding(.top, 1)
            }
        }
        .background(Color(hex: "0B1829"))
        .navigationTitle("Sync Status")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    Task {
                        isSyncingAll = true
                        try? await Task.sleep(nanoseconds: 2_000_000_000)
                        isSyncingAll = false
                    }
                } label: {
                    if isSyncingAll {
                        ProgressView().scaleEffect(0.8)
                    } else {
                        Label("Sync All", systemImage: "arrow.triangle.2.circlepath")
                            .foregroundStyle(Color(hex: "F59E0B"))
                    }
                }
                .disabled(isSyncingAll || !syncService.isOnline)
            }
        }
    }
}

struct SyncRow: View {
    let claimNumber: String
    let adjuster: String
    let status: String
    let fileSize: String
    let showFileSize: Bool

    var body: some View {
        HStack(spacing: 12) {
            RoundedRectangle(cornerRadius: 8)
                .fill(Color(hex: "1E3A5F"))
                .frame(width: 52, height: 52)
                .overlay(
                    Image(systemName: showFileSize ? "photo.stack.fill" : "car.fill")
                        .foregroundStyle(Color(hex: "F59E0B"))
                )

            VStack(alignment: .leading, spacing: 4) {
                Text(claimNumber)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.white)
                Text(adjuster)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text("Last Sync: never")
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }

            Spacer()

            VStack(alignment: .trailing, spacing: 6) {
                if showFileSize {
                    Text(fileSize)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.white)
                    Button("Sync") {}
                        .font(.caption.weight(.medium))
                        .foregroundStyle(Color(hex: "F59E0B"))
                        .padding(.horizontal, 10).padding(.vertical, 4)
                        .background(Color(hex: "F59E0B").opacity(0.15))
                        .cornerRadius(6)
                } else {
                    syncIcon
                }
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(Color(hex: "112238"))
    }

    @ViewBuilder
    var syncIcon: some View {
        switch status {
        case "synced":
            Label("Synced", systemImage: "checkmark.icloud.fill")
                .font(.caption.weight(.medium)).foregroundStyle(Color(hex: "22C55E"))
        case "syncing":
            Label("Syncing...", systemImage: "arrow.clockwise.icloud.fill")
                .font(.caption.weight(.medium)).foregroundStyle(Color(hex: "3B82F6"))
        case "failed":
            Label("Failed", systemImage: "exclamationmark.icloud.fill")
                .font(.caption.weight(.medium)).foregroundStyle(Color(hex: "EF4444"))
        default:
            Label("Pending", systemImage: "clock.fill")
                .font(.caption.weight(.medium)).foregroundStyle(Color(hex: "F59E0B"))
        }
    }
}

#Preview {
    NavigationStack {
        SyncStatusScreen()
            .environmentObject(SyncService.shared)
    }
}
