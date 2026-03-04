import SwiftUI
import MapKit

/// Livegenic-style Claims List with Map toggle
/// Shows claims in list view or map view with pins
struct ClaimsListScreen: View {
    @EnvironmentObject var appState: AppState
    
    @State private var claims: [Claim] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var searchText = ""
    @State private var selectedClaim: Claim?
    @State private var showMapView = false
    @State private var isAvailableForJob = true
    @State private var sortBy: SortOption = .location
    @State private var showAssignmentSheet = false
    @State private var claimToAccept: Claim?
    
    enum SortOption {
        case location, date
    }
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // View toggle header
                viewToggleHeader
                
                if showMapView {
                    // Map view with claims pins
                    ClaimMapView(
                        claims: claims,
                        selectedClaim: $selectedClaim,
                        isAvailableForJob: $isAvailableForJob
                    )
                } else {
                    // List view
                    claimsListView
                }
                
                // Bottom action bar
                bottomActionBar
            }
            .background(DeevoColors.backgroundDark)
            .navigationTitle("Claims")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: {}) {
                        Image(systemName: "line.3.horizontal.decrease.circle")
                            .foregroundStyle(DeevoColors.textSecondary)
                    }
                }
            }
            .toolbarBackground(DeevoColors.primary, for: .navigationBar)
            .toolbarBackground(.visible, for: .navigationBar)
            .searchable(text: $searchText, prompt: "Search claims...")
            .onAppear {
                loadClaims()
            }
            .sheet(isPresented: $showAssignmentSheet) {
                if let claim = claimToAccept {
                    AssignmentAcceptSheet(claim: claim) {
                        // On accept
                        showAssignmentSheet = false
                        loadClaims()
                    }
                }
            }
            .navigationDestination(for: Claim.self) { claim in
                ClaimDetailView(claim: claim)
            }
        }
    }
    
    // MARK: - View Toggle Header
    private var viewToggleHeader: some View {
        HStack {
            // Map/List toggle
            HStack(spacing: 0) {
                Button(action: { showMapView = true }) {
                    Text("Map")
                        .font(.subheadline.weight(.medium))
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(showMapView ? DeevoColors.accent : Color.clear)
                        .foregroundStyle(showMapView ? .white : DeevoColors.textSecondary)
                }
                
                Button(action: { showMapView = false }) {
                    Text("List")
                        .font(.subheadline.weight(.medium))
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(!showMapView ? DeevoColors.accent : Color.clear)
                        .foregroundStyle(!showMapView ? .white : DeevoColors.textSecondary)
                }
            }
            .background(DeevoColors.surface)
            .cornerRadius(8)
            
            Spacer()
            
            // Filter button
            Button(action: {}) {
                HStack(spacing: 4) {
                    Image(systemName: "slider.horizontal.3")
                    Text("Filter")
                }
                .font(.subheadline)
                .foregroundStyle(DeevoColors.textSecondary)
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(DeevoColors.surface)
                .cornerRadius(8)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(DeevoColors.backgroundDark)
    }
    
    // MARK: - Claims List View
    private var claimsListView: some View {
        VStack(spacing: 0) {
            // Sort tabs
            HStack(spacing: 0) {
                Button(action: { sortBy = .location }) {
                    Text("By Location")
                        .font(.subheadline)
                        .foregroundStyle(sortBy == .location ? DeevoColors.accent : DeevoColors.textSecondary)
                        .padding(.vertical, 12)
                        .frame(maxWidth: .infinity)
                        .overlay(alignment: .bottom) {
                            if sortBy == .location {
                                Rectangle()
                                    .fill(DeevoColors.accent)
                                    .frame(height: 2)
                            }
                        }
                }
                
                Button(action: { sortBy = .date }) {
                    Text("By Date")
                        .font(.subheadline)
                        .foregroundStyle(sortBy == .date ? DeevoColors.accent : DeevoColors.textSecondary)
                        .padding(.vertical, 12)
                        .frame(maxWidth: .infinity)
                        .overlay(alignment: .bottom) {
                            if sortBy == .date {
                                Rectangle()
                                    .fill(DeevoColors.accent)
                                    .frame(height: 2)
                            }
                        }
                }
            }
            .background(DeevoColors.surface)
            
            // Claims list
            if isLoading && claims.isEmpty {
                ProgressView()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if claims.isEmpty {
                ContentUnavailableView(
                    "No Claims",
                    systemImage: "doc.text",
                    description: Text("No claims available at this time")
                )
            } else {
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(filteredClaims) { claim in
                            ClaimListCard(claim: claim) {
                                claimToAccept = claim
                                showAssignmentSheet = true
                            }
                        }
                    }
                    .padding(16)
                }
            }
        }
    }
    
    // MARK: - Bottom Action Bar
    private var bottomActionBar: some View {
        HStack {
            Button(action: {}) {
                HStack {
                    Image(systemName: "plus.circle.fill")
                    Text("NEW CLAIM")
                }
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(DeevoColors.accent)
            }
            
            Spacer()
            
            Button(action: {}) {
                Text("HISTORY / RECENT CLAIMS")
                    .font(.subheadline.weight(.medium))
                    .foregroundStyle(DeevoColors.textSecondary)
            }
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 16)
        .background(DeevoColors.surface)
    }
    
    private var filteredClaims: [Claim] {
        var result = claims
        
        if !searchText.isEmpty {
            result = result.filter { claim in
                claim.claimNumber.localizedCaseInsensitiveContains(searchText) ||
                claim.customerName.localizedCaseInsensitiveContains(searchText)
            }
        }
        
        // Sort
        switch sortBy {
        case .location:
            // Sort by distance (placeholder - would use actual location)
            break
        case .date:
            result.sort { $0.createdAt > $1.createdAt }
        }
        
        return result
    }
    
    private func loadClaims() {
        isLoading = true
        
        Task {
            do {
                let response = try await APIService.shared.getClaims(
                    status: nil,
                    priority: nil,
                    assignedToMe: false
                )
                
                await MainActor.run {
                    claims = response.claims
                    isLoading = false
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isLoading = false
                }
            }
        }
    }
}

// MARK: - Claim Map View
struct ClaimMapView: View {
    let claims: [Claim]
    @Binding var selectedClaim: Claim?
    @Binding var isAvailableForJob: Bool
    
    // Kuwait coordinates as default
    @State private var cameraPosition: MapCameraPosition = .region(
        MKCoordinateRegion(
            center: CLLocationCoordinate2D(latitude: 29.3697, longitude: 47.9783),
            span: MKCoordinateSpan(latitudeDelta: 0.15, longitudeDelta: 0.15)
        )
    )
    
    var body: some View {
        ZStack(alignment: .top) {
            Map(position: $cameraPosition) {
                ForEach(claims) { claim in
                    if let lat = claim.latitude, let lon = claim.longitude {
                        Annotation(claim.claimNumber, coordinate: CLLocationCoordinate2D(latitude: lat, longitude: lon)) {
                            ClaimMapPin(claim: claim, isSelected: selectedClaim?.id == claim.id)
                                .onTapGesture {
                                    selectedClaim = claim
                                }
                        }
                    }
                }
            }
            .mapStyle(.standard)
            
            // Available for job toggle
            HStack {
                Toggle(isOn: $isAvailableForJob) {
                    HStack(spacing: 8) {
                        Circle()
                            .fill(isAvailableForJob ? Color.green : Color.gray)
                            .frame(width: 10, height: 10)
                        Text("Available for job")
                            .font(.subheadline.weight(.medium))
                            .foregroundStyle(.white)
                    }
                }
                .toggleStyle(.switch)
                .tint(.green)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
            .background(DeevoColors.surface.opacity(0.95))
            .cornerRadius(12)
            .padding(16)
        }
    }
}

// MARK: - Claim Map Pin
struct ClaimMapPin: View {
    let claim: Claim
    let isSelected: Bool
    
    var body: some View {
        VStack(spacing: 0) {
            ZStack {
                Circle()
                    .fill(statusColor)
                    .frame(width: isSelected ? 44 : 36, height: isSelected ? 44 : 36)
                    .shadow(color: statusColor.opacity(0.5), radius: isSelected ? 8 : 4)
                
                Image(systemName: "doc.text.fill")
                    .font(.system(size: isSelected ? 18 : 14))
                    .foregroundStyle(.white)
            }
            
            // Pin point
            Triangle()
                .fill(statusColor)
                .frame(width: 12, height: 8)
                .offset(y: -2)
        }
    }
    
    private var statusColor: Color {
        switch claim.status {
        case .new: return .orange
        case .assigned, .inProgress: return .blue
        case .pendingReview: return .purple
        case .approved, .closed: return .green
        case .rejected: return .red
        }
    }
}

// MARK: - Triangle Shape
struct Triangle: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        path.move(to: CGPoint(x: rect.midX, y: rect.maxY))
        path.addLine(to: CGPoint(x: rect.minX, y: rect.minY))
        path.addLine(to: CGPoint(x: rect.maxX, y: rect.minY))
        path.closeSubpath()
        return path
    }
}

// MARK: - Claim List Card
struct ClaimListCard: View {
    let claim: Claim
    let onAccept: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Status and claim number
            HStack {
                // Status badge
                Text(claim.status.displayName.uppercased())
                    .font(.caption.weight(.bold))
                    .foregroundStyle(statusColor)
                
                Text("·")
                    .foregroundStyle(DeevoColors.textTertiary)
                
                Text(claim.claimNumber)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.white)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundStyle(DeevoColors.textTertiary)
            }
            
            // Claim type and location
            VStack(alignment: .leading, spacing: 4) {
                Text(claim.claimType ?? "General Claim")
                    .font(.subheadline)
                    .foregroundStyle(DeevoColors.textSecondary)
                
                if let location = claim.location {
                    Text(location)
                        .font(.caption)
                        .foregroundStyle(DeevoColors.textTertiary)
                }
            }
            
            // Customer and evidence info
            HStack {
                Text(claim.customerName)
                    .font(.caption)
                    .foregroundStyle(DeevoColors.textSecondary)
                
                Spacer()
                
                // Photo count
                HStack(spacing: 4) {
                    Image(systemName: "camera.fill")
                        .font(.caption2)
                    Text("\(claim.evidenceCount) photos")
                        .font(.caption)
                }
                .foregroundStyle(DeevoColors.textTertiary)
                
                // Completion percentage
                Text("\(claim.completionPercentage)%")
                    .font(.caption.weight(.medium))
                    .foregroundStyle(DeevoColors.accent)
            }
        }
        .padding(16)
        .background(DeevoColors.surface)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(DeevoColors.border, lineWidth: 1)
        )
        .cornerRadius(12)
        .onTapGesture {
            onAccept()
        }
    }
    
    private var statusColor: Color {
        switch claim.status {
        case .new: return .orange
        case .assigned: return DeevoColors.accent
        case .inProgress: return .blue
        case .pendingReview: return .purple
        case .approved: return .green
        case .rejected: return .red
        case .closed: return DeevoColors.textTertiary
        }
    }
}

// MARK: - Assignment Accept Sheet (Livegenic-style slide to accept)
struct AssignmentAcceptSheet: View {
    let claim: Claim
    let onAccept: () -> Void
    
    @Environment(\.dismiss) private var dismiss
    @State private var dragOffset: CGFloat = 0
    private let maxSlide: CGFloat = 260
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                // Claim info card
                VStack(alignment: .leading, spacing: 16) {
                    HStack {
                        Text(claim.claimNumber)
                            .font(.title2.weight(.bold))
                            .foregroundStyle(.white)
                        
                        Spacer()
                        
                        Text(claim.status.displayName)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(.orange)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.orange.opacity(0.2))
                            .cornerRadius(4)
                    }
                    
                    // Customer contact
                    HStack(spacing: 12) {
                        Image(systemName: "person.circle.fill")
                            .font(.title)
                            .foregroundStyle(DeevoColors.textSecondary)
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text(claim.customerName)
                                .font(.headline)
                                .foregroundStyle(.white)
                            
                            if let phone = claim.customerPhone {
                                Text(phone)
                                    .font(.subheadline)
                                    .foregroundStyle(DeevoColors.textSecondary)
                            }
                        }
                        
                        Spacer()
                        
                        // Contact buttons
                        HStack(spacing: 12) {
                            Button(action: {}) {
                                Image(systemName: "phone.fill")
                                    .font(.title3)
                                    .foregroundStyle(.green)
                                    .padding(10)
                                    .background(Color.green.opacity(0.2))
                                    .clipShape(Circle())
                            }
                            
                            Button(action: {}) {
                                Image(systemName: "envelope.fill")
                                    .font(.title3)
                                    .foregroundStyle(.blue)
                                    .padding(10)
                                    .background(Color.blue.opacity(0.2))
                                    .clipShape(Circle())
                            }
                        }
                    }
                    
                    Divider()
                        .background(DeevoColors.border)
                    
                    // Location map preview
                    if let lat = claim.latitude, let lon = claim.longitude {
                        Map(initialPosition: .region(MKCoordinateRegion(
                            center: CLLocationCoordinate2D(latitude: lat, longitude: lon),
                            span: MKCoordinateSpan(latitudeDelta: 0.01, longitudeDelta: 0.01)
                        ))) {
                            Marker(claim.claimNumber, coordinate: CLLocationCoordinate2D(latitude: lat, longitude: lon))
                        }
                        .frame(height: 150)
                        .cornerRadius(8)
                        .disabled(true)
                    }
                }
                .padding(20)
                .background(DeevoColors.surface)
                .cornerRadius(16)
                
                Spacer()
                
                // Slide to accept
                SlideToAcceptView {
                    onAccept()
                }
                .padding(.bottom, 32)
            }
            .padding(20)
            .background(DeevoColors.backgroundDark)
            .navigationTitle("Accept Assignment")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                    .foregroundStyle(DeevoColors.textSecondary)
                }
            }
            .toolbarBackground(DeevoColors.primary, for: .navigationBar)
            .toolbarBackground(.visible, for: .navigationBar)
        }
    }
}

// MARK: - Slide to Accept View
struct SlideToAcceptView: View {
    let onAccepted: () -> Void
    
    @State private var dragOffset: CGFloat = 0
    private let maxSlide: CGFloat = 260
    
    var body: some View {
        GeometryReader { geometry in
            let trackWidth = geometry.size.width
            let actualMaxSlide = trackWidth - 60
            
            ZStack(alignment: .leading) {
                // Track
                RoundedRectangle(cornerRadius: 30)
                    .fill(DeevoColors.surface)
                    .overlay(
                        RoundedRectangle(cornerRadius: 30)
                            .stroke(DeevoColors.border, lineWidth: 1)
                    )
                
                // Label
                Text("Slide to Accept Assignment")
                    .font(.subheadline.weight(.medium))
                    .foregroundStyle(DeevoColors.textTertiary)
                    .frame(maxWidth: .infinity)
                    .opacity(1 - (dragOffset / actualMaxSlide))
                
                // Draggable circle
                Circle()
                    .fill(DeevoColors.accent)
                    .frame(width: 52, height: 52)
                    .overlay(
                        Image(systemName: "chevron.right.2")
                            .font(.title3.weight(.semibold))
                            .foregroundStyle(.white)
                    )
                    .offset(x: dragOffset + 4)
                    .gesture(
                        DragGesture()
                            .onChanged { value in
                                dragOffset = min(max(0, value.translation.width), actualMaxSlide)
                            }
                            .onEnded { value in
                                if dragOffset > actualMaxSlide * 0.8 {
                                    // Accept
                                    withAnimation(.spring(response: 0.3)) {
                                        dragOffset = actualMaxSlide
                                    }
                                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                                        onAccepted()
                                    }
                                } else {
                                    // Reset
                                    withAnimation(.spring(response: 0.3)) {
                                        dragOffset = 0
                                    }
                                }
                            }
                    )
            }
        }
        .frame(height: 60)
    }
}

#Preview {
    ClaimsListScreen()
        .environmentObject(AppState())
}
