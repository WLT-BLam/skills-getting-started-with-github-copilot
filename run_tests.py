#!/usr/bin/env python3
"""
Test runner script for the Mergington High School Activities API.
Run this script to execute all tests with coverage reporting.
"""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run the test suite with coverage reporting."""
    project_root = Path(__file__).parent
    
    # Change to project directory
    import os
    os.chdir(project_root)
    
    print("🧪 Running FastAPI tests with pytest...")
    print("=" * 50)
    
    # Run tests with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/ directory")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code: {e.returncode}")
        return e.returncode


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)