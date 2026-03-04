# Release Report: JSON Forms Engine

## Overview

Implemented a JSON-driven forms engine that allows adding new form templates without code changes.

## Components Implemented

### 1. FormSchema (Decodable)

**File**: `Services/FormEngine/FormSchema.swift`

```swift
struct FormSchema: Codable, Equatable {
    let id: String
    let name: String
    let version: String
    let category: String
    let description: String?
    let sections: [FormSection]
    let submitButtonText: String?
    let validationRules: [FormValidationRule]?
}

struct FormSection: Codable, Equatable, Identifiable {
    let id: String
    let title: String
    let description: String?
    let icon: String?
    let isCollapsible: Bool
    let isInitiallyExpanded: Bool
    let fields: [FormField]
}

struct FormField: Codable, Equatable, Identifiable {
    let id: String
    let type: FormFieldType
    let label: String
    let placeholder: String?
    let helpText: String?
    let isRequired: Bool
    let defaultValue: AnyCodableValue?
    let validation: FieldValidation?
    let options: [FieldOption]?  // For select, radio, checkbox
    let config: FieldConfig?
}
```

**Supported Field Types**:
- `text`, `textarea`, `number`, `email`, `phone`
- `date`, `time`, `datetime`
- `select`, `radio`, `checkbox`, `toggle`
- `slider`, `counter`, `rating`
- `photo`, `photo_grid`
- `signature`, `location`, `voice_note`
- `hidden`

### 2. TemplateLoader

**File**: `Services/FormEngine/TemplateLoader.swift`

```swift
@MainActor
final class TemplateLoader {
    static let shared = TemplateLoader()
    
    func loadBundleTemplates() async throws -> [FormSchema]
    func loadTemplate(id: String) async throws -> FormSchema
    func reloadTemplates() async throws -> [FormSchema]
}
```

Loads templates from `Forms/Templates/*.json` in the app bundle.

### 3. FormRendererView

**File**: `Views/Forms/FormRendererView.swift`

Dynamic SwiftUI view that renders any FormSchema:
- Sections with collapsible headers
- All field types rendered appropriately
- Validation with field-level errors
- Autosave every 5 seconds
- Submit confirmation dialog
- Offline-first submission via queue

### 4. FormDraft Table/Store

**File**: `Database/Repositories/FormRepository.swift`

```swift
struct FormDraft: Identifiable, Codable, Equatable {
    var id: String
    var templateId: String
    var claimId: String?
    var inspectionId: String?
    var dataJson: String
    var status: FormDraftStatus  // draft, submitted, synced, failed
    var lastSavedAt: Date
    var createdAt: Date
    var updatedAt: Date
    var syncStatus: SyncStatus
}
```

**Database Table** (v4_forms_engine migration):
```sql
CREATE TABLE form_drafts (
    id TEXT PRIMARY KEY,
    templateId TEXT NOT NULL REFERENCES form_templates,
    claimId TEXT REFERENCES claims,
    inspectionId TEXT REFERENCES inspections,
    dataJson TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'draft',
    lastSavedAt DATETIME NOT NULL,
    createdAt DATETIME NOT NULL,
    updatedAt DATETIME NOT NULL,
    syncStatus TEXT NOT NULL DEFAULT 'pending'
);
```

### 5. Submit via Queue

Form submission flow:
1. Validate all fields
2. Show confirmation dialog
3. Save final draft state
4. Mark draft as `submitted`
5. Create `QueuedOperation` with type `submitForm`
6. Enqueue operation
7. Trigger `OperationProcessor.processQueue()`
8. Dismiss form view

## Sample Templates

### 1. Vehicle Inspection (`vehicle_inspection.json`)

**Location**: `Resources/Forms/Templates/vehicle_inspection.json`

**Sections**:
- Vehicle Condition (photo, slider, photo_grid, location, counter)
- Usage Information (photo, select)
- Driver Information (photo, text fields)

### 2. Property Damage Assessment (`property_damage.json`)

**Location**: `Resources/Forms/Templates/property_damage.json`

**Sections**:
- Property Details (select, text, location, photo_grid)
- Damage Assessment (select, rating, photo_grid, textarea, number)
- Affected Areas (multiple toggles)
- Inspector Notes (textarea, toggle)

## Adding a New Template (No Code Change Required)

### Step 1: Create JSON File

Create `Resources/Forms/Templates/my_new_form.json`:

```json
{
  "id": "my_new_form",
  "name": "My New Form",
  "version": "1.0",
  "category": "custom",
  "sections": [
    {
      "id": "section1",
      "title": "Section Title",
      "icon": "star.fill",
      "isCollapsible": true,
      "isInitiallyExpanded": true,
      "fields": [
        {
          "id": "field1",
          "type": "text",
          "label": "Field Label",
          "isRequired": true
        }
      ]
    }
  ],
  "submitButtonText": "Submit"
}
```

### Step 2: Add to Xcode Project

1. Drag JSON file into `Resources/Forms/Templates` group
2. Ensure "Copy items if needed" is checked
3. Ensure target membership includes FieldInspector

### Step 3: Done!

The template will be automatically loaded on app launch and available for use.

## Validation

### Field-Level Validation

```json
{
  "id": "email_field",
  "type": "email",
  "label": "Email",
  "isRequired": true,
  "validation": {
    "pattern": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$",
    "patternMessage": "Please enter a valid email address"
  }
}
```

### Supported Validation Rules

| Rule | Field Types | Description |
|------|-------------|-------------|
| `minLength` | text, textarea | Minimum character count |
| `maxLength` | text, textarea | Maximum character count |
| `minValue` | number, slider | Minimum numeric value |
| `maxValue` | number, slider | Maximum numeric value |
| `pattern` | text, email, phone | Regex pattern |
| `patternMessage` | text, email, phone | Custom error message |
| `minPhotos` | photo, photo_grid | Minimum photos required |
| `maxPhotos` | photo, photo_grid | Maximum photos allowed |

## Acceptance Criteria

| Criteria | Status |
|----------|--------|
| FormSchema Decodable model | Done |
| TemplateLoader from bundle | Done |
| FormRendererView (dynamic) | Done |
| FormDraft table with autosave | Done |
| Validation on submit | Done |
| Submit via queued operation | Done |
| 2 sample JSON templates | Done |
| No code change for new template | Done |
