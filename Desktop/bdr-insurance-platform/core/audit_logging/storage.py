"""
Audit Storage

Extracted from: insurance-hf-project/create_gradio_space.py
Purpose: Storage backends for audit log entries
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from abc import ABC, abstractmethod
import json
from pathlib import Path


class AuditStorage(ABC):
    """Abstract base class for audit storage backends"""
    
    @abstractmethod
    def store(self, entry: 'AuditEntry') -> None:
        """Store an audit entry"""
        pass
    
    @abstractmethod
    def query(self,
             decision_id: Optional[str] = None,
             user_id: Optional[str] = None,
             entry_type: Optional[str] = None,
             start_time: Optional[datetime] = None,
             end_time: Optional[datetime] = None,
             limit: Optional[int] = None) -> List['AuditEntry']:
        """Query audit entries with filters"""
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all entries (use with caution!)"""
        pass


class InMemoryAuditStorage(AuditStorage):
    """
    In-memory audit storage.
    
    Suitable for:
    - Development and testing
    - Demo environments
    - Short-lived sessions
    
    NOT suitable for:
    - Production environments (data lost on restart)
    - Long-term audit trail requirements
    - Compliance requirements
    """
    
    def __init__(self):
        self.entries: List['AuditEntry'] = []
    
    def store(self, entry: 'AuditEntry') -> None:
        """Store an audit entry in memory"""
        self.entries.append(entry)
    
    def query(self,
             decision_id: Optional[str] = None,
             user_id: Optional[str] = None,
             entry_type: Optional[str] = None,
             start_time: Optional[datetime] = None,
             end_time: Optional[datetime] = None,
             limit: Optional[int] = None) -> List['AuditEntry']:
        """Query audit entries with filters"""
        results = self.entries
        
        # Apply filters
        if decision_id:
            results = [e for e in results if e.decision_id == decision_id]
        
        if user_id:
            results = [e for e in results if e.user_id == user_id]
        
        if entry_type:
            results = [e for e in results if e.entry_type == entry_type]
        
        if start_time:
            results = [e for e in results if e.timestamp >= start_time]
        
        if end_time:
            results = [e for e in results if e.timestamp <= end_time]
        
        # Sort by timestamp (newest first)
        results = sorted(results, key=lambda e: e.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            results = results[:limit]
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        if not self.entries:
            return {
                'total_entries': 0,
                'by_type': {},
                'by_level': {},
                'by_user': {},
                'oldest_entry': None,
                'newest_entry': None
            }
        
        by_type = {}
        by_level = {}
        by_user = {}
        
        for entry in self.entries:
            # Count by type
            by_type[entry.entry_type] = by_type.get(entry.entry_type, 0) + 1
            
            # Count by level
            level_str = entry.level.value
            by_level[level_str] = by_level.get(level_str, 0) + 1
            
            # Count by user
            if entry.user_id:
                by_user[entry.user_id] = by_user.get(entry.user_id, 0) + 1
        
        sorted_entries = sorted(self.entries, key=lambda e: e.timestamp)
        
        return {
            'total_entries': len(self.entries),
            'by_type': by_type,
            'by_level': by_level,
            'by_user': by_user,
            'oldest_entry': sorted_entries[0].timestamp.isoformat(),
            'newest_entry': sorted_entries[-1].timestamp.isoformat()
        }
    
    def clear(self) -> None:
        """Clear all entries"""
        self.entries.clear()


class FileAuditStorage(AuditStorage):
    """
    File-based audit storage.
    
    Stores audit entries as JSON lines in a file.
    Suitable for:
    - Development environments
    - Small-scale deployments
    - Backup/export purposes
    
    For production, consider database storage (PostgreSQL, MongoDB, etc.)
    """
    
    def __init__(self, file_path: str):
        """
        Initialize file storage.
        
        Args:
            file_path: Path to the audit log file
        """
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file if it doesn't exist
        if not self.file_path.exists():
            self.file_path.touch()
    
    def store(self, entry: 'AuditEntry') -> None:
        """Store an audit entry to file"""
        with open(self.file_path, 'a') as f:
            f.write(entry.to_json() + '\n')
    
    def query(self,
             decision_id: Optional[str] = None,
             user_id: Optional[str] = None,
             entry_type: Optional[str] = None,
             start_time: Optional[datetime] = None,
             end_time: Optional[datetime] = None,
             limit: Optional[int] = None) -> List['AuditEntry']:
        """Query audit entries from file"""
        from .logger import AuditEntry, AuditLevel
        
        results = []
        
        if not self.file_path.exists():
            return results
        
        with open(self.file_path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                try:
                    data = json.loads(line)
                    
                    # Reconstruct AuditEntry
                    entry = AuditEntry(
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        entry_id=data['entry_id'],
                        entry_type=data['entry_type'],
                        level=AuditLevel(data['level']),
                        decision_id=data.get('decision_id'),
                        user_id=data.get('user_id'),
                        session_id=data.get('session_id'),
                        input_data=data.get('input_data', {}),
                        output_data=data.get('output_data', {}),
                        risk_score=data.get('risk_score'),
                        risk_level=data.get('risk_level'),
                        confidence=data.get('confidence'),
                        uncertainty_flag=data.get('uncertainty_flag', False),
                        human_decision=data.get('human_decision'),
                        human_justification=data.get('human_justification'),
                        oversight_level=data.get('oversight_level'),
                        missing_evidence=data.get('missing_evidence', []),
                        documentation_status=data.get('documentation_status'),
                        compliance_status=data.get('compliance_status'),
                        compliance_violations=data.get('compliance_violations', []),
                        metadata=data.get('metadata', {}),
                        system_version=data.get('system_version'),
                        model_version=data.get('model_version')
                    )
                    
                    # Apply filters
                    if decision_id and entry.decision_id != decision_id:
                        continue
                    if user_id and entry.user_id != user_id:
                        continue
                    if entry_type and entry.entry_type != entry_type:
                        continue
                    if start_time and entry.timestamp < start_time:
                        continue
                    if end_time and entry.timestamp > end_time:
                        continue
                    
                    results.append(entry)
                    
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    # Skip malformed entries
                    continue
        
        # Sort by timestamp (newest first)
        results = sorted(results, key=lambda e: e.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            results = results[:limit]
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        entries = self.query()
        
        if not entries:
            return {
                'total_entries': 0,
                'by_type': {},
                'by_level': {},
                'by_user': {},
                'oldest_entry': None,
                'newest_entry': None,
                'file_size_bytes': 0
            }
        
        by_type = {}
        by_level = {}
        by_user = {}
        
        for entry in entries:
            by_type[entry.entry_type] = by_type.get(entry.entry_type, 0) + 1
            level_str = entry.level.value
            by_level[level_str] = by_level.get(level_str, 0) + 1
            if entry.user_id:
                by_user[entry.user_id] = by_user.get(entry.user_id, 0) + 1
        
        sorted_entries = sorted(entries, key=lambda e: e.timestamp)
        
        return {
            'total_entries': len(entries),
            'by_type': by_type,
            'by_level': by_level,
            'by_user': by_user,
            'oldest_entry': sorted_entries[0].timestamp.isoformat(),
            'newest_entry': sorted_entries[-1].timestamp.isoformat(),
            'file_size_bytes': self.file_path.stat().st_size if self.file_path.exists() else 0
        }
    
    def clear(self) -> None:
        """Clear all entries (deletes the file)"""
        if self.file_path.exists():
            self.file_path.unlink()
        self.file_path.touch()


# TODO(platform): Implement production-grade storage backends
# - PostgreSQL storage for relational queries
# - MongoDB storage for document-based storage
# - S3/Cloud storage for long-term archival
# - Elasticsearch for advanced search and analytics
