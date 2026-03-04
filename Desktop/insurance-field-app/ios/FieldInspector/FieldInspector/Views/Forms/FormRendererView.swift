import SwiftUI
import CoreLocation

/// Dynamic form renderer that renders forms from JSON schema
struct FormRendererView: View {
    let schema: FormSchema
    let claimId: String?
    let draftId: String?
    
    @StateObject private var viewModel: FormRendererViewModel
    @Environment(\.dismiss) private var dismiss
    
    init(schema: FormSchema, claimId: String? = nil, draftId: String? = nil) {
        self.schema = schema
        self.claimId = claimId
        self.draftId = draftId
        self._viewModel = StateObject(wrappedValue: FormRendererViewModel(
            schema: schema,
            claimId: claimId,
            draftId: draftId
        ))
    }
    
    var body: some View {
        List {
            ForEach(schema.sections) { section in
                FormSectionView(
                    section: section,
                    values: $viewModel.values,
                    errors: viewModel.fieldErrors
                )
            }
        }
        .listStyle(.insetGrouped)
        .navigationTitle(schema.name)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button(schema.submitButtonText ?? "Submit") {
                    Task { await viewModel.submit() }
                }
                .buttonStyle(.borderedProminent)
                .tint(DeevoColors.accent)
                .disabled(viewModel.isSubmitting)
            }
        }
        .alert("Submit Form", isPresented: $viewModel.showSubmitConfirmation) {
            Button("Cancel", role: .cancel) {}
            Button("Submit") {
                Task { await viewModel.confirmSubmit() }
            }
        } message: {
            Text("Are you sure you want to submit this form?")
        }
        .alert("Error", isPresented: $viewModel.showError) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(viewModel.errorMessage ?? "An error occurred")
        }
        .onChange(of: viewModel.isSubmitted) { _, submitted in
            if submitted {
                dismiss()
            }
        }
        .task {
            await viewModel.loadDraft()
        }
    }
}

// MARK: - Form Section View

struct FormSectionView: View {
    let section: FormSection
    @Binding var values: [String: AnyCodableValue]
    let errors: [String: String]
    
    @State private var isExpanded: Bool
    
    init(section: FormSection, values: Binding<[String: AnyCodableValue]>, errors: [String: String]) {
        self.section = section
        self._values = values
        self.errors = errors
        self._isExpanded = State(initialValue: section.isInitiallyExpanded)
    }
    
    var body: some View {
        Section {
            if section.isCollapsible {
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        isExpanded.toggle()
                    }
                } label: {
                    HStack {
                        if let icon = section.icon {
                            Image(systemName: icon)
                                .foregroundStyle(DeevoColors.accent)
                        }
                        Text(section.title)
                            .font(.headline)
                            .foregroundStyle(.primary)
                        Spacer()
                        Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                            .foregroundStyle(.secondary)
                            .font(.caption)
                    }
                }
                .buttonStyle(.plain)
            } else {
                HStack {
                    if let icon = section.icon {
                        Image(systemName: icon)
                            .foregroundStyle(DeevoColors.accent)
                    }
                    Text(section.title)
                        .font(.headline)
                }
            }
            
            if isExpanded || !section.isCollapsible {
                ForEach(section.fields) { field in
                    FormFieldView(
                        field: field,
                        value: binding(for: field.id),
                        error: errors[field.id]
                    )
                }
            }
        } footer: {
            if let description = section.description, isExpanded {
                Text(description)
            }
        }
    }
    
    private func binding(for fieldId: String) -> Binding<AnyCodableValue> {
        Binding(
            get: { values[fieldId] ?? AnyCodableValue("") },
            set: { values[fieldId] = $0 }
        )
    }
}

// MARK: - Form Field View

struct FormFieldView: View {
    let field: FormField
    @Binding var value: AnyCodableValue
    let error: String?
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            // Label
            HStack {
                Text(field.label)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                if field.isRequired {
                    Text("*")
                        .foregroundStyle(.red)
                }
            }
            
            // Field input based on type
            fieldInput
            
            // Help text
            if let helpText = field.helpText {
                Text(helpText)
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }
            
            // Error message
            if let error = error {
                Text(error)
                    .font(.caption)
                    .foregroundStyle(.red)
            }
        }
        .padding(.vertical, 4)
    }
    
    @ViewBuilder
    private var fieldInput: some View {
        switch field.type {
        case .text, .email, .phone:
            textField
        case .textArea:
            textAreaField
        case .number:
            numberField
        case .date:
            dateField
        case .select:
            selectField
        case .toggle:
            toggleField
        case .slider:
            sliderField
        case .counter:
            counterField
        case .photo:
            photoField
        case .photoGrid:
            photoGridField
        case .location:
            locationField
        case .rating:
            ratingField
        default:
            Text("Unsupported field type: \(field.type.rawValue)")
                .foregroundStyle(.secondary)
        }
    }
    
    // MARK: - Field Implementations
    
    private var textField: some View {
        TextField(
            field.placeholder ?? "Enter \(field.label.lowercased())...",
            text: stringBinding
        )
        .textFieldStyle(.plain)
        .keyboardType(keyboardType)
        .padding(12)
        .background(Color(.systemGray6))
        .cornerRadius(8)
    }
    
    private var textAreaField: some View {
        TextEditor(text: stringBinding)
            .frame(minHeight: 100)
            .padding(8)
            .background(Color(.systemGray6))
            .cornerRadius(8)
    }
    
    private var numberField: some View {
        TextField(
            field.placeholder ?? "0",
            text: stringBinding
        )
        .textFieldStyle(.plain)
        .keyboardType(.decimalPad)
        .padding(12)
        .background(Color(.systemGray6))
        .cornerRadius(8)
    }
    
    private var dateField: some View {
        DatePicker(
            "",
            selection: dateBinding,
            displayedComponents: .date
        )
        .labelsHidden()
    }
    
    private var selectField: some View {
        Picker("", selection: stringBinding) {
            Text("Select...").tag("")
            ForEach(field.options ?? []) { option in
                Text(option.label).tag(option.value)
            }
        }
        .pickerStyle(.menu)
    }
    
    private var toggleField: some View {
        Toggle("", isOn: boolBinding)
            .labelsHidden()
            .tint(DeevoColors.accent)
    }
    
    private var sliderField: some View {
        let config = field.config
        let minVal = config?.sliderMin ?? 0
        let maxVal = config?.sliderMax ?? 100
        let step = config?.sliderStep ?? 1
        
        return VStack {
            HStack {
                if let labels = config?.sliderLabels, labels.count >= 1 {
                    Text(labels[0]).font(.caption).foregroundStyle(.secondary)
                }
                Slider(
                    value: doubleBinding,
                    in: minVal...maxVal,
                    step: step
                )
                .tint(DeevoColors.accent)
                if let labels = config?.sliderLabels, labels.count >= 2 {
                    Text(labels[1]).font(.caption).foregroundStyle(.secondary)
                }
            }
            Text(String(format: "%.0f", doubleBinding.wrappedValue))
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }
    
    private var counterField: some View {
        let config = field.config
        let minVal = config?.counterMin ?? 0
        let maxVal = config?.counterMax ?? 999
        
        return HStack {
            Spacer()
            Button {
                let current = intBinding.wrappedValue
                if current > minVal {
                    intBinding.wrappedValue = current - 1
                }
            } label: {
                Image(systemName: "minus.circle.fill")
                    .font(.title2)
                    .foregroundStyle(intBinding.wrappedValue > minVal ? DeevoColors.accent : .gray)
            }
            .buttonStyle(.plain)
            
            Text("\(intBinding.wrappedValue)")
                .font(.title3.monospacedDigit())
                .frame(minWidth: 40)
            
            Button {
                let current = intBinding.wrappedValue
                if current < maxVal {
                    intBinding.wrappedValue = current + 1
                }
            } label: {
                Image(systemName: "plus.circle.fill")
                    .font(.title2)
                    .foregroundStyle(DeevoColors.accent)
            }
            .buttonStyle(.plain)
        }
    }
    
    private var photoField: some View {
        // Simplified photo field - would integrate with camera
        Button {
            // TODO: Open camera
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
    
    private var photoGridField: some View {
        let columns = field.config?.photoColumns ?? 4
        let gridColumns = Array(repeating: GridItem(.flexible(), spacing: 8), count: columns)
        
        return LazyVGrid(columns: gridColumns, spacing: 8) {
            Button {
                // TODO: Open camera
            } label: {
                VStack {
                    Image(systemName: "camera")
                    Text("Tap to add")
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
    
    private var locationField: some View {
        HStack {
            Image(systemName: "location.fill")
                .foregroundStyle(stringBinding.wrappedValue.isEmpty ? .orange : .green)
            Text(stringBinding.wrappedValue.isEmpty ? "Acquiring location..." : stringBinding.wrappedValue)
                .font(.caption)
                .foregroundStyle(stringBinding.wrappedValue.isEmpty ? .orange : .green)
        }
    }
    
    private var ratingField: some View {
        let maxRating = field.config?.ratingMax ?? 5
        let icon = field.config?.ratingIcon ?? "star.fill"
        
        return HStack {
            ForEach(1...maxRating, id: \.self) { rating in
                Button {
                    intBinding.wrappedValue = rating
                } label: {
                    Image(systemName: icon)
                        .foregroundStyle(rating <= intBinding.wrappedValue ? DeevoColors.accent : .gray)
                }
                .buttonStyle(.plain)
            }
        }
    }
    
    // MARK: - Bindings
    
    private var stringBinding: Binding<String> {
        Binding(
            get: { value.stringValue ?? "" },
            set: { value = AnyCodableValue($0) }
        )
    }
    
    private var intBinding: Binding<Int> {
        Binding(
            get: { value.intValue ?? 0 },
            set: { value = AnyCodableValue($0) }
        )
    }
    
    private var doubleBinding: Binding<Double> {
        Binding(
            get: { value.doubleValue ?? 0 },
            set: { value = AnyCodableValue($0) }
        )
    }
    
    private var boolBinding: Binding<Bool> {
        Binding(
            get: { value.boolValue ?? false },
            set: { value = AnyCodableValue($0) }
        )
    }
    
    private var dateBinding: Binding<Date> {
        Binding(
            get: {
                if let str = value.stringValue {
                    return ISO8601DateFormatter().date(from: str) ?? Date()
                }
                return Date()
            },
            set: {
                value = AnyCodableValue(ISO8601DateFormatter().string(from: $0))
            }
        )
    }
    
    private var keyboardType: UIKeyboardType {
        switch field.type {
        case .email: return .emailAddress
        case .phone: return .phonePad
        case .number: return .decimalPad
        default: return .default
        }
    }
}

// MARK: - View Model

@MainActor
class FormRendererViewModel: ObservableObject {
    let schema: FormSchema
    let claimId: String?
    let draftId: String?
    
    @Published var values: [String: AnyCodableValue] = [:]
    @Published var fieldErrors: [String: String] = [:]
    @Published var isSubmitting = false
    @Published var isSubmitted = false
    @Published var showSubmitConfirmation = false
    @Published var showError = false
    @Published var errorMessage: String?
    
    private let formRepository = FormRepository.shared
    private let operationRepository = OperationRepository.shared
    private var autosaveTask: Task<Void, Never>?
    private var currentDraftId: String?
    
    init(schema: FormSchema, claimId: String?, draftId: String?) {
        self.schema = schema
        self.claimId = claimId
        self.draftId = draftId
        self.currentDraftId = draftId
        
        // Initialize with default values
        initializeDefaults()
    }
    
    private func initializeDefaults() {
        for section in schema.sections {
            for field in section.fields {
                if let defaultValue = field.defaultValue {
                    values[field.id] = defaultValue
                }
            }
        }
    }
    
    func loadDraft() async {
        // Create or load draft
        if let draftId = currentDraftId {
            do {
                if let draft = try await formRepository.fetchDraft(id: draftId) {
                    if let data = draft.dataJson.data(using: .utf8) {
                        let decoded = try JSONDecoder().decode([String: AnyCodableValue].self, from: data)
                        values = decoded
                    }
                }
            } catch {
                AppLogger.error("Failed to load draft", error: error, category: AppLogger.sync)
            }
        } else {
            // Create new draft
            do {
                let draft = try await formRepository.createDraft(
                    templateId: schema.id,
                    claimId: claimId
                )
                currentDraftId = draft.id
            } catch {
                AppLogger.error("Failed to create draft", error: error, category: AppLogger.sync)
            }
        }
        
        // Start autosave
        startAutosave()
    }
    
    private func startAutosave() {
        autosaveTask?.cancel()
        autosaveTask = Task {
            while !Task.isCancelled {
                try? await Task.sleep(nanoseconds: 5_000_000_000) // 5 seconds
                guard !Task.isCancelled else { break }
                await saveDraft()
            }
        }
    }
    
    private func saveDraft() async {
        guard let draftId = currentDraftId else { return }
        
        do {
            let encoder = JSONEncoder()
            let data = try encoder.encode(values)
            let json = String(data: data, encoding: .utf8) ?? "{}"
            try await formRepository.updateDraftData(id: draftId, dataJson: json)
        } catch {
            AppLogger.error("Failed to save draft", error: error, category: AppLogger.sync)
        }
    }
    
    func submit() async {
        // Validate
        if !validate() {
            return
        }
        
        showSubmitConfirmation = true
    }
    
    func confirmSubmit() async {
        guard let draftId = currentDraftId else {
            errorMessage = "No draft to submit"
            showError = true
            return
        }
        
        isSubmitting = true
        
        do {
            // Save final draft state
            await saveDraft()
            
            // Mark draft as submitted
            try await formRepository.markSubmitted(id: draftId)
            
            // Create payload
            let encoder = JSONEncoder()
            let dataJson = String(data: try encoder.encode(values), encoding: .utf8) ?? "{}"
            
            let payload = FormSubmissionPayload(
                draftId: draftId,
                templateId: schema.id,
                claimId: claimId,
                inspectionId: nil,
                dataJson: dataJson
            )
            
            let payloadData = try encoder.encode(payload)
            let payloadJson = String(data: payloadData, encoding: .utf8) ?? "{}"
            
            // Enqueue operation
            let operation = QueuedOperation(
                operationType: .submitForm,
                entityType: "form_draft",
                entityId: draftId,
                payloadJson: payloadJson
            )
            
            try await operationRepository.enqueue(operation)
            
            // Trigger processing
            await OperationProcessor.shared.processQueue()
            
            isSubmitted = true
            
        } catch {
            errorMessage = error.localizedDescription
            showError = true
            AppLogger.error("Failed to submit form", error: error, category: AppLogger.sync)
        }
        
        isSubmitting = false
    }
    
    private func validate() -> Bool {
        fieldErrors.removeAll()
        var isValid = true
        
        for section in schema.sections {
            for field in section.fields {
                if let error = validateField(field) {
                    fieldErrors[field.id] = error
                    isValid = false
                }
            }
        }
        
        return isValid
    }
    
    private func validateField(_ field: FormField) -> String? {
        let value = values[field.id]
        
        // Required check
        if field.isRequired {
            if value == nil || (value?.stringValue?.isEmpty ?? true) {
                return "\(field.label) is required"
            }
        }
        
        // Type-specific validation
        if let validation = field.validation {
            if let str = value?.stringValue {
                if let minLen = validation.minLength, str.count < minLen {
                    return "Minimum \(minLen) characters required"
                }
                if let maxLen = validation.maxLength, str.count > maxLen {
                    return "Maximum \(maxLen) characters allowed"
                }
                if let pattern = validation.pattern {
                    let regex = try? NSRegularExpression(pattern: pattern)
                    let range = NSRange(str.startIndex..., in: str)
                    if regex?.firstMatch(in: str, range: range) == nil {
                        return validation.patternMessage ?? "Invalid format"
                    }
                }
            }
            
            if let num = value?.doubleValue {
                if let minVal = validation.minValue, num < minVal {
                    return "Minimum value is \(minVal)"
                }
                if let maxVal = validation.maxValue, num > maxVal {
                    return "Maximum value is \(maxVal)"
                }
            }
        }
        
        return nil
    }
    
    deinit {
        autosaveTask?.cancel()
    }
}
