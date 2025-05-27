#!/usr/bin/env python3

"""
Enum Synchronization Script

This script ensures that Python enums and TypeScript enums stay in sync.
It can be run as part of the type generation pipeline to catch enum mismatches.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set


def extract_python_enum_values(enum_file: Path) -> Dict[str, Set[str]]:
    """Extract enum values from Python enum files."""
    enums = {}
    
    if not enum_file.exists():
        return enums
    
    content = enum_file.read_text()
    
    # Find ProcessingStatus enum
    pattern = r'class ProcessingStatus\(.*?\):(.*?)(?=class|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        enum_body = match.group(1)
        # Extract enum values like: PENDING = "PENDING"
        value_pattern = r'(\w+)\s*=\s*["\'](\w+)["\']'
        values = set()
        for value_match in re.finditer(value_pattern, enum_body):
            values.add(value_match.group(2))
        enums['ProcessingStatus'] = values
    
    return enums


def extract_typescript_enum_values(enum_file: Path) -> Dict[str, Set[str]]:
    """Extract enum values from TypeScript enum files."""
    enums = {}
    
    if not enum_file.exists():
        return enums
    
    content = enum_file.read_text()
    
    # Find ProcessingStatus enum
    pattern = r'export enum ProcessingStatus\s*{(.*?)}'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        enum_body = match.group(1)
        # Extract enum values like: PENDING = "PENDING"
        value_pattern = r'(\w+)\s*=\s*["\'](\w+)["\']'
        values = set()
        for value_match in re.finditer(value_pattern, enum_body):
            values.add(value_match.group(2))
        enums['ProcessingStatus'] = values
    
    return enums


def extract_database_enum_values(db_file: Path) -> Dict[str, Set[str]]:
    """Extract enum values from database types file."""
    enums = {}
    
    if not db_file.exists():
        return enums
    
    content = db_file.read_text()
    
    # Find processing_status_enum in Constants
    pattern = r'processing_status_enum:\s*\[(.*?)\]'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        values_str = match.group(1)
        # Extract quoted values
        value_pattern = r'["\'](\w+)["\']'
        values = set()
        for value_match in re.finditer(value_pattern, values_str):
            values.add(value_match.group(1))
        enums['processing_status_enum'] = values
    
    return enums


def check_enum_consistency():
    """Check that all enum definitions are consistent."""
    project_root = Path(__file__).parent.parent.parent
    
    # File paths
    python_enum_file = project_root / "apps/core/models/enums.py"
    ts_shared_file = project_root / "packages/types/src/shared.ts"
    db_types_file = project_root / "packages/supabase/types/database.ts"
    
    # Extract enum values
    python_enums = extract_python_enum_values(python_enum_file)
    ts_enums = extract_typescript_enum_values(ts_shared_file)
    db_enums = extract_database_enum_values(db_types_file)
    
    print("🔍 Checking enum consistency...")
    
    # Check ProcessingStatus consistency
    python_values = python_enums.get('ProcessingStatus', set())
    ts_values = ts_enums.get('ProcessingStatus', set())
    db_values = db_enums.get('processing_status_enum', set())
    
    all_consistent = True
    
    if python_values != ts_values:
        print("❌ ProcessingStatus mismatch between Python and TypeScript:")
        print(f"   Python: {sorted(python_values)}")
        print(f"   TypeScript: {sorted(ts_values)}")
        all_consistent = False
    
    if python_values != db_values:
        print("❌ ProcessingStatus mismatch between Python and Database:")
        print(f"   Python: {sorted(python_values)}")
        print(f"   Database: {sorted(db_values)}")
        all_consistent = False
    
    if ts_values != db_values:
        print("❌ ProcessingStatus mismatch between TypeScript and Database:")
        print(f"   TypeScript: {sorted(ts_values)}")
        print(f"   Database: {sorted(db_values)}")
        all_consistent = False
    
    if all_consistent:
        print("✅ All ProcessingStatus enums are consistent!")
        print(f"   Values: {sorted(python_values)}")
    
    return all_consistent


if __name__ == "__main__":
    consistent = check_enum_consistency()
    exit(0 if consistent else 1)
