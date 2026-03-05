import SwiftUI

struct TemplatesView: View {
    @State private var templates: [InspectionTemplate] = []
    @State private var isLoading = false
    @State private var selectedTemplate: InspectionTemplate?
    
    var body: some View {
        VStack {
            if isLoading {
                ProgressView("Loading templates...")
            } else if templates.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "doc.text")
                        .font(.system(size: 60))
                        .foregroundColor(.secondary)
                    Text("No templates available")
                        .font(.headline)
                }
            } else {
                List {
                    ForEach(templates) { template in
                        TemplateRow(template: template)
                            .onTapGesture {
                                selectedTemplate = template
                            }
                    }
                }
                .listStyle(.insetGrouped)
            }
        }
        .navigationTitle("Inspection Templates")
        .sheet(item: $selectedTemplate) { template in
            TemplateDetailView(template: template)
        }
        .onAppear {
            loadTemplates()
        }
    }
    
    private func loadTemplates() {
        isLoading = true
        
        // For now, use the default template
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            templates = [InspectionTemplate.motorInspection]
            isLoading = false
        }
    }
}

// MARK: - Template Row

struct TemplateRow: View {
    let template: InspectionTemplate
    
    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: "doc.text.fill")
                .font(.title2)
                .foregroundColor(.blue)
                .frame(width: 44, height: 44)
                .background(Color.blue.opacity(0.1))
                .cornerRadius(10)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(template.name)
                    .font(.headline)
                
                if let description = template.description {
                    Text(description)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                }
                
                HStack {
                    Label(template.claimType.capitalized, systemImage: "tag")
                    Text("•")
                    Label("v\(template.version)", systemImage: "number")
                    Text("•")
                    Label("\(template.sections.count) sections", systemImage: "list.bullet")
                }
                .font(.caption)
                .foregroundColor(.secondary)
            }
            
            Spacer()
            
            Image(systemName: "chevron.right")
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 8)
    }
}

// MARK: - Template Detail View

struct TemplateDetailView: View {
    let template: InspectionTemplate
    
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationStack {
            List {
                Section("Overview") {
                    LabeledContent("Name", value: template.name)
                    LabeledContent("Version", value: template.version)
                    LabeledContent("Claim Type", value: template.claimType.capitalized)
                    if let description = template.description {
                        Text(description)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
                
                ForEach(template.sections) { section in
                    Section(section.title) {
                        if let description = section.description {
                            Text(description)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        
                        ForEach(section.fields) { field in
                            HStack {
                                VStack(alignment: .leading, spacing: 2) {
                                    HStack {
                                        Text(field.label)
                                            .font(.subheadline)
                                        if field.required {
                                            Text("*")
                                                .foregroundColor(.red)
                                        }
                                    }
                                    Text(field.type.rawValue.capitalized)
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                                
                                Spacer()
                                
                                Image(systemName: iconForFieldType(field.type))
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                }
            }
            .navigationTitle(template.name)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") { dismiss() }
                }
            }
        }
    }
    
    private func iconForFieldType(_ type: FieldValueType) -> String {
        switch type {
        case .text: return "textformat"
        case .number: return "number"
        case .dropdown: return "chevron.down.circle"
        case .toggle: return "switch.2"
        case .date: return "calendar"
        case .signature: return "signature"
        case .photo: return "camera"
        }
    }
}

#Preview {
    NavigationStack {
        TemplatesView()
    }
}
