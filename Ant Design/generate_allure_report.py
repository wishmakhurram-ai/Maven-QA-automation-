"""
Script to generate and open Allure report after test execution
Run this script after running pytest to view the Allure report
"""
import os
import subprocess
import sys
import webbrowser
from pathlib import Path

def generate_allure_report():
    """Generate Allure report from test results"""
    allure_results_dir = Path("reports/allure-results")
    allure_report_dir = Path("reports/allure-report")
    
    # Check if allure results exist
    if not allure_results_dir.exists() or not list(allure_results_dir.glob("*.json")):
        print("[ERROR] No Allure results found. Please run tests first with:")
        print("   pytest tests/test_maven_automation.py -v")
        return False
    
    print("[INFO] Generating Allure report...")
    
    try:
        # Generate report
        result = subprocess.run(
            ["allure", "generate", str(allure_results_dir), "--clean", "-o", str(allure_report_dir)],
            capture_output=True,
            text=True,
            check=True
        )
        print("[OK] Allure report generated successfully!")
        print(f"   Report location: {allure_report_dir.absolute()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error generating Allure report: {e.stderr}")
        print("\n[INFO] Make sure Allure is installed:")
        print("   Windows: Download from https://github.com/allure-framework/allure2/releases")
        print("   Or use: scoop install allure")
        return False
    except FileNotFoundError:
        print("[ERROR] Allure command not found!")
        print("\n[INFO] Please install Allure:")
        print("   Windows: Download from https://github.com/allure-framework/allure2/releases")
        print("   Or use: scoop install allure")
        print("   Or use: choco install allure")
        return False

def open_allure_report():
    """Open Allure report in browser"""
    allure_report_dir = Path("reports/allure-report")
    index_html = allure_report_dir / "index.html"
    
    if index_html.exists():
        print("[INFO] Opening Allure report in browser...")
        file_url = f"file:///{index_html.absolute()}"
        webbrowser.open(file_url)
        print(f"[OK] Report opened: {file_url}")
    else:
        print("[ERROR] Allure report not found. Please generate it first.")
        print("   Run: python generate_allure_report.py")

def serve_allure_report():
    """Serve Allure report using allure serve"""
    allure_results_dir = Path("reports/allure-results")
    
    if not allure_results_dir.exists():
        print("[ERROR] No Allure results found. Please run tests first.")
        return
    
        print("[INFO] Starting Allure server...")
    try:
        subprocess.run(["allure", "serve", str(allure_results_dir)], check=True)
    except FileNotFoundError:
        print("[ERROR] Allure command not found!")
        print("\n[INFO] Please install Allure:")
        print("   Windows: Download from https://github.com/allure-framework/allure2/releases")
    except KeyboardInterrupt:
        print("\n[OK] Allure server stopped.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve_allure_report()
    else:
        if generate_allure_report():
            open_allure_report()


