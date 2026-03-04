import Foundation
import GRDB
import Combine
import UIKit

/// ViewModel for managing evidence (photos, videos, documents)
@MainActor
class EvidenceViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var mediaAssets: [MediaAsset] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var selectedAsset: MediaAsset?
    @Published var uploadProgress: [String: Double] = [:]
    
    // MARK: - Computed Properties
    
    var photoAssets: [MediaAsset] {
        mediaAssets.filter { $0.type == .photo }
    }
    
    var videoAssets: [MediaAsset] {
        mediaAssets.filter { $0.type == .video }
    }
    
    var documentAssets: [MediaAsset] {
        mediaAssets.filter { $0.type == .document }
    }
    
    var totalSize: Int {
        mediaAssets.reduce(0) { $0 + $1.fileSize }
    }
    
    var pendingUploads: [MediaAsset] {
        mediaAssets.filter { $0.syncStatus == .pending || $0.syncStatus == .uploading }
    }
    
    // MARK: - Properties
    
    private let database: DatabaseManager
    private let api: APIService
    private let sync: SyncService
    private var claimId: String?
    private var inspectionId: String?
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(
        database: DatabaseManager = .shared,
        api: APIService = .shared,
        sync: SyncService = .shared
    ) {
        self.database = database
        self.api = api
        self.sync = sync
    }
    
    // MARK: - Public Methods
    
    /// Load media assets for a claim
    func loadAssets(claimId: String, inspectionId: String? = nil) async {
        self.claimId = claimId
        self.inspectionId = inspectionId
        
        isLoading = true
        errorMessage = nil
        
        do {
            mediaAssets = try await database.database.read { db in
                var query = MediaAsset.filter(Column("claimId") == claimId)
                
                if let inspectionId = inspectionId {
                    query = query.filter(Column("inspectionId") == inspectionId)
                }
                
                return try query
                    .order(Column("capturedAt").desc)
                    .fetchAll(db)
            }
            
            isLoading = false
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
        }
    }
    
    /// Add a photo from camera or library
    func addPhoto(image: UIImage, tags: [String] = [], caption: String? = nil) async throws {
        guard let claimId = claimId else {
            throw NSError(domain: "EvidenceViewModel", code: 1, userInfo: [
                NSLocalizedDescriptionKey: "No claim selected"
            ])
        }
        
        // Save image to documents directory
        let filename = "photo_\(UUID().uuidString).jpg"
        let documentsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let fileURL = documentsURL.appendingPathComponent(filename)
        
        guard let imageData = image.jpegData(compressionQuality: 0.8) else {
            throw NSError(domain: "EvidenceViewModel", code: 2, userInfo: [
                NSLocalizedDescriptionKey: "Failed to convert image to data"
            ])
        }
        
        try imageData.write(to: fileURL)
        
        // Create media asset
        let asset = MediaAsset(
            id: UUID().uuidString,
            claimId: claimId,
            inspectionId: inspectionId,
            type: .photo,
            filename: filename,
            mimeType: "image/jpeg",
            fileSize: imageData.count,
            localPath: fileURL.path,
            remoteUrl: nil,
            thumbnailPath: nil,
            tags: tags,
            caption: caption,
            latitude: nil,
            longitude: nil,
            capturedAt: Date(),
            createdAt: Date(),
            updatedAt: Date(),
            syncStatus: .pending,
            syncError: nil
        )
        
        // Save to database
        try await database.database.write { db in
            try asset.insert(db)
        }
        
        // Queue sync
        try await sync.queueSync(
            entityType: .mediaAsset,
            entityId: asset.id,
            operation: .create,
            payload: asset
        )
        
        // Reload assets
        await loadAssets(claimId: claimId, inspectionId: inspectionId)
        
        // Try to upload if online
        if sync.isOnline {
            await uploadAsset(asset)
        }
    }
    
    /// Upload a media asset to server
    func uploadAsset(_ asset: MediaAsset) async {
        guard let localPath = asset.localPath,
              FileManager.default.fileExists(atPath: localPath) else {
            return
        }
        
        uploadProgress[asset.id] = 0.0
        
        do {
            // Update status to uploading
            var updatingAsset = asset
            updatingAsset.syncStatus = .uploading
            
            let assetToUpdate = updatingAsset
            try await database.database.write { db in
                try assetToUpdate.update(db)
            }
            
            // Simulate upload progress (in real implementation, use URLSession with progress)
            for progress in stride(from: 0.0, through: 1.0, by: 0.1) {
                uploadProgress[asset.id] = progress
                try await Task.sleep(nanoseconds: 100_000_000) // 0.1 seconds
            }
            
            // Upload to server
            let fileURL = URL(fileURLWithPath: localPath)
            let response = try await api.uploadMedia(fileURL: fileURL, claimId: asset.claimId)
            
            // Update asset with remote URL
            var uploadedAsset = asset
            uploadedAsset.remoteUrl = response.url
            uploadedAsset.syncStatus = .synced
            uploadedAsset.updatedAt = Date()
            
            let uploadedToSave = uploadedAsset
            try await database.database.write { db in
                try uploadedToSave.update(db)
            }
            
            uploadProgress[asset.id] = 1.0
            
            // Reload assets
            if let claimId = claimId {
                await loadAssets(claimId: claimId, inspectionId: inspectionId)
            }
        } catch {
            // Update status to failed
            var failedAsset = asset
            failedAsset.syncStatus = .failed
            failedAsset.syncError = error.localizedDescription
            
            let failedToSave = failedAsset
            _ = try? await database.database.write { db in
                try failedToSave.update(db)
            }
            
            uploadProgress[asset.id] = nil
            errorMessage = "Upload failed: \(error.localizedDescription)"
        }
    }
    
    /// Update asset tags
    func updateTags(asset: MediaAsset, tags: [String]) async throws {
        var updated = asset
        updated.tags = tags
        updated.updatedAt = Date()
        
        let assetToSave = updated
        try await database.database.write { db in
            try assetToSave.update(db)
        }
        
        // Queue sync
        try await sync.queueSync(
            entityType: .mediaAsset,
            entityId: asset.id,
            operation: .update,
            payload: assetToSave
        )
        
        // Reload assets
        if let claimId = claimId {
            await loadAssets(claimId: claimId, inspectionId: inspectionId)
        }
    }
    
    /// Update asset caption
    func updateCaption(asset: MediaAsset, caption: String?) async throws {
        var updated = asset
        updated.caption = caption
        updated.updatedAt = Date()
        
        let assetToSave = updated
        try await database.database.write { db in
            try assetToSave.update(db)
        }
        
        // Queue sync
        try await sync.queueSync(
            entityType: .mediaAsset,
            entityId: asset.id,
            operation: .update,
            payload: assetToSave
        )
        
        // Reload assets
        if let claimId = claimId {
            await loadAssets(claimId: claimId, inspectionId: inspectionId)
        }
    }
    
    /// Delete a media asset
    func deleteAsset(_ asset: MediaAsset) async throws {
        // Delete local file
        if let localPath = asset.localPath {
            try? FileManager.default.removeItem(atPath: localPath)
        }
        
        // Delete from database
        _ = try await database.database.write { db in
            try asset.delete(db)
        }
        
        // Queue sync
        try await sync.queueSync(
            entityType: .mediaAsset,
            entityId: asset.id,
            operation: .delete,
            payload: ["id": asset.id]
        )
        
        // Reload assets
        if let claimId = claimId {
            await loadAssets(claimId: claimId, inspectionId: inspectionId)
        }
    }
    
    /// Retry failed uploads
    func retryFailedUploads() async {
        let failed = mediaAssets.filter { $0.syncStatus == .failed }
        
        for asset in failed {
            await uploadAsset(asset)
        }
    }
}
