import SwiftUI

struct AuditLogTab: View {
    let claimId: String
    
    @State private var auditEvents: [AuditEventDisplay] = []
    @State private var isLoading = false
    
    var body: some View {
        VStack {
            if isLoading {
                ProgressView("Loading audit log...")
            } else if auditEvents.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "clock.arrow.circlepath")
                        .font(.system(size: 60))
                        .foregroundColor(.secondary)
                    Text("No audit events")
                        .font(.headline)
                    Text("Actions taken on this claim will appear here.")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
            } else {
                List {
                    ForEach(auditEvents) { event in
                        AuditEventRow(event: event)
                    }
                }
                .listStyle(.plain)
            }
        }
        .onAppear {
            loadAuditEvents()
        }
    }
    
    private func loadAuditEvents() {
        // In a real app, this would fetch from the API
        // For now, we'll show sample data
        isLoading = true
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            auditEvents = [
                AuditEventDisplay(
                    id: UUID().uuidString,
                    eventType: "claim.created",
                    actorName: "System",
                    description: "Claim was created",
                    timestamp: Date().addingTimeInterval(-86400 * 3),
                    isVerified: true
                ),
                AuditEventDisplay(
                    id: UUID().uuidString,
                    eventType: "claim.assigned",
                    actorName: "Admin User",
                    description: "Claim assigned to John Smith",
                    timestamp: Date().addingTimeInterval(-86400 * 2),
                    isVerified: true
                ),
                AuditEventDisplay(
                    id: UUID().uuidString,
                    eventType: "claim.accepted",
                    actorName: "John Smith",
                    description: "Claim accepted by inspector",
                    timestamp: Date().addingTimeInterval(-86400),
                    isVerified: true
                ),
                AuditEventDisplay(
                    id: UUID().uuidString,
                    eventType: "inspection.started",
                    actorName: "John Smith",
                    description: "Inspection started using Motor Vehicle template",
                    timestamp: Date().addingTimeInterval(-43200),
                    isVerified: true
                ),
                AuditEventDisplay(
                    id: UUID().uuidString,
                    eventType: "media.uploaded",
                    actorName: "John Smith",
                    description: "3 photos uploaded",
                    timestamp: Date().addingTimeInterval(-21600),
                    isVerified: true
                ),
            ]
            isLoading = false
        }
    }
}

// MARK: - Audit Event Display Model

struct AuditEventDisplay: Identifiable {
    let id: String
    let eventType: String
    let actorName: String
    let description: String
    let timestamp: Date
    let isVerified: Bool
}

// MARK: - Audit Event Row

struct AuditEventRow: View {
    let event: AuditEventDisplay
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            // Icon
            Image(systemName: iconForEventType(event.eventType))
                .font(.title3)
                .foregroundColor(colorForEventType(event.eventType))
                .frame(width: 32)
            
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(event.description)
                        .font(.subheadline)
                        .fontWeight(.medium)
                    
                    Spacer()
                    
                    if event.isVerified {
                        Image(systemName: "checkmark.shield.fill")
                            .foregroundColor(.green)
                            .font(.caption)
                    }
                }
                
                HStack {
                    Text(event.actorName)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Text("•")
                        .foregroundColor(.secondary)
                    
                    Text(event.timestamp.formatted(date: .abbreviated, time: .shortened))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(.vertical, 8)
    }
    
    private func iconForEventType(_ type: String) -> String {
        switch type {
        case "claim.created": return "plus.circle.fill"
        case "claim.assigned": return "person.badge.plus"
        case "claim.accepted": return "checkmark.circle.fill"
        case "claim.status_changed": return "arrow.triangle.2.circlepath"
        case "inspection.started": return "checklist"
        case "inspection.completed": return "checkmark.seal.fill"
        case "media.uploaded": return "photo.fill"
        case "ai.suggestion_requested": return "brain"
        case "ai.suggestion_received": return "sparkles"
        case "report.generated": return "doc.richtext"
        default: return "circle.fill"
        }
    }
    
    private func colorForEventType(_ type: String) -> Color {
        switch type {
        case "claim.created": return .blue
        case "claim.assigned": return .orange
        case "claim.accepted": return .green
        case "claim.status_changed": return .purple
        case "inspection.started": return .yellow
        case "inspection.completed": return .green
        case "media.uploaded": return .cyan
        case "ai.suggestion_requested", "ai.suggestion_received": return .pink
        case "report.generated": return .indigo
        default: return .gray
        }
    }
}

#Preview {
    AuditLogTab(claimId: "test-claim-id")
}
