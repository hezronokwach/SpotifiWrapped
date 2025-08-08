#!/usr/bin/env python3
"""
Simple test runner for SpotifiWrapped
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tests.test_database import TestSpotifyDatabase
from tests.test_genre_extractor import TestGenreExtractor

def main():
    """Run all tests"""
    
    print("🎵 SpotifiWrapped Test Suite 🎵")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSpotifyDatabase))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestGenreExtractor))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors
    
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    if failures > 0:
        print(f"❌ Failed: {failures}")
    if errors > 0:
        print(f"💥 Errors: {errors}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)