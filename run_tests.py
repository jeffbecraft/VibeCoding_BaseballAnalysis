"""
Test Runner for MLB Baseball Analysis System

Runs all regression tests and generates a summary report.
"""

import unittest
import sys
import os
from io import StringIO

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_all_tests(verbose=True):
    """
    Run all test suites and return results.
    
    Args:
        verbose: Whether to show detailed output
        
    Returns:
        TestResult object
    """
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result


def print_test_summary(result):
    """
    Print a summary of test results.
    
    Args:
        result: TestResult object from test run
    """
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    success = total_tests - failures - errors - skipped
    
    print(f"\nTotal Tests Run: {total_tests}")
    print(f"✓ Passed: {success}")
    print(f"✗ Failed: {failures}")
    print(f"⚠ Errors: {errors}")
    print(f"⊘ Skipped: {skipped}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
        
        if failures > 0:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        
        if errors > 0:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    print("=" * 70)


def run_specific_test(test_file):
    """
    Run a specific test file.
    
    Args:
        test_file: Name of test file (e.g., 'test_data_fetcher')
    """
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{test_file}')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run MLB Analysis regression tests')
    parser.add_argument('--test', type=str, help='Run specific test file (e.g., test_cache)')
    parser.add_argument('--quiet', action='store_true', help='Minimize output')
    
    args = parser.parse_args()
    
    if args.test:
        print(f"\nRunning specific test: {args.test}\n")
        result = run_specific_test(args.test)
    else:
        print("\nRunning all regression tests...\n")
        result = run_all_tests(verbose=not args.quiet)
    
    print_test_summary(result)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
