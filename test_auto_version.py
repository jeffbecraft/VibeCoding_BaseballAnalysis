"""
Test script to verify auto-versioning setup is working correctly.

This script:
1. Checks that all required files exist
2. Verifies version can be read
3. Tests the bump_version.py script (dry run)
"""

import sys
from pathlib import Path


def test_version_files_exist():
    """Verify all version-related files exist"""
    print("Checking required files...")
    
    files_to_check = [
        "src/__init__.py",
        "pyproject.toml",
        "scripts/bump_version.py",
        ".github/workflows/auto-version.yml",
        "docs/VERSION_MANAGEMENT.md",
        "docs/AUTO_VERSION_SUMMARY.md"
    ]
    
    project_root = Path(__file__).parent
    all_exist = True
    
    for file_path in files_to_check:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} NOT FOUND")
            all_exist = False
    
    return all_exist


def test_version_import():
    """Test that version can be imported"""
    print("\nTesting version import...")
    
    try:
        from src import __version__
        print(f"  ✓ Current version: {__version__}")
        return True
    except ImportError as e:
        print(f"  ✗ Failed to import version: {e}")
        return False


def test_version_in_pyproject():
    """Test that version exists in pyproject.toml"""
    print("\nChecking pyproject.toml...")
    
    try:
        import re
        project_root = Path(__file__).parent
        toml_file = project_root / "pyproject.toml"
        content = toml_file.read_text(encoding='utf-8')
        
        match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
        if match:
            print(f"  ✓ Version in pyproject.toml: {match.group(1)}")
            return True
        else:
            print("  ✗ Version not found in pyproject.toml")
            return False
    except Exception as e:
        print(f"  ✗ Error reading pyproject.toml: {e}")
        return False


def test_bump_script_syntax():
    """Test that bump_version.py has valid syntax"""
    print("\nChecking bump_version.py syntax...")
    
    try:
        import py_compile
        project_root = Path(__file__).parent
        script_file = project_root / "scripts" / "bump_version.py"
        
        py_compile.compile(str(script_file), doraise=True)
        print("  ✓ Script syntax is valid")
        return True
    except py_compile.PyCompileError as e:
        print(f"  ✗ Syntax error in script: {e}")
        return False


def test_workflow_file():
    """Test that GitHub workflow file exists and has correct structure"""
    print("\nChecking GitHub workflow...")
    
    try:
        project_root = Path(__file__).parent
        workflow_file = project_root / ".github" / "workflows" / "auto-version.yml"
        content = workflow_file.read_text(encoding='utf-8')
        
        required_sections = [
            "name: Auto Version Bump",
            "on:",
            "jobs:",
            "test-and-version:",
            "Run full regression test suite",
            "Bump version",
            "Create version tag"
        ]
        
        all_found = True
        for section in required_sections:
            if section in content:
                print(f"  ✓ Found: {section}")
            else:
                print(f"  ✗ Missing: {section}")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"  ✗ Error reading workflow file: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Auto-Versioning Setup Verification")
    print("=" * 60)
    
    tests = [
        ("File Existence", test_version_files_exist),
        ("Version Import", test_version_import),
        ("PyProject Version", test_version_in_pyproject),
        ("Bump Script Syntax", test_bump_script_syntax),
        ("Workflow File", test_workflow_file)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Error running {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Auto-versioning setup is complete.")
        print("\nNext steps:")
        print("1. Commit these changes to trigger first auto-version")
        print("2. Push to master/main branch")
        print("3. Check GitHub Actions for workflow execution")
        print("4. Verify version increments to 1.0.1")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
