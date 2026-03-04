// DispatchMapView.swift
// Dispatch Map with claim pins and bottom list
// DEEVO Field Inspector

import SwiftUI
import MapKit

struct DispatchMapView: View {
    @State private var cameraPosition: MapCameraPosition = .region(
        MKCoordinateRegion(
            center: CLLocationCoordinate2D(latitude: 29.3759, longitude: 47.9774), // Kuwait
            span: MKCoordinateSpan(latitudeDelta: 0.5, longitudeDelta: 0.5)
        )
    )
    @State private var selectedClaim: SampleClaim?
    @State private var showClaimDetail = false
    
    // Sample claims for demo
    private let sampleClaims: [SampleClaim] = [
        SampleClaim(id: "CLM-001", title: "Motor Accident - Al Farwaniyah", status: "In Progress", latitude: 29.2785, longitude: 47.9591, claimant: "Ahmed Al-Rashidi"),
        SampleClaim(id: "CLM-002", title: "Property Damage - Salmiya", status: "Pending", latitude: 29.3347, longitude: 48.0765, claimant: "Fatima Al-Ali"),
        SampleClaim(id: "CLM-003", title: "Theft Claim - Kuwait City", status: "Review", latitude: 29.3759, longitude: 47.9774, claimant: "Omar Al-Mahmoud"),
        SampleClaim(id: "CLM-004", title: "Fire Damage - Hawalli", status: "Urgent", latitude: 29.3328, longitude: 48.0286, claimant: "Sara Al-Hassan"),
        SampleClaim(id: "CLM-005", title: "Water Damage - Jabriya", status: "In Progress", latitude: 29.3167, longitude: 48.0333, claimant: "Khalid Al-Mutairi")
    ]
    
    var body: some View {
        GeometryReader { geometry in
            VStack(spacing: 0) {
                // Map view (top 60%)
                Map(position: $cameraPosition) {
                    ForEach(sampleClaims) { claim in
                        Annotation(claim.id, coordinate: claim.coordinate) {
                            ClaimMapPin(claim: claim, isSelected: selectedClaim?.id == claim.id)
                                .onTapGesture {
                                    withAnimation(.easeInOut(duration: 0.2)) {
                                        selectedClaim = claim
                                    }
                                }
                        }
                    }
                }
                .mapStyle(.standard)
                .frame(height: geometry.size.height * 0.55)
                
                // Divider
                Rectangle()
                    .fill(DeevoColors.border)
                    .frame(height: 1)
                
                // Claims list (bottom 45%)
                VStack(spacing: 0) {
                    // Header
                    HStack {
                        Text("Nearby Claims")
                            .font(.headline)
                            .foregroundStyle(.white)
                        Spacer()
                        Text("\(sampleClaims.count) claims")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 12)
                    .background(DeevoColors.surface)
                    
                    // Claims list
                    ScrollView {
                        LazyVStack(spacing: 1) {
                            ForEach(sampleClaims) { claim in
                                ClaimListRow(claim: claim, isSelected: selectedClaim?.id == claim.id)
                                    .onTapGesture {
                                        selectedClaim = claim
                                        showClaimDetail = true
                                    }
                            }
                        }
                    }
                }
                .background(DeevoColors.backgroundDark)
            }
        }
        .navigationTitle("Dispatch Map")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showClaimDetail) {
            if let claim = selectedClaim {
                ClaimDetailSheet(claim: claim)
            }
        }
    }
}

// MARK: - Supporting Types

struct SampleClaim: Identifiable {
    let id: String
    let title: String
    let status: String
    let latitude: Double
    let longitude: Double
    let claimant: String
    
    var coordinate: CLLocationCoordinate2D {
        CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    }
    
    var statusColor: Color {
        switch status {
        case "Urgent": return DeevoColors.error
        case "In Progress": return DeevoColors.info
        case "Pending": return DeevoColors.accent
        case "Review": return DeevoColors.warning
        default: return DeevoColors.textSecondary
        }
    }
}

struct ClaimMapPin: View {
    let claim: SampleClaim
    let isSelected: Bool
    
    var body: some View {
        VStack(spacing: 0) {
            ZStack {
                Circle()
                    .fill(claim.statusColor)
                    .frame(width: isSelected ? 44 : 32, height: isSelected ? 44 : 32)
                    .shadow(color: claim.statusColor.opacity(0.5), radius: isSelected ? 8 : 4)
                
                Image(systemName: "car.fill")
                    .font(isSelected ? .body : .caption)
                    .foregroundStyle(.white)
            }
            
            // Pin tail
            Triangle()
                .fill(claim.statusColor)
                .frame(width: 12, height: 8)
                .offset(y: -2)
        }
        .animation(.easeInOut(duration: 0.2), value: isSelected)
    }
}

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

struct ClaimListRow: View {
    let claim: SampleClaim
    let isSelected: Bool
    
    var body: some View {
        HStack(spacing: 12) {
            // Status indicator
            Circle()
                .fill(claim.statusColor)
                .frame(width: 10, height: 10)
            
            // Claim info
            VStack(alignment: .leading, spacing: 4) {
                Text(claim.title)
                    .font(.subheadline.weight(.medium))
                    .foregroundStyle(.white)
                    .lineLimit(1)
                
                HStack(spacing: 8) {
                    Text(claim.id)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    
                    Text("•")
                        .foregroundStyle(.secondary)
                    
                    Text(claim.claimant)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            
            Spacer()
            
            // Status badge
            Text(claim.status)
                .font(.caption.weight(.medium))
                .foregroundStyle(claim.statusColor)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(claim.statusColor.opacity(0.15))
                .cornerRadius(6)
            
            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundStyle(.tertiary)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(isSelected ? DeevoColors.surface : DeevoColors.surfaceElevated)
    }
}

struct ClaimDetailSheet: View {
    let claim: SampleClaim
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                // Claim header
                VStack(spacing: 8) {
                    Text(claim.id)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    
                    Text(claim.title)
                        .font(.title2.weight(.semibold))
                        .foregroundStyle(.white)
                        .multilineTextAlignment(.center)
                    
                    Text(claim.status)
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(claim.statusColor)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(claim.statusColor.opacity(0.15))
                        .cornerRadius(8)
                }
                .padding(.top, 20)
                
                // Claimant info
                VStack(alignment: .leading, spacing: 12) {
                    Label(claim.claimant, systemImage: "person.fill")
                        .foregroundStyle(.white)
                    
                    Label("\(claim.latitude, specifier: "%.4f"), \(claim.longitude, specifier: "%.4f")", systemImage: "location.fill")
                        .foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(16)
                .background(DeevoColors.surface)
                .cornerRadius(12)
                .padding(.horizontal, 20)
                
                Spacer()
                
                // Action buttons
                VStack(spacing: 12) {
                    Button {
                        dismiss()
                    } label: {
                        Label("Open Full Claim", systemImage: "doc.text.fill")
                            .font(.headline)
                            .foregroundStyle(.black)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(DeevoColors.accent)
                            .cornerRadius(12)
                    }
                    
                    Button {
                        dismiss()
                    } label: {
                        Label("Get Directions", systemImage: "arrow.triangle.turn.up.right.diamond.fill")
                            .font(.headline)
                            .foregroundStyle(DeevoColors.accent)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(DeevoColors.accent.opacity(0.15))
                            .cornerRadius(12)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 20)
            }
            .background(DeevoColors.backgroundDark)
            .navigationTitle("Claim Details")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                    .foregroundStyle(DeevoColors.accent)
                }
            }
        }
    }
}

#Preview {
    NavigationStack {
        DispatchMapView()
    }
}
