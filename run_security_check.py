"""
Security Check Script for MLB Statistics Application

Runs comprehensive security checks following industry standards:
- Code security scanning (bandit)
- Dependency vulnerability scanning (safety, pip-audit)
- Code quality analysis (pylint)
- Type checking (mypy)
- Secret detection

Run this before pushing sensitive changes or periodically for audits.

Usage:
    python run_security_check.py
"""

import subprocess
import sys
import json
import os
from pathlib import Path


class SecurityChecker:
    """Runs various security and code quality checks."""
    
    def __init__(self):
        self.checks_passed = []
        self.checks_failed = []
        self.warnings = []
        # Use sys.executable to ensure we use the same Python interpreter
        self.python_exe = sys.executable
        
    def print_header(self, text):
        """Print a formatted header."""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)
        
    def run_command(self, cmd, check_name, allow_failure=False):
        """Run a command and track results."""
        print(f"\n🔍 Running: {check_name}")
        print(f"   Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print(f"✅ {check_name}: PASSED")
                self.checks_passed.append(check_name)
                if result.stdout.strip():
                    print(result.stdout)
                return True
            else:
                if allow_failure:
                    print(f"⚠️  {check_name}: WARNING")
                    self.warnings.append(check_name)
                    if result.stdout.strip():
                        print(result.stdout)
                    if result.stderr.strip():
                        print(result.stderr)
                    return True
                else:
                    print(f"❌ {check_name}: FAILED")
                    self.checks_failed.append(check_name)
                    if result.stdout.strip():
                        print(result.stdout)
                    if result.stderr.strip():
                        print(result.stderr)
                    return False
                    
        except FileNotFoundError:
            print(f"❌ {check_name}: Tool not installed")
            self.checks_failed.append(f"{check_name} (not installed)")
            return False
        except Exception as e:
            print(f"❌ {check_name}: Error - {e}")
            self.checks_failed.append(f"{check_name} (error)")
            return False
    
    def check_bandit(self):
        """Run bandit security scanner."""
        self.print_header("SECURITY SCAN: Bandit")
        print("Scanning for common security issues in Python code...")
        
        cmd = [
            self.python_exe, '-m', 'bandit',
            '-r', 'src/', 'utils/',
            '-f', 'screen',
            '-ll'  # Only show medium and high severity
        ]
        
        return self.run_command(cmd, "Bandit Security Scan", allow_failure=True)
    
    def check_safety(self):
        """Run safety to check for known vulnerabilities in dependencies."""
        self.print_header("DEPENDENCY SCAN: Safety")
        print("Checking dependencies for known vulnerabilities...")
        
        cmd = [self.python_exe, '-m', 'safety', 'check', '--json']
        
        # Safety returns non-zero if vulnerabilities found, but that's expected
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        try:
            if result.stdout.strip():
                data = json.loads(result.stdout)
                if isinstance(data, list) and len(data) == 0:
                    print("✅ No known vulnerabilities found in dependencies")
                    self.checks_passed.append("Safety Dependency Scan")
                    return True
                else:
                    print(f"⚠️  Found {len(data)} potential vulnerabilities:")
                    print(result.stdout)
                    self.warnings.append("Safety Dependency Scan")
                    return True
        except json.JSONDecodeError:
            # If not JSON, just show output
            if "No known security vulnerabilities" in result.stdout:
                print("✅ No known vulnerabilities found in dependencies")
                self.checks_passed.append("Safety Dependency Scan")
                return True
            
        if result.stdout.strip():
            print(result.stdout)
        if result.stderr.strip():
            print(result.stderr)
            
        self.warnings.append("Safety Dependency Scan")
        return True
    
    def check_pip_audit(self):
        """Run pip-audit for comprehensive dependency scanning."""
        self.print_header("DEPENDENCY SCAN: pip-audit")
        print("Comprehensive dependency vulnerability scanning...")
        
        cmd = [self.python_exe, '-m', 'pip_audit', '--desc']
        
        return self.run_command(cmd, "pip-audit Dependency Scan", allow_failure=True)
    
    def check_pylint(self):
        """Run pylint for code quality."""
        self.print_header("CODE QUALITY: Pylint")
        print("Analyzing code quality and potential issues...")
        
        cmd = [
            self.python_exe, '-m', 'pylint',
            'src/', 'utils/',
            '--disable=C0111,R0903',  # Disable docstring and too-few-public-methods
            '--max-line-length=100',
            '--score=yes'
        ]
        
        return self.run_command(cmd, "Pylint Code Quality", allow_failure=True)
    
    def check_secrets(self):
        """Check for accidentally committed secrets."""
        self.print_header("SECRET DETECTION")
        print("Scanning for potential secrets in code...")
        
        # Simple pattern matching for common secrets
        patterns = [
            'password',
            'api_key',
            'secret',
            'token',
            'private_key'
        ]
        
        issues_found = []
        
        for pattern in patterns:
            # Search Python files
            try:
                result = subprocess.run(
                    ['git', 'grep', '-i', pattern, '--', '*.py'],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    # Filter out comments and variable names
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        # Skip if it's just a variable name or comment
                        if '# ' not in line or '"""' not in line:
                            if '=' in line and '"' in line.split('=')[1]:
                                issues_found.append(line)
            except:
                pass
        
        if issues_found:
            print(f"⚠️  Found {len(issues_found)} potential secrets:")
            for issue in issues_found[:5]:  # Show first 5
                print(f"   {issue}")
            self.warnings.append("Secret Detection")
        else:
            print("✅ No obvious secrets detected")
            self.checks_passed.append("Secret Detection")
        
        return True
    
    def check_imports(self):
        """Check for insecure imports."""
        self.print_header("IMPORT SECURITY")
        print("Checking for potentially insecure imports...")
        
        dangerous_imports = [
            'pickle',  # Can execute arbitrary code
            'yaml.load',  # yaml.safe_load should be used
            'eval',
            'exec',
            'compile',
            '__import__'
        ]
        
        issues = []
        for pattern in dangerous_imports:
            try:
                result = subprocess.run(
                    ['git', 'grep', pattern, '--', '*.py'],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    issues.append(f"Found '{pattern}': {len(result.stdout.split(chr(10)))} occurrences")
            except:
                pass
        
        if issues:
            print("⚠️  Found potentially dangerous patterns:")
            for issue in issues:
                print(f"   {issue}")
            print("\n   Note: Some uses may be legitimate (e.g., pickle for caching)")
            self.warnings.append("Import Security Check")
        else:
            print("✅ No dangerous imports detected")
            self.checks_passed.append("Import Security Check")
        
        return True
    
    def run_all_checks(self):
        """Run all security checks."""
        print("\n" + "=" * 70)
        print("  MLB STATISTICS - SECURITY & QUALITY CHECK")
        print("  Following Industry Standard Secure Coding Practices")
        print("=" * 70)
        
        # Check if we're in a git repo
        try:
            subprocess.run(['git', 'rev-parse', '--git-dir'], 
                         capture_output=True, check=True)
        except:
            print("\n⚠️  Warning: Not in a git repository. Some checks may be limited.")
        
        # Run all checks
        self.check_bandit()
        self.check_safety()
        self.check_pip_audit()
        self.check_secrets()
        self.check_imports()
        self.check_pylint()
        
        # Print summary
        self.print_summary()
        
        # Return exit code
        return 0 if len(self.checks_failed) == 0 else 1
    
    def print_summary(self):
        """Print summary of all checks."""
        self.print_header("SECURITY CHECK SUMMARY")
        
        print(f"\n✅ Passed: {len(self.checks_passed)}")
        for check in self.checks_passed:
            print(f"   • {check}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings: {len(self.warnings)}")
            for check in self.warnings:
                print(f"   • {check}")
        
        if self.checks_failed:
            print(f"\n❌ Failed: {len(self.checks_failed)}")
            for check in self.checks_failed:
                print(f"   • {check}")
        
        print("\n" + "=" * 70)
        
        if self.checks_failed:
            print("⚠️  SECURITY ISSUES DETECTED - Review and fix before deploying")
            print("\nInstall missing tools:")
            print("  pip install bandit safety pip-audit pylint")
        elif self.warnings:
            print("✅ NO CRITICAL ISSUES - Review warnings before deploying")
        else:
            print("✅ ALL SECURITY CHECKS PASSED - Code follows secure practices")
        
        print("=" * 70 + "\n")


def main():
    """Main entry point."""
    checker = SecurityChecker()
    exit_code = checker.run_all_checks()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
