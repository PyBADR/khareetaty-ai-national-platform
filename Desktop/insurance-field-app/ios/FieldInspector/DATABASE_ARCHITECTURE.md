# Database Architecture - FieldInspector

## Overview

FieldInspector uses GRDB 6.29.3 as the SQLite wrapper for local data persistence. The architecture follows an offline-first approach with a single `DatabaseQueue` instance managed by `DatabaseManager`.

## Database Configuration

### Single DatabaseQueue Pattern

```swift
@MainActor
final class DatabaseManager: Sendable {
    static let shared = DatabaseManager()
    private var dbQueue: DatabaseQueue?
    
    var database: DatabaseQueue {
        guard let db = dbQueue else {
            fatalError("Database not initialized. Call setup() first.")
        }
        return db
    }
}
```

**Key Points:**
- Single `DatabaseQueue` instance (not `DatabasePool`) for simplicity and safety
- `@MainActor` isolation ensures thread-safe access
- Foreign keys enabled via PRAGMA
- Database file: `Documents/DeevoSentinel.sqlite`

## Schema (4 Migrations)

### Migration v1_initial

| Table | Purpose | Key Indexes |
|-------|---------|-------------|
| `users` | User accounts | `users_tenant_email_unique` |
| `claims` | Insurance claims | `claims_status`, `claims_priority`, `claims_assignedToId` |
| `inspections` | Claim inspections | `inspections_claimId` |
| `inspection_fields` | Form field values | `inspection_fields_inspectionId`, `inspection_fields_unique` |
| `media_assets` | Photos, videos, audio | `media_assets_claimId`, `media_assets_syncStatus` |
| `sync_queue_items` | Legacy sync queue | `sync_queue_items_processedAt` |
| `audit_events` | Audit trail | `audit_events_claimId`, `audit_events_createdAt` |

### Migration v2_multi_tenancy

Adds `tenantId` column to: `users`, `claims`, `inspections`, `media_assets`

### Migration v3_sync_hardening

| Table | Purpose | Key Indexes |
|-------|---------|-------------|
| `idempotency_records` | Prevent duplicate operations | `idempotency_records_expiresAt` |
| `sync_conflicts` | Track field-level conflicts | `sync_conflicts_entityId`, `sync_conflicts_resolvedAt` |
| `claim_sync_status` | Per-claim sync state | (primary key only) |

### Migration v4_forms_engine (NEW)

| Table | Purpose | Key Indexes |
|-------|---------|-------------|
| `form_templates` | JSON form schemas | `form_templates_category`, `form_templates_isActive` |
| `form_drafts` | In-progress form data | `form_drafts_templateId`, `form_drafts_claimId`, `form_drafts_status`, `form_drafts_syncStatus` |
| `queued_operations` | Offline operation queue | `queued_operations_status`, `queued_operations_nextRetryAt`, `queued_operations_entityId` |

## Repository Layer

Views **MUST NOT** directly query GRDB. All data access goes through repositories:

### ClaimRepository
```swift
@MainActor
final class ClaimRepository {
    static let shared = ClaimRepository()
    
    func fetchAll(tenantId: String) async throws -> [Claim]
    func fetch(id: String) async throws -> Claim?
    func fetchByStatus(_ status: ClaimStatus, tenantId: String) async throws -> [Claim]
    func insert(_ claim: Claim) async throws
    func update(_ claim: Claim) async throws
    func delete(id: String) async throws
    func markSynced(id: String) async throws
    func search(query: String, tenantId: String) async throws -> [Claim]
}
```

### EvidenceRepository
```swift
@MainActor
final class EvidenceRepository {
    static let shared = EvidenceRepository()
    
    func fetchForClaim(claimId: String) async throws -> [MediaAsset]
    func fetchPendingSync() async throws -> [MediaAsset]
    func insert(_ asset: MediaAsset) async throws
    func markSynced(id: String, remoteUrl: String) async throws
    func markSyncFailed(id: String, error: String) async throws
}
```

### FormRepository
```swift
@MainActor
final class FormRepository {
    static let shared = FormRepository()
    
    // Templates
    func fetchAllTemplates() async throws -> [FormTemplate]
    func fetchTemplate(id: String) async throws -> FormTemplate?
    func saveTemplate(_ template: FormTemplate) async throws
    
    // Drafts
    func fetchAllDrafts() async throws -> [FormDraft]
    func fetchDrafts(claimId: String) async throws -> [FormDraft]
    func createDraft(templateId: String, claimId: String?) async throws -> FormDraft
    func updateDraftData(id: String, dataJson: String) async throws
    func markSubmitted(id: String) async throws
    func markSynced(id: String) async throws
}
```

### OperationRepository
```swift
@MainActor
final class OperationRepository {
    static let shared = OperationRepository()
    
    func enqueue(_ operation: QueuedOperation) async throws
    func fetchPending() async throws -> [QueuedOperation]
    func fetchReadyForRetry() async throws -> [QueuedOperation]
    func fetchFailed() async throws -> [QueuedOperation]
    func markProcessing(id: String) async throws
    func markCompleted(id: String) async throws
    func markFailed(id: String, error: String, nextRetryDelay: TimeInterval) async throws
    func resetForRetry(id: String) async throws
}
```

## Indexes for Hot Paths

### Sync Hot Paths
- `queued_operations_status` - Filter pending/failed operations
- `queued_operations_nextRetryAt` - Find operations ready for retry
- `media_assets_syncStatus` - Find assets needing upload
- `form_drafts_syncStatus` - Find drafts needing submission

### Query Hot Paths
- `claims_status` - Dashboard filtering
- `claims_assignedToId` - User's assigned claims
- `claims_tenantId` - Multi-tenant isolation
- `inspections_claimId` - Claim detail view
- `form_drafts_claimId` - Claim forms tab

## Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   SwiftUI   │────▶│  Repository  │────▶│ DatabaseManager │
│    Views    │     │    Layer     │     │  (DatabaseQueue)│
└─────────────┘     └──────────────┘     └─────────────────┘
       │                   │                      │
       │                   │                      ▼
       │                   │              ┌───────────────┐
       │                   │              │    SQLite     │
       │                   │              │   Database    │
       │                   │              └───────────────┘
       │                   │
       ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│              OperationProcessor (Serial)                 │
│  - Processes queued_operations                          │
│  - Exponential backoff on failure                       │
│  - Idempotency via idempotencyKey                       │
└─────────────────────────────────────────────────────────┘
```

## Offline-First Principles

1. **Write Local First**: All mutations write to local DB immediately
2. **Queue for Sync**: Operations enqueued in `queued_operations`
3. **Idempotent Operations**: Each operation has unique `idempotencyKey`
4. **Retry with Backoff**: Failed operations retry with exponential backoff
5. **Conflict Detection**: Server conflicts stored in `sync_conflicts`

## Migration Strategy

- Migrations are **append-only** - never modify existing migrations
- Each migration has a unique identifier (e.g., `v4_forms_engine`)
- GRDB's `DatabaseMigrator` handles version tracking
- Migrations run automatically on app launch via `DatabaseManager.setup()`

## Thread Safety

- `DatabaseManager` is `@MainActor` isolated
- All repository methods are `async` and run on MainActor
- GRDB's `DatabaseQueue` serializes all database access
- No direct database access from background threads

## Testing Considerations

- Use in-memory database for unit tests
- `DatabaseManager.clearAllData()` for test cleanup
- Repository layer enables easy mocking for view tests
