#!/usr/bin/env python3
"""
Auto-increment version number after successful test execution.

This script:
1. Reads the current version from src/__init__.py
2. Increments the patch version (e.g., 1.0.0 -> 1.0.1)
3. Updates version in src/__init__.py and pyproject.toml
4. Commits the change to git

Version format: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes (manual increment)
- MINOR: New features (manual increment)
- PATCH: Bug fixes, automated increment
"""

import re
import sys
from pathlib import Path
from datetime import datetime


def get_current_version(init_file: Path) -> str:
    """Extract current version from __init__.py"""
    content = init_file.read_text(encoding='utf-8')
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Could not find __version__ in src/__init__.py")
    return match.group(1)


def parse_version(version: str) -> tuple:
    """Parse version string into (major, minor, patch)"""
    parts = version.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}. Expected MAJOR.MINOR.PATCH")
    return tuple(int(p) for p in parts)


def increment_patch(version: str) -> str:
    """Increment the patch version number"""
    major, minor, patch = parse_version(version)
    return f"{major}.{minor}.{patch + 1}"


def update_init_file(init_file: Path, new_version: str) -> None:
    """Update version in src/__init__.py"""
    content = init_file.read_text(encoding='utf-8')
    updated = re.sub(
        r'(__version__\s*=\s*["\'])[^"\']+(["\'])',
        rf'\g<1>{new_version}\g<2>',
        content
    )
    init_file.write_text(updated, encoding='utf-8')
    print(f"✓ Updated {init_file}")


def update_pyproject_toml(toml_file: Path, new_version: str) -> None:
    """Update version in pyproject.toml"""
    content = toml_file.read_text(encoding='utf-8')
    updated = re.sub(
        r'(^version\s*=\s*["\'])[^"\']+(["\'])',
        rf'\g<1>{new_version}\g<2>',
        content,
        flags=re.MULTILINE
    )
    toml_file.write_text(updated, encoding='utf-8')
    print(f"✓ Updated {toml_file}")


def update_changelog(changelog_file: Path, version: str, old_version: str) -> None:
    """Add entry to CHANGELOG.md"""
    if not changelog_file.exists():
        # Create new changelog
        content = f"""# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [{version}] - {datetime.now().strftime('%Y-%m-%d')}

### Changed
- Auto-incremented version from {old_version} after successful test execution

"""
    else:
        content = changelog_file.read_text(encoding='utf-8')
        # Find insertion point (after the header, before first version entry)
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('## ['):
                insert_idx = i
                break
        
        new_entry = f"""## [{version}] - {datetime.now().strftime('%Y-%m-%d')}

### Changed
- Auto-incremented version from {old_version} after successful test execution

"""
        if insert_idx > 0:
            lines.insert(insert_idx, new_entry)
        else:
            lines.append(new_entry)
        
        content = '\n'.join(lines)
    
    changelog_file.write_text(content, encoding='utf-8')
    print(f"✓ Updated {changelog_file}")


def main():
    """Main version bump workflow"""
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # File paths
    init_file = project_root / "src" / "__init__.py"
    toml_file = project_root / "pyproject.toml"
    changelog_file = project_root / "CHANGELOG.md"
    
    # Validate files exist
    if not init_file.exists():
        print(f"✗ Error: {init_file} not found")
        sys.exit(1)
    if not toml_file.exists():
        print(f"✗ Error: {toml_file} not found")
        sys.exit(1)
    
    try:
        # Get current version
        current_version = get_current_version(init_file)
        print(f"Current version: {current_version}")
        
        # Calculate new version
        new_version = increment_patch(current_version)
        print(f"New version: {new_version}")
        
        # Update files
        update_init_file(init_file, new_version)
        update_pyproject_toml(toml_file, new_version)
        update_changelog(changelog_file, new_version, current_version)
        
        print(f"\n✓ Version bumped from {current_version} to {new_version}")
        print(f"\nFiles updated:")
        print(f"  - {init_file.relative_to(project_root)}")
        print(f"  - {toml_file.relative_to(project_root)}")
        print(f"  - {changelog_file.relative_to(project_root)}")
        
        return 0
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
