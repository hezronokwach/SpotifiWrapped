#!/usr/bin/env python3
"""
Simple test runner script for SpotifiWrapped.
"""

import sys
import os
import subprocess
import argparse

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def run_command(cmd, description=""):
    """Run a command and return the result."""
    print(f"🔧 {description}")
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="SpotifiWrapped Test Runner")
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--module', help='Run specific test module')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage (if available)')
    parser.add_argument('--quick', action='store_true', help='Run quick smoke tests')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    print("🎵 SpotifiWrapped Test Runner 🎵")
    print("=" * 50)
    
    success = True
    
    if args.quick or (not any([args.all, args.unit, args.integration, args.module])):
        print("🚀 Running quick smoke tests...")
        
        # Test basic functionality
        basic_tests = [
            [sys.executable, "-m", "unittest", "tests.test_data_processing.TestNormalizeTimestamp", "-v" if args.verbose else "-q"],
            [sys.executable, "-m", "unittest", "tests.test_data_processing.TestCalculateDurationMinutes", "-v" if args.verbose else "-q"],
        ]
        
        for test_cmd in basic_tests:
            if not run_command(test_cmd, "Running basic function tests"):
                success = False
                
    elif args.all:
        print("🎯 Running all tests...")
        cmd = [sys.executable, "tests/test_runner.py"]
        if not args.verbose:
            cmd.append("--quiet")
        success = run_command(cmd, "Running full test suite")
        
    elif args.unit:
        print("🧪 Running unit tests...")
        unit_modules = [
            "tests.test_data_processing",
            "tests.test_database", 
            "tests.test_analyzer",
            "tests.test_api",
            "tests.test_sample_data_generator",
            "tests.test_wellness_analyzer",
            "tests.test_genre_extractor"
        ]
        
        for module in unit_modules:
            cmd = [sys.executable, "-m", "unittest", module, "-v" if args.verbose else "-q"]
            if not run_command(cmd, f"Running {module}"):
                success = False
                
    elif args.integration:
        print("🔗 Running integration tests...")
        cmd = [sys.executable, "-m", "unittest", "tests.test_integration", "-v" if args.verbose else "-q"]
        success = run_command(cmd, "Running integration tests")
        
    elif args.module:
        print(f"📋 Running module: {args.module}")
        cmd = [sys.executable, "tests/test_runner.py", "--module", args.module]
        if not args.verbose:
            cmd.append("--quiet")
        success = run_command(cmd, f"Running {args.module} tests")
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed successfully!")
        print("✅ Your SpotifiWrapped application is ready to rock! 🎸")
    else:
        print("⚠️  Some tests failed.")
        print("🔧 Please check the output above and fix any issues.")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)