import Foundation
import GRDB

// MARK: - Media Type

enum MediaType: String, Codable, CaseIterable, DatabaseValueConvertible {
    case photo = "photo"
    case video = "video"
    case document = "document"
    
    var displayName: String {
        switch self {
        case .photo: return "Photo"
        case .video: return "Video"
        case .document: return "Document"
        }
    }
    
    var iconName: String {
        switch self {
        case .photo: return "photo"
        case .video: return "video"
        case .document: return "doc"
        }
    }
}

// MARK: - Media Asset Model

struct MediaAsset: Identifiable, Codable, Equatable {
    var id: String
    var claimId: String
    var inspectionId: String?
    var type: MediaType
    var filename: String
    var mimeType: String
    var fileSize: Int
    var localPath: String?
    var remoteUrl: String?
    var thumbnailPath: String?
    var tags: [String]
    var caption: String?
    var latitude: Double?
    var longitude: Double?
    var capturedAt: Date?
    var createdAt: Date
    var updatedAt: Date
    var syncStatus: SyncStatus
    var syncError: String?
    
    init(
        id: String = UUID().uuidString,
        claimId: String,
        inspectionId: String? = nil,
        type: MediaType,
        filename: String,
        mimeType: String,
        fileSize: Int,
        localPath: String? = nil,
        remoteUrl: String? = nil,
        thumbnailPath: String? = nil,
        tags: [String] = [],
        caption: String? = nil,
        latitude: Double? = nil,
        longitude: Double? = nil,
        capturedAt: Date? = nil,
        createdAt: Date = Date(),
        updatedAt: Date = Date(),
        syncStatus: SyncStatus = .pending,
        syncError: String? = nil
    ) {
        self.id = id
        self.claimId = claimId
        self.inspectionId = inspectionId
        self.type = type
        self.filename = filename
        self.mimeType = mimeType
        self.fileSize = fileSize
        self.localPath = localPath
        self.remoteUrl = remoteUrl
        self.thumbnailPath = thumbnailPath
        self.tags = tags
        self.caption = caption
        self.latitude = latitude
        self.longitude = longitude
        self.capturedAt = capturedAt
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.syncStatus = syncStatus
        self.syncError = syncError
    }
    
    var tagsString: String {
        get { tags.joined(separator: ",") }
        set { tags = newValue.split(separator: ",").map { String($0).trimmingCharacters(in: .whitespaces) } }
    }
    
    var fileSizeFormatted: String {
        let formatter = ByteCountFormatter()
        formatter.countStyle = .file
        return formatter.string(fromByteCount: Int64(fileSize))
    }
}

extension MediaAsset: FetchableRecord, PersistableRecord {
    static let databaseTableName = "media_assets"
    
    // Custom encoding for tags array
    func encode(to container: inout PersistenceContainer) {
        container["id"] = id
        container["claimId"] = claimId
        container["inspectionId"] = inspectionId
        container["type"] = type
        container["filename"] = filename
        container["mimeType"] = mimeType
        container["fileSize"] = fileSize
        container["localPath"] = localPath
        container["remoteUrl"] = remoteUrl
        container["thumbnailPath"] = thumbnailPath
        container["tags"] = tagsString
        container["caption"] = caption
        container["latitude"] = latitude
        container["longitude"] = longitude
        container["capturedAt"] = capturedAt
        container["createdAt"] = createdAt
        container["updatedAt"] = updatedAt
        container["syncStatus"] = syncStatus
        container["syncError"] = syncError
    }
}
