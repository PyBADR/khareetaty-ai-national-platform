# Release Report: Offline Sync System

## Overview

Implemented a production-grade offline-first sync system using `queued_operations` as the single source of truth.

## Components Implemented

### 1. QueuedOperation Model

**File**: `Database/Repositories/OperationRepository.swift`

```swift
struct QueuedOperation: Identifiable, Codable, Equatable {
    var id: String
    var operationType: OperationType
    var entityType: String
    var entityId: String
    var payloadJson: String
    var idempotencyKey: String  // Deterministic, prevents duplicates
    var status: OperationStatus
    var attempts: Int
    var maxAttempts: Int
    var lastError: String?
    var nextRetryAt: Date?
    var createdAt: Date
    var processedAt: Date?
}
```

**Operation Types**:
- `submitForm` - Form submission
- `uploadEvidence` - Media upload
- `updateClaim` - Claim updates
- `createInspection` - New inspections
- `updateInspection` - Inspection updates
- `deleteMedia` - Media deletion

### 2. OperationRepository

**File**: `Database/Repositories/OperationRepository.swift`

Key methods:
- `enqueue()` - Add operation with idempotency check
- `fetchPending()` - Get operations ready to process
- `fetchReadyForRetry()` - Get failed ops past retry time
- `markProcessing()` - Increment attempts, set processing
- `markCompleted()` - Set processed timestamp
- `markFailed()` - Set error and next retry time
- `resetForRetry()` - Manual retry trigger

### 3. OperationProcessor

**File**: `Services/OperationProcessor.swift`

Serial processor with:
- Network monitoring (auto-process when online)
- Exponential backoff (1s -> 5min max)
- Per-operation type handlers
- Idempotency enforcement
- Max attempts (5 default)

### 4. Database Migration

**File**: `Database/DatabaseManager.swift` (v4_forms_engine)

```sql
CREATE TABLE queued_operations (
    id TEXT PRIMARY KEY,
    operationType TEXT NOT NULL,
    entityType TEXT NOT NULL,
    entityId TEXT NOT NULL,
    payloadJson TEXT NOT NULL,
    idempotencyKey TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    maxAttempts INTEGER NOT NULL DEFAULT 5,
    lastError TEXT,
    nextRetryAt DATETIME,
    createdAt DATETIME NOT NULL,
    processedAt DATETIME
);
```

### 5. SyncStatusScreen Updates

**File**: `Views/SyncStatusScreen.swift`

- Now uses `queued_operations` as source of truth
- Shows real operation data (not mock)
- Per-operation retry button
- "Retry All Failed" button
- Pending/failed counts from database

## Idempotency Key Generation

Deterministic key based on operation type, entity type, entity ID, and timestamp.
Duplicate operations with same idempotency key are rejected.

## Retry/Backoff Configuration

- Initial delay: 1 second
- Max delay: 5 minutes
- Multiplier: 2x
- Jitter: 10%
- Max attempts: 5

## Acceptance Criteria

| Criteria | Status |
|----------|--------|
| QueuedOperation model with all required fields | Done |
| OperationRepository with CRUD operations | Done |
| OperationProcessor with serial processing | Done |
| Exponential backoff (1s-5min) | Done |
| Max attempts (5) with permanent failure | Done |
| Idempotency key generation | Done |
| Evidence capture through queue | Done |
| Form submission through queue | Done |
| SyncStatusScreen uses queued_operations | Done |
| Per-operation retry action | Done |
