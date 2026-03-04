import SwiftUI

struct InspectionFormView: View {
    let inspection: Inspection
    
    @State private var template: InspectionTemplate?
    @State private var fields: [InspectionField] = []
    @State private var fieldValues: [String: String] = [:]
    @State private var isLoading = false
    @State private var isSaving = false
    @State private var currentSectionIndex = 0
    @State private var showCompleteAlert = false
    
    var body: some View {
        VStack(spacing: 0) {
            if isLoading {
                ProgressView("Loading form...")
            } else if let template = template {
                // Section tabs
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(Array(template.sections.enumerated()), id: \.element.key) { index, section in
                            SectionTabButton(
                                title: section.title,
                                isSelected: currentSectionIndex == index,
                                isComplete: isSectionComplete(section)
                            ) {
                                currentSectionIndex = index
                            }
                        }
                    }
                    .padding()
                }
                .background(Color(.systemGray6))
                
                Divider()
                
                // Form content
                TabView(selection: $currentSectionIndex) {
                    ForEach(Array(template.sections.enumerated()), id: \.element.key) { index, section in
                        SectionFormView(
                            section: section,
                            fieldValues: $fieldValues,
                            onFieldChanged: { key, value in
                                saveField(sectionKey: section.key, fieldKey: key, value: value)
                            }
                        )
                        .tag(index)
                    }
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
                
                // Bottom bar
                HStack {
                    if currentSectionIndex > 0 {
                        Button(action: { currentSectionIndex -= 1 }) {
                            Label("Previous", systemImage: "chevron.left")
                        }
                    }
                    
                    Spacer()
                    
                    if isSaving {
                        ProgressView()
                            .scaleEffect(0.8)
                        Text("Saving...")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    if currentSectionIndex < template.sections.count - 1 {
                        Button(action: { currentSectionIndex += 1 }) {
                            Label("Next", systemImage: "chevron.right")
                        }
                    } else {
                        Button("Complete Inspection") {
                            showCompleteAlert = true
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(!isFormComplete)
                    }
                }
                .padding()
                .background(Color(.systemBackground))
            }
        }
        .navigationTitle("Inspection Form")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            loadInspection()
        }
        .alert("Complete Inspection", isPresented: $showCompleteAlert) {
            Button("Cancel", role: .cancel) {}
            Button("Complete") {
                completeInspection()
            }
        } message: {
            Text("Are you sure you want to mark this inspection as complete? This action cannot be undone.")
        }
    }
    
    private var isFormComplete: Bool {
        guard let template = template else { return false }
        for section in template.sections {
            for field in section.fields where field.required {
                let key = "\(section.key).\(field.key)"
                if fieldValues[key]?.isEmpty ?? true {
                    return false
                }
            }
        }
        return true
    }
    
    private func isSectionComplete(_ section: TemplateSection) -> Bool {
        for field in section.fields where field.required {
            let key = "\(section.key).\(field.key)"
            if fieldValues[key]?.isEmpty ?? true {
                return false
            }
        }
        return true
    }
    
    private func loadInspection() {
        isLoading = true
        Task {
            do {
                let response = try await APIService.shared.getInspection(id: inspection.id)
                await MainActor.run {
                    // Use default template if none returned
                    if let templateWrapper = response.template {
                        template = InspectionTemplate(
                            id: inspection.templateId,
                            name: templateWrapper.name,
                            description: templateWrapper.description,
                            version: templateWrapper.version,
                            claimType: templateWrapper.claimType,
                            sections: templateWrapper.sections,
                            isActive: true
                        )
                    } else {
                        template = InspectionTemplate.motorInspection
                    }
                    isLoading = false
                }
            } catch {
                await MainActor.run {
                    template = InspectionTemplate.motorInspection
                    isLoading = false
                }
            }
        }
    }
    
    private func saveField(sectionKey: String, fieldKey: String, value: String?) {
        isSaving = true
        Task {
            do {
                _ = try await APIService.shared.updateInspectionFields(
                    id: inspection.id,
                    fields: [FieldUpdate(sectionKey: sectionKey, fieldKey: fieldKey, value: value)]
                )
                await MainActor.run {
                    isSaving = false
                }
            } catch {
                await MainActor.run {
                    isSaving = false
                }
            }
        }
    }
    
    private func completeInspection() {
        Task {
            do {
                _ = try await APIService.shared.completeInspection(id: inspection.id)
            } catch {
                print("Error completing inspection: \(error)")
            }
        }
    }
}

// MARK: - Section Tab Button

struct SectionTabButton: View {
    let title: String
    let isSelected: Bool
    let isComplete: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 4) {
                if isComplete {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                }
                Text(title)
                    .fontWeight(isSelected ? .semibold : .regular)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(isSelected ? Color.blue : Color(.systemGray5))
            .foregroundColor(isSelected ? .white : .primary)
            .cornerRadius(20)
        }
    }
}

// MARK: - Section Form View

struct SectionFormView: View {
    let section: TemplateSection
    @Binding var fieldValues: [String: String]
    let onFieldChanged: (String, String?) -> Void
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                // Section header
                VStack(alignment: .leading, spacing: 4) {
                    Text(section.title)
                        .font(.title2)
                        .fontWeight(.bold)
                    if let description = section.description {
                        Text(description)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
                
                // Fields
                ForEach(section.fields.sorted(by: { $0.order < $1.order })) { field in
                    FormFieldView(
                        field: field,
                        value: Binding(
                            get: { fieldValues["\(section.key).\(field.key)"] ?? "" },
                            set: { newValue in
                                fieldValues["\(section.key).\(field.key)"] = newValue
                                onFieldChanged(field.key, newValue.isEmpty ? nil : newValue)
                            }
                        )
                    )
                }
            }
            .padding()
        }
    }
}

// MARK: - Form Field View

struct FormFieldView: View {
    let field: TemplateField
    @Binding var value: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(field.label)
                    .font(.subheadline)
                    .fontWeight(.medium)
                if field.required {
                    Text("*")
                        .foregroundColor(.red)
                }
            }
            
            switch field.type {
            case .text:
                if field.multiline ?? false {
                    TextEditor(text: $value)
                        .frame(minHeight: 100)
                        .padding(8)
                        .background(Color(.systemGray6))
                        .cornerRadius(8)
                } else {
                    TextField(field.placeholder ?? "", text: $value)
                        .textFieldStyle(.plain)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(8)
                }
                
            case .number:
                TextField(field.placeholder ?? "0", text: $value)
                    .textFieldStyle(.plain)
                    .keyboardType(.decimalPad)
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(8)
                
            case .dropdown:
                Picker(field.label, selection: $value) {
                    Text("Select...").tag("")
                    ForEach(field.options ?? [], id: \.self) { option in
                        Text(option).tag(option)
                    }
                }
                .pickerStyle(.menu)
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(8)
                
            case .toggle:
                Toggle(isOn: Binding(
                    get: { value == "true" },
                    set: { value = $0 ? "true" : "false" }
                )) {
                    EmptyView()
                }
                .toggleStyle(.switch)
                
            case .date:
                DatePicker(
                    "",
                    selection: Binding(
                        get: {
                            ISO8601DateFormatter().date(from: value) ?? Date()
                        },
                        set: {
                            value = ISO8601DateFormatter().string(from: $0)
                        }
                    ),
                    displayedComponents: .date
                )
                .datePickerStyle(.compact)
                
            case .signature:
                SignatureFieldView(value: $value)
                
            case .photo:
                PhotoFieldView(value: $value)
            }
        }
    }
}

// MARK: - Signature Field View

struct SignatureFieldView: View {
    @Binding var value: String
    @State private var showSignaturePad = false
    
    var body: some View {
        Button(action: { showSignaturePad = true }) {
            HStack {
                if value.isEmpty {
                    Image(systemName: "signature")
                    Text("Tap to sign")
                } else {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                    Text("Signature captured")
                }
                Spacer()
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(8)
        }
        .sheet(isPresented: $showSignaturePad) {
            SignaturePadView(onSave: { signature in
                value = signature
                showSignaturePad = false
            })
        }
    }
}

// MARK: - Photo Field View

struct PhotoFieldView: View {
    @Binding var value: String
    @State private var showCamera = false
    
    var body: some View {
        Button(action: { showCamera = true }) {
            HStack {
                if value.isEmpty {
                    Image(systemName: "camera")
                    Text("Tap to capture photo")
                } else {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                    Text("Photo captured")
                }
                Spacer()
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(8)
        }
        .sheet(isPresented: $showCamera) {
            CameraView(onCapture: { photoId in
                value = photoId
                showCamera = false
            })
        }
    }
}

// MARK: - Signature Pad View (Placeholder)

struct SignaturePadView: View {
    let onSave: (String) -> Void
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationStack {
            VStack {
                Text("Signature Pad")
                    .font(.headline)
                Text("Draw your signature below")
                    .foregroundColor(.secondary)
                
                Rectangle()
                    .fill(Color(.systemGray6))
                    .frame(height: 200)
                    .cornerRadius(12)
                    .overlay(
                        Text("Signature area")
                            .foregroundColor(.secondary)
                    )
                    .padding()
                
                Button("Save Signature") {
                    onSave(UUID().uuidString)
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()
            .navigationTitle("Signature")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }
}

// MARK: - Camera View (Placeholder)

struct CameraView: View {
    let onCapture: (String) -> Void
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationStack {
            VStack {
                Text("Camera")
                    .font(.headline)
                
                Rectangle()
                    .fill(Color.black)
                    .aspectRatio(4/3, contentMode: .fit)
                    .overlay(
                        Image(systemName: "camera.viewfinder")
                            .font(.system(size: 60))
                            .foregroundColor(.white.opacity(0.5))
                    )
                    .cornerRadius(12)
                    .padding()
                
                Button("Capture Photo") {
                    onCapture(UUID().uuidString)
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()
            .navigationTitle("Capture Photo")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }
}
