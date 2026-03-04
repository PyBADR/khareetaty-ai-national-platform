#!/usr/bin/env python3
"""Ownership Checker - CI Enforcement Tool.

Scans the codebase for DecisionRequest instantiations and ensures
that all decisions have proper ownership and accountability.

Usage:
    python tools/governance/check_ownership.py

Exit codes:
    0: All decisions have proper ownership
    1: Ownership violations found
    2: Script error

This script MUST be run in CI/CD pipelines.
Failure = build fails.
"""

import ast
import sys
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass


@dataclass
class OwnershipViolation:
    """Represents an ownership violation found in code."""
    file_path: str
    line_number: int
    violation_type: str
    message: str
    code_snippet: str


class DecisionRequestVisitor(ast.NodeVisitor):
    """AST visitor to find DecisionRequest instantiations."""
    
    def __init__(self, file_path: str, source_code: str):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.splitlines()
        self.violations: List[OwnershipViolation] = []
    
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls to find DecisionRequest instantiations."""
        # Check if this is a DecisionRequest call
        is_decision_request = False
        
        if isinstance(node.func, ast.Name) and node.func.id == "DecisionRequest":
            is_decision_request = True
        elif isinstance(node.func, ast.Attribute) and node.func.attr == "DecisionRequest":
            is_decision_request = True
        
        if is_decision_request:
            self._check_decision_request(node)
        
        self.generic_visit(node)
    
    def _check_decision_request(self, node: ast.Call) -> None:
        """Check if a DecisionRequest has ownership and accountability_scope."""
        # Extract keyword arguments
        kwargs = {kw.arg: kw.value for kw in node.keywords}
        
        # Check for ownership
        has_ownership = 'ownership' in kwargs
        has_accountability_scope = 'accountability_scope' in kwargs
        
        # Get code snippet
        line_num = node.lineno
        code_snippet = self._get_code_snippet(line_num)
        
        # Check if this is in a test file (tests are allowed to skip ownership)
        is_test_file = 'test_' in self.file_path or '/tests/' in self.file_path
        
        if not is_test_file:
            if not has_ownership:
                self.violations.append(OwnershipViolation(
                    file_path=self.file_path,
                    line_number=line_num,
                    violation_type="MISSING_OWNERSHIP",
                    message="DecisionRequest missing 'ownership' parameter",
                    code_snippet=code_snippet,
                ))
            
            if not has_accountability_scope:
                self.violations.append(OwnershipViolation(
                    file_path=self.file_path,
                    line_number=line_num,
                    violation_type="MISSING_ACCOUNTABILITY_SCOPE",
                    message="DecisionRequest missing 'accountability_scope' parameter",
                    code_snippet=code_snippet,
                ))
    
    def _get_code_snippet(self, line_num: int, context_lines: int = 2) -> str:
        """Get code snippet around a line number."""
        start = max(0, line_num - context_lines - 1)
        end = min(len(self.source_lines), line_num + context_lines)
        
        snippet_lines = []
        for i in range(start, end):
            prefix = ">>> " if i == line_num - 1 else "    "
            snippet_lines.append(f"{prefix}{self.source_lines[i]}")
        
        return "\n".join(snippet_lines)


def scan_file(file_path: Path) -> List[OwnershipViolation]:
    """Scan a Python file for ownership violations.
    
    Args:
        file_path: Path to the Python file
    
    Returns:
        List of ownership violations found
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Parse the AST
        tree = ast.parse(source_code, filename=str(file_path))
        
        # Visit the AST
        visitor = DecisionRequestVisitor(str(file_path), source_code)
        visitor.visit(tree)
        
        return visitor.violations
    
    except SyntaxError as e:
        print(f"⚠️  Syntax error in {file_path}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"⚠️  Error scanning {file_path}: {e}", file=sys.stderr)
        return []


def scan_directory(directory: Path, exclude_patterns: List[str] = None) -> List[OwnershipViolation]:
    """Scan a directory recursively for ownership violations.
    
    Args:
        directory: Directory to scan
        exclude_patterns: Patterns to exclude (e.g., '__pycache__', '.git')
    
    Returns:
        List of all ownership violations found
    """
    if exclude_patterns is None:
        exclude_patterns = ['__pycache__', '.git', '.venv', 'venv', 'node_modules', '.pytest_cache']
    
    all_violations = []
    
    for py_file in directory.rglob('*.py'):
        # Skip excluded patterns
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue
        
        violations = scan_file(py_file)
        all_violations.extend(violations)
    
    return all_violations


def print_violations(violations: List[OwnershipViolation]) -> None:
    """Print violations in a readable format."""
    if not violations:
        print("✅ No ownership violations found!")
        return
    
    print(f"\n❌ Found {len(violations)} ownership violation(s):\n")
    
    for i, violation in enumerate(violations, 1):
        print(f"Violation #{i}:")
        print(f"  File: {violation.file_path}")
        print(f"  Line: {violation.line_number}")
        print(f"  Type: {violation.violation_type}")
        print(f"  Message: {violation.message}")
        print(f"\n  Code:")
        for line in violation.code_snippet.split('\n'):
            print(f"  {line}")
        print()


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code (0 = success, 1 = violations found, 2 = error)
    """
    print("🔍 Scanning codebase for ownership violations...\n")
    
    # Get repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    # Scan key directories
    directories_to_scan = [
        repo_root / "core",
        repo_root / "modules",
        repo_root / "spaces",
    ]
    
    all_violations = []
    
    for directory in directories_to_scan:
        if directory.exists():
            print(f"Scanning {directory}...")
            violations = scan_directory(directory)
            all_violations.extend(violations)
        else:
            print(f"⚠️  Directory not found: {directory}")
    
    print()
    
    # Print results
    print_violations(all_violations)
    
    # Print summary
    if all_violations:
        print("\n" + "="*80)
        print("OWNERSHIP ENFORCEMENT FAILED")
        print("="*80)
        print(f"\nFound {len(all_violations)} violation(s).")
        print("\nAll DecisionRequest instantiations MUST include:")
        print("  1. ownership: AccountabilityChain")
        print("  2. accountability_scope: AccountabilityScope")
        print("\nSee docs/OWNERSHIP_MODEL.md for details.")
        print("\nCI build will FAIL until these are fixed.\n")
        return 1
    else:
        print("\n" + "="*80)
        print("✅ OWNERSHIP ENFORCEMENT PASSED")
        print("="*80)
        print("\nAll decisions have proper ownership and accountability.\n")
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Script error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(2)
