import SwiftUI
import CoreLocation
import AVFoundation

// MARK: - Vehicle Inspection Form View (ION Reference)
/// Matches ION's Vehicle Pre-Check Inspection form exactly

struct VehicleInspectionFormView: View {
    let claimId: String
    
    // MARK: - State
    @State private var vehiclePhotos: [CapturedPhoto] = []
    @State private var conditionScore: Double = 50
    @State private var damagePhotos: [CapturedPhoto] = []
    @State private var location: CLLocationCoordinate2D?
    @State private var locationError: String?
    @State private var issueCount: Int = 0
    @State private var voiceRecordingURL: URL?
    @State private var isRecordingVoice: Bool = false
    
    // Usage Information Section
    @State private var usageExpanded: Bool = true
    @State private var odometerPhotos: [CapturedPhoto] = []
    @State private var fuelConditions: String = ""
    
    // Driver Information Section
    @State private var driverExpanded: Bool = false
    @State private var driverLicensePhotos: [CapturedPhoto] = []
    @State private var driverName: String = ""
    @State private var licenseNumber: String = ""
    @State private var driverPhone: String = ""
    
    // Submission
    @State private var isSubmitting: Bool = false
    @State private var showSubmitAlert: Bool = false
    
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        List {
            // SECTION 1: Vehicle Condition
            vehicleConditionSection
            
            // SECTION 2: Usage Information (collapsible)
            usageInformationSection
            
            // SECTION 3: Driver Information (collapsible)
            driverInformationSection
        }
        .listStyle(.insetGrouped)
        .navigationTitle("Vehicle Pre-Check Inspection")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button("Send") {
                    showSubmitAlert = true
                }
                .buttonStyle(.borderedProminent)
                .tint(DeevoColors.accent)
                .disabled(isSubmitting)
            }
        }
        .alert("Submit Inspection", isPresented: $showSubmitAlert) {
            Button("Cancel", role: .cancel) {}
            Button("Submit") {
                Task { await submit() }
            }
        } message: {
            Text("Are you sure you want to submit this vehicle inspection?")
        }
        .onAppear {
            requestLocation()
        }
    }
    
    // MARK: - Vehicle Condition Section
    
    private var vehicleConditionSection: some View {
        Section {
            CollapsibleSectionHeader(
                title: "Vehicle Inspection",
                icon: "car.fill",
                isExpanded: .constant(true)
            )
            
            // Picture of Vehicle
            FormPhotoRow(
                title: "Picture of Vehicle",
                photos: $vehiclePhotos,
                maxPhotos: 1,
                label: "Front View"
            )
            
            // Overall Condition Slider
            VStack(alignment: .leading, spacing: 8) {
                Text("Overall Condition of Vehicle")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                
                HStack {
                    Text("Poor")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    
                    Slider(value: $conditionScore, in: 0...100, step: 1)
                        .tint(conditionColor)
                    
                    Text(conditionLabel)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                
                // Condition indicator bar
                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        RoundedRectangle(cornerRadius: 4)
                            .fill(Color(.systemGray5))
                            .frame(height: 8)
                        
                        RoundedRectangle(cornerRadius: 4)
                            .fill(conditionColor)
                            .frame(width: geo.size.width * (conditionScore / 100), height: 8)
                    }
                }
                .frame(height: 8)
            }
            .padding(.vertical, 4)
            
            // Areas of Concern — 4-photo grid
            FormPhotoGridRow(
                title: "Areas of Concern on Vehicle",
                photos: $damagePhotos,
                maxPhotos: 8,
                columns: 4
            )
            
            // Location
            VStack(alignment: .leading, spacing: 4) {
                Text("Location of Vehicle")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                
                if let coord = location {
                    HStack {
                        Image(systemName: "location.fill")
                            .foregroundStyle(.green)
                        Text(String(format: "%.4f, %.4f", coord.latitude, coord.longitude))
                            .font(.caption)
                            .foregroundStyle(.green)
                    }
                } else {
                    Label(
                        locationError ?? "Failed to acquire a GPS location fix",
                        systemImage: "exclamationmark.triangle"
                    )
                    .font(.caption)
                    .foregroundStyle(.orange)
                }
            }
            .padding(.vertical, 4)
            
            // Issue Counter
            HStack {
                Text("Number of Issues Found")
                    .font(.subheadline)
                Spacer()
                
                Button {
                    if issueCount > 0 { issueCount -= 1 }
                } label: {
                    Image(systemName: "minus.circle.fill")
                        .font(.title2)
                        .foregroundStyle(issueCount > 0 ? DeevoColors.accent : .gray)
                }
                .buttonStyle(.plain)
                
                Text("\(issueCount)")
                    .font(.title3.monospacedDigit())
                    .frame(minWidth: 40)
                
                Button {
                    issueCount += 1
                } label: {
                    Image(systemName: "plus.circle.fill")
                        .font(.title2)
                        .foregroundStyle(DeevoColors.accent)
                }
                .buttonStyle(.plain)
            }
            .padding(.vertical, 4)
            
            // Voice Message
            VoiceRecorderRow(
                title: "Voice Message for Inspection Audit Team",
                recordingURL: $voiceRecordingURL,
                isRecording: $isRecordingVoice
            )
        }
    }
    
    // MARK: - Usage Information Section
    
    private var usageInformationSection: some View {
        Section {
            CollapsibleSectionHeader(
                title: "Usage Information",
                icon: "gauge.high",
                isExpanded: $usageExpanded
            )
            
            if usageExpanded {
                // Odometer photo
                FormPhotoRow(
                    title: "Photo of Odometer",
                    photos: $odometerPhotos,
                    maxPhotos: 1,
                    label: "Odometer"
                )
                
                // Fuel Conditions
                VStack(alignment: .leading, spacing: 4) {
                    Text("Fuel Conditions")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                    
                    TextField("Enter fuel conditions...", text: $fuelConditions)
                        .textFieldStyle(.plain)
                        .padding(12)
                        .background(Color(.systemGray6))
                        .cornerRadius(8)
                }
            }
        }
    }
    
    // MARK: - Driver Information Section
    
    private var driverInformationSection: some View {
        Section {
            CollapsibleSectionHeader(
                title: "Driver Information",
                icon: "person.fill",
                isExpanded: $driverExpanded
            )
            
            if driverExpanded {
                FormPhotoRow(
                    title: "Driver License",
                    photos: $driverLicensePhotos,
                    maxPhotos: 1,
                    label: "Driver License"
                )
                
                FormTextField(title: "Driver Name", text: $driverName)
                FormTextField(title: "License Number", text: $licenseNumber)
                FormTextField(title: "Phone", text: $driverPhone, keyboardType: .phonePad)
            }
        }
    }
    
    // MARK: - Helpers
    
    private var conditionColor: Color {
        switch conditionScore {
        case 0..<30:  return .red
        case 30..<60: return .orange
        case 60..<80: return .yellow
        default:      return .green
        }
    }
    
    private var conditionLabel: String {
        switch conditionScore {
        case 0..<30:  return "Poor"
        case 30..<60: return "Fair"
        case 60..<80: return "Good"
        default:      return "Satisfactory"
        }
    }
    
    private func requestLocation() {
        // TODO: Implement CLLocationManager
        // For now, simulate location acquisition
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            // Simulate Kuwait location
            location = CLLocationCoordinate2D(latitude: 29.3697, longitude: 47.9783)
        }
    }
    
    private func submit() async {
        isSubmitting = true
        
        // TODO: Submit to API
        // let request = VehicleInspectionRequest(...)
        // try await APIService.shared.submitVehicleInspection(claimId: claimId, request: request)
        
        try? await Task.sleep(nanoseconds: 1_000_000_000)
        
        await MainActor.run {
            isSubmitting = false
            dismiss()
        }
    }
}

// MARK: - Supporting Views

struct CapturedPhoto: Identifiable {
    let id = UUID()
    var image: UIImage?
    var localPath: String?
    var label: String?
    var uploadStatus: UploadStatus = .pending
    
    enum UploadStatus {
        case pending, uploading, uploaded, failed
    }
}

struct CollapsibleSectionHeader: View {
    let title: String
    let icon: String
    @Binding var isExpanded: Bool
    
    var body: some View {
        Button {
            withAnimation(.easeInOut(duration: 0.2)) {
                isExpanded.toggle()
            }
        } label: {
            HStack {
                Image(systemName: icon)
                    .foregroundStyle(DeevoColors.accent)
                Text(title)
                    .font(.headline)
                    .foregroundStyle(.primary)
                Spacer()
                Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                    .foregroundStyle(.secondary)
                    .font(.caption)
            }
        }
        .buttonStyle(.plain)
    }
}

struct FormPhotoRow: View {
    let title: String
    @Binding var photos: [CapturedPhoto]
    let maxPhotos: Int
    let label: String
    
    @State private var showCamera = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.subheadline)
                .foregroundStyle(.secondary)
            
            HStack(spacing: 12) {
                // Show existing photos
                ForEach(photos) { photo in
                    if let image = photo.image {
                        Image(uiImage: image)
                            .resizable()
                            .scaledToFill()
                            .frame(width: 80, height: 60)
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color(.systemGray4), lineWidth: 1)
                            )
                    }
                }
                
                // Add photo button
                if photos.count < maxPhotos {
                    Button {
                        showCamera = true
                    } label: {
                        VStack(spacing: 4) {
                            Image(systemName: "plus")
                                .font(.title2)
                            Text("Add photo")
                                .font(.caption2)
                        }
                        .frame(width: 80, height: 60)
                        .background(Color(.systemGray6))
                        .foregroundStyle(.secondary)
                        .cornerRadius(8)
                    }
                }
            }
        }
        .sheet(isPresented: $showCamera) {
            PhotoCaptureSheet(label: label) { image in
                let photo = CapturedPhoto(image: image, label: label)
                photos.append(photo)
            }
        }
    }
}

struct FormPhotoGridRow: View {
    let title: String
    @Binding var photos: [CapturedPhoto]
    let maxPhotos: Int
    let columns: Int
    
    @State private var showCamera = false
    
    private var gridColumns: [GridItem] {
        Array(repeating: GridItem(.flexible(), spacing: 8), count: columns)
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.subheadline)
                .foregroundStyle(.secondary)
            
            LazyVGrid(columns: gridColumns, spacing: 8) {
                ForEach(photos) { photo in
                    if let image = photo.image {
                        Image(uiImage: image)
                            .resizable()
                            .scaledToFill()
                            .frame(height: 60)
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                    }
                }
                
                if photos.count < maxPhotos {
                    Button {
                        showCamera = true
                    } label: {
                        VStack {
                            Image(systemName: "camera")
                            Text("Tap to choose photo")
                                .font(.caption2)
                        }
                        .frame(height: 60)
                        .frame(maxWidth: .infinity)
                        .background(Color(.systemGray6))
                        .foregroundStyle(.secondary)
                        .cornerRadius(8)
                    }
                }
            }
        }
        .sheet(isPresented: $showCamera) {
            PhotoCaptureSheet(label: "Damage") { image in
                let photo = CapturedPhoto(image: image, label: "Damage")
                photos.append(photo)
            }
        }
    }
}

struct FormTextField: View {
    let title: String
    @Binding var text: String
    var keyboardType: UIKeyboardType = .default
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.subheadline)
                .foregroundStyle(.secondary)
            
            TextField("Enter \(title.lowercased())...", text: $text)
                .textFieldStyle(.plain)
                .keyboardType(keyboardType)
                .padding(12)
                .background(Color(.systemGray6))
                .cornerRadius(8)
        }
    }
}

struct VoiceRecorderRow: View {
    let title: String
    @Binding var recordingURL: URL?
    @Binding var isRecording: Bool
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.subheadline)
                .foregroundStyle(.secondary)
            
            Button {
                // TODO: Implement AVAudioRecorder
                isRecording.toggle()
            } label: {
                HStack {
                    Image(systemName: isRecording ? "stop.circle.fill" : "mic.fill")
                        .foregroundStyle(isRecording ? .red : DeevoColors.accent)
                    Text(isRecording ? "Recording... tap to stop" : "Tap to record voice message")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(12)
                .background(Color(.systemGray6))
                .cornerRadius(8)
            }
            .buttonStyle(.plain)
            
            if recordingURL != nil {
                HStack {
                    Image(systemName: "waveform")
                        .foregroundStyle(.green)
                    Text("Voice message recorded")
                        .font(.caption)
                        .foregroundStyle(.green)
                    Spacer()
                    Button("Play") {
                        // TODO: Play recording
                    }
                    .font(.caption)
                }
            }
        }
    }
}

struct PhotoCaptureSheet: View {
    let label: String
    let onCapture: (UIImage) -> Void
    
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Text("Capture \(label)")
                    .font(.headline)
                
                Rectangle()
                    .fill(Color.black)
                    .aspectRatio(4/3, contentMode: .fit)
                    .overlay(
                        Image(systemName: "camera.viewfinder")
                            .font(.system(size: 60))
                            .foregroundStyle(.white.opacity(0.5))
                    )
                    .cornerRadius(12)
                    .padding()
                
                Button("Capture Photo") {
                    // TODO: Implement actual camera capture
                    // For now, create a placeholder image
                    let renderer = UIGraphicsImageRenderer(size: CGSize(width: 400, height: 300))
                    let image = renderer.image { ctx in
                        UIColor.systemGray5.setFill()
                        ctx.fill(CGRect(x: 0, y: 0, width: 400, height: 300))
                    }
                    onCapture(image)
                    dismiss()
                }
                .buttonStyle(.borderedProminent)
                .tint(DeevoColors.accent)
            }
            .padding()
            .navigationTitle("Camera")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }
}

#Preview {
    NavigationStack {
        VehicleInspectionFormView(claimId: "test-claim-id")
    }
}
