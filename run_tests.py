#!/usr/bin/env python3
"""
Test runner script for FlaskTasks application.

This script provides a convenient way to run different types of tests
and generate coverage reports.
"""

import sys
import subprocess
import os


def run_unittest():
    """Run tests using unittest."""
    print("Running tests with unittest...")
    print("=" * 50)
    
    # Run all unittest test suites
    test_files = ['test_simple.py', 'test_app.py', 'test_templates.py']
    results = []
    
    for test_file in test_files:
        print(f"\n--- Running {test_file} ---")
        result = subprocess.run([sys.executable, '-m', 'unittest', test_file, '-v'])
        results.append(result.returncode == 0)
    
    print("✅ All unittest test suites completed!")
    return all(results)


def run_pytest():
    """Run tests using pytest."""
    print("Running tests with pytest...")
    print("=" * 50)
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("pytest not installed. Installing required packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytest'])
    
    # Run pytest test suite
    result = subprocess.run([sys.executable, '-m', 'pytest', 'test_pytest.py', '-v'])
    
    print("✅ pytest test suite completed!")
    return result.returncode == 0


def run_coverage():
    """Run tests with coverage reporting."""
    print("Running tests with coverage...")
    print("=" * 50)
    
    try:
        import coverage
    except ImportError:
        print("Installing coverage...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'])
    
    # Run coverage on all unittest test suites
    test_files = ['test_simple.py', 'test_app.py', 'test_templates.py']
    
    for i, test_file in enumerate(test_files):
        cmd = [sys.executable, '-m', 'coverage', 'run', '--source=app']
        if i > 0:  # Append to existing coverage for subsequent runs
            cmd.append('--append')
        cmd.extend(['-m', 'unittest', test_file])
        subprocess.run(cmd)
    
    print("Note: Using all unittest test suites for coverage")
    
    # Generate coverage report
    subprocess.run([sys.executable, '-m', 'coverage', 'report'])
    subprocess.run([sys.executable, '-m', 'coverage', 'html'])
    
    print("\nCoverage report generated in htmlcov/index.html")


def run_all():
    """Run all test suites."""
    print("Running all tests...")
    print("=" * 50)
    
    success = True
    
    print("\n1. Running unittest suite...")
    if not run_unittest():
        success = False
    
    print("\n2. Running pytest suite...")
    if not run_pytest():
        success = False
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [unittest|pytest|coverage|all]")
        print("\nOptions:")
        print("  unittest  - Run tests using unittest framework")
        print("  pytest    - Run tests using pytest framework")
        print("  coverage  - Run tests with coverage reporting")
        print("  all       - Run all test suites")
        sys.exit(1)
    
    test_type = sys.argv[1].lower()
    
    if test_type == 'unittest':
        success = run_unittest()
    elif test_type == 'pytest':
        success = run_pytest()
    elif test_type == 'coverage':
        run_coverage()
        success = True
    elif test_type == 'all':
        run_all()
        success = True
    else:
        print(f"Unknown test type: {test_type}")
        sys.exit(1)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()