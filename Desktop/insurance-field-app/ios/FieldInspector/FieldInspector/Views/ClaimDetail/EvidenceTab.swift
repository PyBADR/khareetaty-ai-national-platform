import SwiftUI

struct EvidenceTab: View {
    let claimId: String
    
    @State private var mediaAssets: [MediaAsset] = []
    @State private var isLoading = false
    @State private var showCaptureSheet = false
    @State private var selectedAsset: MediaAsset?
    @State private var filterType: MediaType?
    
    var body: some View {
        VStack(spacing: 0) {
            // Filter bar
            HStack {
                EvidenceFilterChip(title: "All", isSelected: filterType == nil) {
                    filterType = nil
                }
                EvidenceFilterChip(title: "Photos", isSelected: filterType == .photo) {
                    filterType = .photo
                }
                EvidenceFilterChip(title: "Videos", isSelected: filterType == .video) {
                    filterType = .video
                }
                EvidenceFilterChip(title: "Documents", isSelected: filterType == .document) {
                    filterType = .document
                }
                
                Spacer()
                
                Button(action: { showCaptureSheet = true }) {
                    Label("Add", systemImage: "plus")
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()
            
            Divider()
            
            if isLoading {
                SkeletonClaimDetail()
            } else if filteredAssets.isEmpty {
                Spacer()
                VStack(spacing: 16) {
                    Image(systemName: "photo.stack")
                        .font(.system(size: 60))
                        .foregroundColor(.secondary)
                    Text("No evidence captured")
                        .font(.headline)
                    Text("Capture photos, videos, or upload documents to document this claim.")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding()
                Spacer()
            } else {
                // Grid view
                ScrollView {
                    LazyVGrid(columns: [
                        GridItem(.adaptive(minimum: 150, maximum: 200), spacing: 16)
                    ], spacing: 16) {
                        ForEach(filteredAssets) { asset in
                            MediaAssetCard(asset: asset)
                                .onTapGesture {
                                    selectedAsset = asset
                                }
                        }
                    }
                    .padding()
                }
            }
        }
        .sheet(isPresented: $showCaptureSheet) {
            EvidenceCaptureSheet(claimId: claimId) { newAsset in
                mediaAssets.append(newAsset)
            }
        }
        .sheet(item: $selectedAsset) { asset in
            MediaAssetDetailView(asset: asset)
        }
        .onAppear {
            loadMediaAssets()
        }
    }
    
    private var filteredAssets: [MediaAsset] {
        if let filterType = filterType {
            return mediaAssets.filter { $0.type == filterType }
        }
        return mediaAssets
    }
    
    private func loadMediaAssets() {
        isLoading = true
        Task {
            do {
                let response = try await APIService.shared.getMediaAssets(claimId: claimId)
                await MainActor.run {
                    mediaAssets = response.mediaAssets
                    isLoading = false
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                }
            }
        }
    }
}

// MARK: - Filter Chip

private struct EvidenceFilterChip: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.subheadline)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(isSelected ? DeevoColors.accent : Color(.systemGray5))
                .foregroundColor(isSelected ? .white : .primary)
                .cornerRadius(16)
        }
    }
}

// MARK: - Media Asset Card

struct MediaAssetCard: View {
    let asset: MediaAsset
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Thumbnail
            ZStack {
                Rectangle()
                    .fill(Color(.systemGray5))
                    .aspectRatio(1, contentMode: .fit)
                
                Image(systemName: asset.type.iconName)
                    .font(.system(size: 40))
                    .foregroundColor(.secondary)
                
                // Sync status indicator
                if asset.syncStatus != .synced {
                    VStack {
                        HStack {
                            Spacer()
                            Image(systemName: asset.syncStatus.iconName)
                                .foregroundColor(asset.syncStatus == .failed ? DeevoColors.error : DeevoColors.accent)
                                .padding(4)
                                .background(Color(.systemBackground))
                                .clipShape(Circle())
                        }
                        Spacer()
                    }
                    .padding(8)
                }
            }
            .cornerRadius(8)
            
            // Info
            VStack(alignment: .leading, spacing: 2) {
                Text(asset.filename)
                    .font(.caption)
                    .lineLimit(1)
                
                Text(asset.fileSizeFormatted)
                    .font(.caption2)
                    .foregroundColor(.secondary)
                
                if !asset.tags.isEmpty {
                    HStack(spacing: 4) {
                        ForEach(asset.tags.prefix(2), id: \.self) { tag in
                            Text(tag)
                                .font(.caption2)
                                .padding(.horizontal, 4)
                                .padding(.vertical, 2)
                                .background(DeevoColors.secondary.opacity(0.1))
                                .foregroundColor(DeevoColors.secondary)
                                .cornerRadius(4)
                        }
                        if asset.tags.count > 2 {
                            Text("+\(asset.tags.count - 2)")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                    }
                }
            }
        }
    }
}

// MARK: - Evidence Capture Sheet

struct EvidenceCaptureSheet: View {
    let claimId: String
    let onCaptured: (MediaAsset) -> Void
    
    @Environment(\.dismiss) private var dismiss
    @State private var selectedOption = 0
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                Text("Add Evidence")
                    .font(.title2)
                    .fontWeight(.bold)
                
                HStack(spacing: 20) {
                    CaptureOptionButton(
                        icon: "camera.fill",
                        title: "Camera",
                        subtitle: "Take a photo"
                    ) {
                        // Open camera
                    }
                    
                    CaptureOptionButton(
                        icon: "video.fill",
                        title: "Video",
                        subtitle: "Record video"
                    ) {
                        // Open video recorder
                    }
                    
                    CaptureOptionButton(
                        icon: "photo.on.rectangle",
                        title: "Gallery",
                        subtitle: "Choose existing"
                    ) {
                        // Open photo picker
                    }
                    
                    CaptureOptionButton(
                        icon: "doc.fill",
                        title: "Document",
                        subtitle: "Upload file"
                    ) {
                        // Open document picker
                    }
                }
                .padding()
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }
}

// MARK: - Capture Option Button

struct CaptureOptionButton: View {
    let icon: String
    let title: String
    let subtitle: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.system(size: 30))
                    .frame(width: 60, height: 60)
                    .background(DeevoColors.secondary.opacity(0.1))
                    .foregroundColor(DeevoColors.secondary)
                    .clipShape(Circle())
                
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Media Asset Detail View

struct MediaAssetDetailView: View {
    let asset: MediaAsset
    
    @Environment(\.dismiss) private var dismiss
    @State private var tags: String = ""
    @State private var caption: String = ""
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    // Preview
                    ZStack {
                        Rectangle()
                            .fill(Color(.systemGray5))
                            .aspectRatio(4/3, contentMode: .fit)
                        
                        Image(systemName: asset.type.iconName)
                            .font(.system(size: 80))
                            .foregroundColor(.secondary)
                    }
                    .cornerRadius(12)
                    
                    // Info
                    GroupBox("Details") {
                        VStack(alignment: .leading, spacing: 12) {
                            InfoRow(label: "Filename", value: asset.filename)
                            InfoRow(label: "Type", value: asset.type.displayName)
                            InfoRow(label: "Size", value: asset.fileSizeFormatted)
                            InfoRow(label: "Captured", value: asset.capturedAt?.formatted() ?? "Unknown")
                            InfoRow(label: "Sync Status", value: asset.syncStatus.displayName)
                        }
                    }
                    
                    // Tags
                    GroupBox("Tags") {
                        TextField("Add tags (comma separated)", text: $tags)
                            .textFieldStyle(.plain)
                    }
                    
                    // Caption
                    GroupBox("Caption") {
                        TextField("Add a caption...", text: $caption)
                            .textFieldStyle(.plain)
                    }
                }
                .padding()
            }
            .navigationTitle("Evidence Details")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") { dismiss() }
                }
                ToolbarItem(placement: .primaryAction) {
                    Button("Save") {
                        // Save changes
                        dismiss()
                    }
                }
            }
        }
        .onAppear {
            tags = asset.tags.joined(separator: ", ")
            caption = asset.caption ?? ""
        }
    }
}
