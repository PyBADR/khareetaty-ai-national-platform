# FieldInspector iPad App - Baseline Audit Report

**Date:** March 4, 2026  
**Auditor:** Staff iOS Engineer + Data/Platform Architect  
**Repo Path:** ~/Desktop/insurance-field-app/ios/FieldInspector/

---

## 1. Project Overview

### 1.1 Schemes & Targets

| Target | Type | Description |
|--------|------|-------------|
| FieldInspector | App | Main iPad application |
| AppLogger | Framework | Unified logging via os.Logger |
| Config | Framework | Configuration management (xcconfig) |
| PDFGenerator | Framework | PDF report generation |
| ToastManager | Framework | Toast notification UI |

**Bundle ID:** `com.fieldinsurance.FieldInspector`  
**Deployment Target:** iOS 17.0  
**Swift Version:** 5.9  
**Package Dependencies:** GRDB 6.29.3

### 1.2 Build Status (from warnings_before.txt)

**Previous State:** 20 issues (1 settings + 19 warnings)  
**Current State:** 0 warnings, 0 errors (per warnings_after.txt)

---

## 2. Database Architecture

### 2.1 Current Implementation

**Location:** `FieldInspector/Database/DatabaseManager.swift`  
**Database Type:** SQLite via GRDB  
**Database File:** `DeevoSentinel.sqlite` (Documents directory)  
**Access Pattern:** Singleton `DatabaseManager.shared` with `DatabaseQueue`

### 2.2 Current Tables (from migrations)

| Table | Purpose | Indexes |
|-------|---------|--------|
| `users` | User accounts | tenant_email_unique, tenantId |
| `claims` | Insurance claims | tenant_claimNumber_unique, status, priority, assignedToId, tenantId |
| `inspections` | Claim inspections | claimId, tenantId |
| `inspection_fields` | Form field values | inspectionId, unique(inspectionId, sectionKey, fieldKey) |
| `media_assets` | Photos/videos/docs | claimId, inspectionId, syncStatus, tenantId |
| `sync_queue_items` | Offline sync queue | processedAt |
| `audit_events` | Audit trail (hash chain) | claimId, createdAt |
| `idempotency_records` | Dedup sync operations | expiresAt |
| `sync_conflicts` | Conflict tracking | entityId, resolvedAt |
| `claim_sync_status` | Per-claim sync state | (primary key only) |

### 2.3 Migration Versions

1. **v1_initial** - Core schema (users, claims, inspections, inspection_fields, media_assets, sync_queue_items, audit_events)
2. **v2_multi_tenancy** - Added tenantId columns and indexes
3. **v3_sync_hardening** - Added idempotencyKey, nextRetryAt, idempotency_records, sync_conflicts, claim_sync_status

---

## 3. Services Graph

### 3.1 Current Services

```
┌─────────────────────────────────────────────────────────────┐
│                      FieldInspectorApp                       │
│                            │                                 │
│              ┌─────────────┼─────────────┐                   │
│              ▼             ▼             ▼                   │
│      DatabaseManager   SyncService   APIService              │
│      (singleton)       (singleton)   (actor)                 │
│              │             │             │                   │
│              └─────────────┼─────────────┘                   │
│                            │                                 │
│              ┌─────────────┼─────────────┐                   │
│              ▼             ▼             ▼                   │
│        PDFService   PerformanceManager  AppLogger            │
└─────────────────────────────────────────────────────────────┘
```

| Service | Type | Responsibility |
|---------|------|----------------|
| `DatabaseManager` | @MainActor singleton | GRDB database access, migrations |
| `SyncService` | @MainActor ObservableObject | Offline sync, conflict resolution, network monitoring |
| `APIService` | actor singleton | REST API communication, token refresh |
| `PDFService` | Service | PDF report generation |
| `PerformanceManager` | Service | Performance metrics, signposts |

### 3.2 Service Issues Identified

| Issue | Severity | Location |
|-------|----------|----------|
| No repository layer - Views/ViewModels query GRDB directly | HIGH | Throughout |
| DatabaseManager is @MainActor but database ops should be async | MEDIUM | DatabaseManager.swift |
| SyncService directly accesses DatabaseManager.database | MEDIUM | SyncService.swift |

---

## 4. Forms Implementation

### 4.1 Current State

**Location:** `FieldInspector/Views/Forms/`

| File | Description |
|------|-------------|
| `VehicleInspectionFormView.swift` | Hardcoded vehicle inspection form (583 lines) |
| `EquipmentInspectionFormView.swift` | Hardcoded equipment inspection form |
| `WorkOrderFormView.swift` | Hardcoded work order form |

### 4.2 Form Architecture Issues

| Issue | Severity | Description |
|-------|----------|-------------|
| **No JSON-driven forms** | CRITICAL | Forms are hardcoded SwiftUI views, not data-driven |
| **No FormSchema model** | CRITICAL | No Decodable schema for dynamic form rendering |
| **No TemplateLoader** | CRITICAL | No mechanism to load templates from bundle |
| **No FormDraft persistence** | HIGH | Form state not saved to database |
| **No form validation** | HIGH | No centralized validation before submit |
| **Submit not queued** | HIGH | Form submission bypasses offline queue |

### 4.3 Current Form Components

- `CapturedPhoto` - Photo capture model
- `CollapsibleSectionHeader` - Expandable section UI
- `FormPhotoRow` - Single photo capture row
- `FormPhotoGridRow` - Multi-photo grid
- `FormTextField` - Text input field
- `VoiceRecorderRow` - Voice memo capture
- `PhotoCaptureSheet` - Camera capture sheet

---

## 5. Sync Implementation

### 5.1 Current State

**Location:** `FieldInspector/Services/SyncService.swift` (622 lines)

### 5.2 Sync Features Present

| Feature | Status | Notes |
|---------|--------|-------|
| Network monitoring | ✅ | NWPathMonitor |
| Exponential backoff | ✅ | BackoffConfig with jitter |
| Sync queue (sync_queue_items) | ✅ | Basic queue implementation |
| Idempotency keys | ⚠️ | Model exists, not fully integrated |
| Conflict detection | ⚠️ | Model exists, resolution incomplete |
| Per-claim sync status | ✅ | ClaimSyncStatus model |
| Push/Pull sync | ✅ | Via APIService |

### 5.3 Sync Issues Identified

| Issue | Severity | Description |
|-------|----------|-------------|
| **SyncStatusScreen uses hardcoded data** | CRITICAL | Lines 62-69 show mock data, not queued_operations |
| **No retry action per failed op** | HIGH | UI shows failed status but no retry button |
| **Evidence capture not queued** | HIGH | Photos bypass offline queue |
| **Form submission not queued** | HIGH | Forms submit directly, not via queue |
| **Idempotency not enforced** | MEDIUM | Key generated but not checked before processing |
| **No OperationProcessor** | MEDIUM | No serial processor for queue items |

---

## 6. UI/UX Audit

### 6.1 Current State

**Design System:** `FieldInspector/DesignSystem/`
- `Colors.swift` - DeevoColors theme
- `Typography.swift` - Font styles
- `Components/` - Reusable UI components

### 6.2 UI Issues Identified

| Issue | Severity | Description |
|-------|----------|-------------|
| **No unified error presentation** | HIGH | Errors handled inconsistently across views |
| **No offline banner** | HIGH | No persistent indicator when offline |
| **SyncStatusScreen mock data** | HIGH | Hardcoded rows instead of real queue |
| **MainActor compliance** | MEDIUM | Some async state mutations may race |

---

## 7. Critical Blockers

### 7.1 CRITICAL (Must Fix)

| # | Issue | File(s) | Fix Approach | Acceptance Criteria |
|---|-------|---------|--------------|--------------------|
| C1 | Forms are hardcoded, not JSON-driven | Views/Forms/*.swift | Implement FormSchema, TemplateLoader, FormRendererView | Add new template = add JSON file only |
| C2 | SyncStatusScreen shows mock data | Views/Sync/SyncStatusScreen.swift | Query queued_operations table | Screen reflects actual queue state |
| C3 | No FormDraft persistence | - | Add form_drafts table, FormDraftStore | Drafts survive app restart |
| C4 | Form submission bypasses queue | Views/Forms/*.swift | Enqueue SubmitForm operation | Offline submit works |

### 7.2 HIGH (Should Fix)

| # | Issue | File(s) | Fix Approach | Acceptance Criteria |
|---|-------|---------|--------------|--------------------|
| H1 | No repository layer | Database/, ViewModels/ | Create ClaimRepository, EvidenceRepository, FormRepository, OperationRepository | Views never import GRDB |
| H2 | Evidence capture not queued | ViewModels/EvidenceViewModel.swift | Enqueue media upload operations | Offline photo capture queued |
| H3 | No retry action per failed op | Views/Sync/SyncStatusScreen.swift | Add retry button, call retryOperation() | User can retry individual ops |
| H4 | No unified error presentation | Throughout | Create ErrorBanner component | Single error UI pattern |
| H5 | No offline banner | - | Create OfflineBanner based on SyncService.isOnline | Persistent offline indicator |
| H6 | Idempotency not enforced | Services/SyncService.swift | Check idempotency_records before processing | Duplicate ops rejected |

### 7.3 MEDIUM (Nice to Fix)

| # | Issue | File(s) | Fix Approach | Acceptance Criteria |
|---|-------|---------|--------------|--------------------|
| M1 | DatabaseManager @MainActor | Database/DatabaseManager.swift | Remove @MainActor, use async methods | DB ops don't block main thread |
| M2 | No OperationProcessor | Services/ | Create serial queue processor | Ops processed in order |
| M3 | Missing form_templates table | Database/DatabaseManager.swift | Add migration v4 | Templates cached locally |

### 7.4 LOW (Optional)

| # | Issue | File(s) | Fix Approach | Acceptance Criteria |
|---|-------|---------|--------------|--------------------|
| L1 | Claim model has policyNumber not in DB | Models/Claim.swift | Add column or remove property | Model matches schema |
| L2 | Some indexes may be redundant | DatabaseManager.swift | Audit index usage | Only necessary indexes |

---

## 8. Missing Tables (Required)

| Table | Purpose | Status |
|-------|---------|--------|
| `claims` | Insurance claims | ✅ Exists |
| `evidence` (media_assets) | Photos/videos | ✅ Exists (as media_assets) |
| `form_templates` | JSON form schemas | ❌ Missing |
| `form_drafts` | Autosaved form state | ❌ Missing |
| `queued_operations` | Offline operation queue | ⚠️ Exists as sync_queue_items |
| `audit_events` | Audit trail | ✅ Exists |

---

## 9. Recommendations Summary

### Phase 1: Data Infrastructure
1. Create repository layer (ClaimRepository, EvidenceRepository, FormRepository, OperationRepository)
2. Add form_templates and form_drafts tables
3. Rename/alias sync_queue_items to queued_operations for clarity
4. Add missing indexes for form queries

### Phase 2: Offline Queue
1. Implement OperationProcessor for serial processing
2. Integrate evidence capture through queue
3. Integrate form submission through queue
4. Update SyncStatusScreen to use real queue data
5. Add retry action per failed operation

### Phase 3: JSON Forms Engine
1. Define FormSchema (Decodable)
2. Implement TemplateLoader from bundle
3. Implement FormRendererView (dynamic)
4. Implement FormDraft autosave
5. Create 2 sample JSON templates

### Phase 4: UI/UX Consistency
1. Create unified ErrorBanner component
2. Create OfflineBanner component
3. Ensure MainActor compliance throughout

### Phase 5: Release & CI
1. Verify GitHub Actions workflow
2. Create ARCHIVE_CHECKLIST.md
3. Verify privacy manifest

---

## 10. Files Reviewed

- `FieldInspector/Database/DatabaseManager.swift` (324 lines)
- `FieldInspector/Services/SyncService.swift` (622 lines)
- `FieldInspector/Services/APIService.swift` (696 lines)
- `FieldInspector/Services/PDFService.swift`
- `FieldInspector/Services/PerformanceManager.swift`
- `FieldInspector/Models/Claim.swift` (234 lines)
- `FieldInspector/Models/SyncModels.swift` (179 lines)
- `FieldInspector/Models/MediaAsset.swift` (131 lines)
- `FieldInspector/Models/Inspection.swift` (127 lines)
- `FieldInspector/Models/AuditEvent.swift` (162 lines)
- `FieldInspector/Views/Forms/VehicleInspectionFormView.swift` (583 lines)
- `FieldInspector/Views/Sync/SyncStatusScreen.swift` (177 lines)
- `FieldInspector/FieldInspectorApp.swift` (110 lines)
- `warnings_before.txt` (41 lines)
- `warnings_after.txt` (53 lines)
- `RELEASE_REPORT.md` (156 lines)

---

**End of Baseline Report**
