"""
Run tests and automatically generate Allure report
This script runs pytest and then generates/opens the Allure report
"""
import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run pytest tests"""
    print("="*80)
    print("RUNNING TESTS")
    print("="*80)
    
    # Run pytest with Allure
    cmd = [
        "pytest",
        "tests/test_maven_automation.py",
        "-v",
        "--alluredir=reports/allure-results",
        "--clean-alluredir"
    ]
    
    # Add any additional arguments passed to this script
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    print(f"Command: {' '.join(cmd)}")
    print("="*80)
    
    result = subprocess.run(cmd)
    return result.returncode

def generate_and_open_report():
    """Generate and open Allure report"""
    print("\n" + "="*80)
    print("GENERATING ALLURE REPORT")
    print("="*80)
    
    # Import and run the report generation
    from generate_allure_report import generate_allure_report, open_allure_report
    
    if generate_allure_report():
        open_allure_report()

if __name__ == "__main__":
    # Run tests
    exit_code = run_tests()
    
    # Generate report regardless of test results
    generate_and_open_report()
    
    # Exit with pytest exit code
    sys.exit(exit_code)


