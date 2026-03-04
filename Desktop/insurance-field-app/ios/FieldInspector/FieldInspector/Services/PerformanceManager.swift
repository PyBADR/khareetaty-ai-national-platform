import Foundation
import SwiftUI
import GRDB

// MARK: - Performance Manager

/// Centralized performance optimization manager for Deevo Sentinel
final class PerformanceManager: ObservableObject {
    static let shared = PerformanceManager()
    
    // MARK: - Configuration
    
    struct Config {
        static let defaultPageSize = 50
        static let maxPageSize = 100
        static let prefetchThreshold = 10 // Load more when 10 items from end
        static let imageCompressionQuality: CGFloat = 0.7
        static let maxImageDimension: CGFloat = 1920
        static let thumbnailSize: CGFloat = 200
        static let memoryCacheLimit = 50 * 1024 * 1024 // 50MB
        static let diskCacheLimit = 200 * 1024 * 1024 // 200MB
    }
    
    // MARK: - Published State
    
    @Published var isLoadingMore = false
    @Published var memoryUsage: UInt64 = 0
    @Published var cacheSize: UInt64 = 0
    
    // MARK: - Private Properties
    
    private let imageCache = NSCache<NSString, UIImage>()
    private let operationQueue: OperationQueue
    private var backgroundTasks: [String: Task<Void, Never>] = [:]
    
    private init() {
        operationQueue = OperationQueue()
        operationQueue.maxConcurrentOperationCount = 4
        operationQueue.qualityOfService = .userInitiated
        
        imageCache.countLimit = 100
        imageCache.totalCostLimit = Config.memoryCacheLimit
        
        setupMemoryWarningObserver()
    }
    
    // MARK: - Memory Management
    
    private func setupMemoryWarningObserver() {
        NotificationCenter.default.addObserver(
            forName: UIApplication.didReceiveMemoryWarningNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.handleMemoryWarning()
        }
    }
    
    func handleMemoryWarning() {
        imageCache.removeAllObjects()
        cancelAllBackgroundTasks()
        print("[Performance] Memory warning - cleared caches")
    }
    
    func updateMemoryUsage() {
        var info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size) / 4
        
        let result = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
            }
        }
        
        if result == KERN_SUCCESS {
            memoryUsage = info.resident_size
        }
    }
    
    // MARK: - Background Task Management
    
    func scheduleBackgroundTask(id: String, priority: TaskPriority = .medium, operation: @escaping () async -> Void) {
        cancelBackgroundTask(id: id)
        
        let task = Task(priority: priority) {
            await operation()
            _ = await MainActor.run {
                self.backgroundTasks.removeValue(forKey: id)
            }
        }
        
        backgroundTasks[id] = task
    }
    
    func cancelBackgroundTask(id: String) {
        backgroundTasks[id]?.cancel()
        backgroundTasks.removeValue(forKey: id)
    }
    
    func cancelAllBackgroundTasks() {
        backgroundTasks.values.forEach { $0.cancel() }
        backgroundTasks.removeAll()
    }
}

// MARK: - Pagination Support

struct PaginatedResult<T> {
    let items: [T]
    let totalCount: Int
    let page: Int
    let pageSize: Int
    let hasMore: Bool
    
    var nextPage: Int? {
        hasMore ? page + 1 : nil
    }
}

class PaginationState: ObservableObject {
    @Published var currentPage = 0
    @Published var isLoading = false
    @Published var hasMore = true
    @Published var totalCount = 0
    
    let pageSize: Int
    
    init(pageSize: Int = PerformanceManager.Config.defaultPageSize) {
        self.pageSize = pageSize
    }
    
    func reset() {
        currentPage = 0
        isLoading = false
        hasMore = true
        totalCount = 0
    }
    
    func update<T>(with result: PaginatedResult<T>) {
        currentPage = result.page
        hasMore = result.hasMore
        totalCount = result.totalCount
        isLoading = false
    }
}

// MARK: - Lazy Loading Claims

extension DatabaseManager {
    
    /// Fetch claims with pagination for smooth scrolling
    func fetchClaimsPaginated(
        page: Int,
        pageSize: Int = PerformanceManager.Config.defaultPageSize,
        status: ClaimStatus? = nil,
        searchQuery: String? = nil
    ) throws -> PaginatedResult<Claim> {
        let offset = page * pageSize
        
        return try database.read { db in
            var query = Claim.all()
            
            // Apply status filter
            if let status = status {
                query = query.filter(Column("status") == status.rawValue)
            }
            
            // Apply search filter
            if let search = searchQuery, !search.isEmpty {
                let pattern = "%\(search)%"
                query = query.filter(
                    Column("claimNumber").like(pattern) ||
                    Column("customerName").like(pattern) ||
                    Column("policyNumber").like(pattern)
                )
            }
            
            // Get total count
            let totalCount = try query.fetchCount(db)
            
            // Fetch page
            let items = try query
                .order(Column("createdAt").desc)
                .limit(pageSize, offset: offset)
                .fetchAll(db)
            
            let hasMore = offset + items.count < totalCount
            
            return PaginatedResult(
                items: items,
                totalCount: totalCount,
                page: page,
                pageSize: pageSize,
                hasMore: hasMore
            )
        }
    }
}

// MARK: - Image Compression

extension PerformanceManager {
    
    /// Compress image for upload with quality and size optimization
    func compressImage(_ image: UIImage, maxDimension: CGFloat? = nil) -> Data? {
        let maxDim = maxDimension ?? Config.maxImageDimension
        
        // Resize if needed
        let resizedImage = resizeImage(image, maxDimension: maxDim)
        
        // Compress to JPEG
        return resizedImage.jpegData(compressionQuality: Config.imageCompressionQuality)
    }
    
    /// Create thumbnail for list display
    func createThumbnail(_ image: UIImage) -> UIImage {
        return resizeImage(image, maxDimension: Config.thumbnailSize)
    }
    
    private func resizeImage(_ image: UIImage, maxDimension: CGFloat) -> UIImage {
        let size = image.size
        
        // Check if resize needed
        guard size.width > maxDimension || size.height > maxDimension else {
            return image
        }
        
        // Calculate new size maintaining aspect ratio
        let ratio = min(maxDimension / size.width, maxDimension / size.height)
        let newSize = CGSize(width: size.width * ratio, height: size.height * ratio)
        
        // Render resized image
        let renderer = UIGraphicsImageRenderer(size: newSize)
        return renderer.image { _ in
            image.draw(in: CGRect(origin: .zero, size: newSize))
        }
    }
    
    /// Get compressed image data size
    func getCompressedSize(_ image: UIImage) -> Int {
        return compressImage(image)?.count ?? 0
    }
}

// MARK: - Image Caching

extension PerformanceManager {
    
    func cacheImage(_ image: UIImage, forKey key: String) {
        let cost = image.jpegData(compressionQuality: 1.0)?.count ?? 0
        imageCache.setObject(image, forKey: key as NSString, cost: cost)
    }
    
    func getCachedImage(forKey key: String) -> UIImage? {
        return imageCache.object(forKey: key as NSString)
    }
    
    func removeCachedImage(forKey key: String) {
        imageCache.removeObject(forKey: key as NSString)
    }
    
    func clearImageCache() {
        imageCache.removeAllObjects()
    }
}

// MARK: - Lazy Loading View Modifier

struct LazyLoadModifier: ViewModifier {
    let itemIndex: Int
    let totalItems: Int
    let threshold: Int
    let loadMore: () -> Void
    
    func body(content: Content) -> some View {
        content
            .onAppear {
                if itemIndex >= totalItems - threshold {
                    loadMore()
                }
            }
    }
}

extension View {
    func onReachingEnd(
        itemIndex: Int,
        totalItems: Int,
        threshold: Int = PerformanceManager.Config.prefetchThreshold,
        loadMore: @escaping () -> Void
    ) -> some View {
        modifier(LazyLoadModifier(
            itemIndex: itemIndex,
            totalItems: totalItems,
            threshold: threshold,
            loadMore: loadMore
        ))
    }
}

// MARK: - Optimized Claims List View

struct OptimizedClaimsListView: View {
    @StateObject private var pagination = PaginationState()
    @State private var claims: [Claim] = []
    @State private var searchText = ""
    @State private var selectedStatus: ClaimStatus?
    
    var body: some View {
        VStack(spacing: 0) {
            // Search bar
            searchBar
            
            // Status filter
            statusFilter
            
            // Claims list with lazy loading
            claimsList
        }
        .background(DeevoColors.backgroundDark)
        .task {
            await loadInitialClaims()
        }
    }
    
    private var searchBar: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(DeevoColors.textSecondary)
            
            TextField("Search claims...", text: $searchText)
                .textFieldStyle(.plain)
                .foregroundColor(DeevoColors.textPrimary)
                .onChange(of: searchText) { _, _ in
                    Task {
                        pagination.reset()
                        await loadInitialClaims()
                    }
                }
        }
        .padding()
        .background(DeevoColors.surfaceElevated)
    }
    
    private var statusFilter: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                FilterChip(title: "All", isSelected: selectedStatus == nil) {
                    selectedStatus = nil
                    Task {
                        pagination.reset()
                        await loadInitialClaims()
                    }
                }
                
                ForEach(ClaimStatus.allCases, id: \.self) { status in
                    FilterChip(title: status.displayName, isSelected: selectedStatus == status) {
                        selectedStatus = status
                        Task {
                            pagination.reset()
                            await loadInitialClaims()
                        }
                    }
                }
            }
            .padding(.horizontal)
        }
        .padding(.vertical, 8)
    }
    
    private var claimsList: some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                ForEach(Array(claims.enumerated()), id: \.element.id) { index, claim in
                    OptimizedClaimRowView(claim: claim)
                        .onReachingEnd(
                            itemIndex: index,
                            totalItems: claims.count
                        ) {
                            Task {
                                await loadMoreClaims()
                            }
                        }
                }
                
                if pagination.isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: DeevoColors.accent))
                        .padding()
                }
                
                if !pagination.hasMore && !claims.isEmpty {
                    Text("All \(pagination.totalCount) claims loaded")
                        .font(DeevoTypography.caption)
                        .foregroundColor(DeevoColors.textSecondary)
                        .padding()
                }
            }
            .padding()
        }
    }
    
    private func loadInitialClaims() async {
        guard !pagination.isLoading else { return }
        pagination.isLoading = true
        
        do {
            let result = try DatabaseManager.shared.fetchClaimsPaginated(
                page: 0,
                status: selectedStatus,
                searchQuery: searchText.isEmpty ? nil : searchText
            )
            
            await MainActor.run {
                claims = result.items
                pagination.update(with: result)
            }
        } catch {
            print("[Performance] Failed to load claims: \(error)")
            pagination.isLoading = false
        }
    }
    
    private func loadMoreClaims() async {
        guard !pagination.isLoading && pagination.hasMore else { return }
        pagination.isLoading = true
        
        do {
            let result = try DatabaseManager.shared.fetchClaimsPaginated(
                page: pagination.currentPage + 1,
                status: selectedStatus,
                searchQuery: searchText.isEmpty ? nil : searchText
            )
            
            await MainActor.run {
                claims.append(contentsOf: result.items)
                pagination.update(with: result)
            }
        } catch {
            print("[Performance] Failed to load more claims: \(error)")
            pagination.isLoading = false
        }
    }
}

// MARK: - Filter Chip

struct FilterChip: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(DeevoTypography.caption)
                .fontWeight(isSelected ? .semibold : .regular)
                .foregroundColor(isSelected ? DeevoColors.backgroundDark : DeevoColors.textPrimary)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(
                    Capsule()
                        .fill(isSelected ? DeevoColors.accent : DeevoColors.surfaceElevated)
                )
        }
    }
}

// MARK: - Claim Row View (Optimized)

struct OptimizedClaimRowView: View {
    let claim: Claim
    
    var body: some View {
        HStack(spacing: 16) {
            // Status indicator
            Circle()
                .fill(claim.status.color)
                .frame(width: 12, height: 12)
            
            // Claim info
            VStack(alignment: .leading, spacing: 4) {
                Text(claim.claimNumber)
                    .font(DeevoTypography.bodyLarge)
                    .fontWeight(.semibold)
                    .foregroundColor(DeevoColors.textPrimary)
                
                Text(claim.customerName)
                    .font(DeevoTypography.bodyMedium)
                    .foregroundColor(DeevoColors.textSecondary)
            }
            
            Spacer()
            
            // Risk score badge
            if let riskScore = claim.riskScore {
                RiskBadge(score: riskScore)
            }
            
            // Chevron
            Image(systemName: "chevron.right")
                .foregroundColor(DeevoColors.textSecondary)
        }
        .padding()
        .background(DeevoColors.surfaceElevated)
        .cornerRadius(12)
    }
}

// MARK: - Risk Badge

struct RiskBadge: View {
    let score: Int
    
    var riskBand: RiskBand {
        RiskBand.from(score: score)
    }
    
    var body: some View {
        Text("\(score)")
            .font(DeevoTypography.caption)
            .fontWeight(.bold)
            .foregroundColor(.white)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(
                Capsule()
                    .fill(riskBand.color)
            )
    }
}

// MARK: - Background Upload Queue

actor BackgroundUploadQueue {
    static let shared = BackgroundUploadQueue()
    
    private var queue: [UploadTask] = []
    private var isProcessing = false
    private let maxConcurrent = 3
    private var activeUploads = 0
    
    struct UploadTask: Identifiable {
        let id = UUID()
        let claimId: String
        let imageData: Data
        let filename: String
        let priority: Priority
        var retryCount = 0
        
        enum Priority: Int, Comparable {
            case low = 0
            case normal = 1
            case high = 2
            
            static func < (lhs: Priority, rhs: Priority) -> Bool {
                lhs.rawValue < rhs.rawValue
            }
        }
    }
    
    func enqueue(_ task: UploadTask) {
        queue.append(task)
        queue.sort { $0.priority > $1.priority }
        
        Task {
            await processQueue()
        }
    }
    
    func cancelAll() {
        queue.removeAll()
    }
    
    func cancelForClaim(_ claimId: String) {
        queue.removeAll { $0.claimId == claimId }
    }
    
    var pendingCount: Int {
        queue.count
    }
    
    private func processQueue() async {
        guard !isProcessing else { return }
        isProcessing = true
        
        while !queue.isEmpty && activeUploads < maxConcurrent {
            let task = queue.removeFirst()
            activeUploads += 1
            
            Task {
                await processTask(task)
                activeUploads -= 1
                await processQueue()
            }
        }
        
        isProcessing = false
    }
    
    private func processTask(_ task: UploadTask) async {
        do {
            // Simulate upload - replace with actual API call
            try await Task.sleep(nanoseconds: 1_000_000_000) // 1 second
            print("[Upload] Completed: \(task.filename) for claim \(task.claimId)")
        } catch {
            if task.retryCount < 3 {
                var retryTask = task
                retryTask.retryCount += 1
                queue.append(retryTask)
                print("[Upload] Retry \(retryTask.retryCount) for: \(task.filename)")
            } else {
                print("[Upload] Failed after 3 retries: \(task.filename)")
            }
        }
    }
}

// MARK: - Performance Monitoring View

struct PerformanceMonitorView: View {
    @ObservedObject var performanceManager = PerformanceManager.shared
    @State private var uploadQueueCount = 0
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Performance Monitor")
                .font(DeevoTypography.headlineMedium)
                .foregroundColor(DeevoColors.textPrimary)
            
            // Memory usage
            MetricRow(
                title: "Memory Usage",
                value: formatBytes(performanceManager.memoryUsage),
                icon: "memorychip"
            )
            
            // Cache size
            MetricRow(
                title: "Image Cache",
                value: formatBytes(performanceManager.cacheSize),
                icon: "photo.stack"
            )
            
            // Upload queue
            MetricRow(
                title: "Pending Uploads",
                value: "\(uploadQueueCount)",
                icon: "arrow.up.circle"
            )
            
            // Actions
            HStack(spacing: 12) {
                Button("Clear Cache") {
                    performanceManager.clearImageCache()
                }
                .buttonStyle(.bordered)
                
                Button("Update Stats") {
                    performanceManager.updateMemoryUsage()
                    Task {
                        uploadQueueCount = await BackgroundUploadQueue.shared.pendingCount
                    }
                }
                .buttonStyle(.bordered)
            }
        }
        .padding()
        .background(DeevoColors.surfaceElevated)
        .cornerRadius(16)
        .task {
            performanceManager.updateMemoryUsage()
            uploadQueueCount = await BackgroundUploadQueue.shared.pendingCount
        }
    }
    
    private func formatBytes(_ bytes: UInt64) -> String {
        let formatter = ByteCountFormatter()
        formatter.countStyle = .memory
        return formatter.string(fromByteCount: Int64(bytes))
    }
}

struct MetricRow: View {
    let title: String
    let value: String
    let icon: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(DeevoColors.accent)
                .frame(width: 24)
            
            Text(title)
                .font(DeevoTypography.bodyMedium)
                .foregroundColor(DeevoColors.textSecondary)
            
            Spacer()
            
            Text(value)
                .font(DeevoTypography.bodyLarge)
                .fontWeight(.semibold)
                .foregroundColor(DeevoColors.textPrimary)
        }
    }
}
