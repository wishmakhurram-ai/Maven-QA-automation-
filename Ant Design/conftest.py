"""
Root conftest.py for pytest-bdd automation
Provides context fixture and WebDriver setup for all tests
"""
# CRITICAL: Import step definitions FIRST before anything else
# This ensures step definitions are registered with pytest-bdd BEFORE any test files are processed
# Import in this order to ensure dependencies are loaded correctly
import steps.maven_steps  # noqa: F401
import steps.button_steps  # noqa: F401
import steps.input_steps  # noqa: F401
import steps.dropdown_steps  # noqa: F401
import steps.menu_steps  # noqa: F401
import steps.pagination_steps  # noqa: F401
import steps.upload_steps  # noqa: F401
import steps.table_steps  # noqa: F401
import steps.checkbox_steps  # noqa: F401
import steps.treeselect_steps  # noqa: F401
import steps.datepicker_steps  # noqa: F401

import pytest

# Optional Allure support: tests must still run even if allure is not installed
try:
    import allure  # type: ignore
    HAS_ALLURE = True
except ModuleNotFoundError:
    allure = None  # type: ignore
    HAS_ALLURE = False
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from framework.components.input_handler import InputHandler
from framework.components.button_handler import ButtonHandler
from framework.components.dropdown_handler import DropdownHandler
from framework.components.menu_handler import MenuHandler
from framework.components.pagination_handler import PaginationHandler
from framework.components.upload_handler import UploadHandler
from framework.components.table_handler import TableHandler
from framework.components.checkbox_handler import CheckboxHandler
from framework.components.treeselect_handler import TreeSelectHandler
from framework.components.datepicker_handler import DatePickerHandler
from framework.context.element_context import ElementContext
import inspect
import os
import sys
from datetime import datetime

# Enable ANSI color codes on Windows for colored output
if sys.platform == 'win32':
    os.system('')  # Enable ANSI escape sequences on Windows

# Global test results tracker
test_results = {
    'passed': [],
    'failed': [],
    'skipped': [],
    'total': 0,
    'start_time': None,
    'end_time': None
}

# Global variable to store current step name for data-attr-id logging
_current_step_name = None


@pytest.fixture(scope="session")
def driver():
    """
    Create and configure Chrome WebDriver instance
    Returns WebDriver instance that will be reused across tests
    """
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Performance optimizations
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")  # Disable image loading for speed
    chrome_options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2,  # Disable images
        "profile.default_content_setting_values.notifications": 2  # Disable notifications
    })
    
    # Create WebDriver instance
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(1)  # Reduced to 1 second for faster execution
    
    yield driver
    
    # Cleanup
    driver.quit()


def _perform_login_if_needed(driver, context_obj):
    """
    Helper function to perform login for ADMIN-* scenarios
    Only logs in if user is not already logged in
    """
    try:
        current_url = driver.current_url.lower()
        
        # Check if already logged in (not on login page)
        if 'login' not in current_url:
            # Verify we're actually logged in by checking for dashboard elements
            try:
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                wait = WebDriverWait(driver, 2)
                # Try to find dashboard elements (navigation, firms table, etc.) - if found, we're logged in
                dashboard_elements = wait.until(EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Firms') or contains(text(), 'Users')]")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table, .ant-table, [class*='table']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "nav, [class*='menu'], [class*='navigation']"))
                ))
                # Dashboard elements found, we're logged in
                print(f"   >> Already logged in, reusing session")
                context_obj.logged_in = True
                return True
            except:
                # Dashboard elements not found, might not be logged in - perform login
                print(f"   >> Not logged in (no dashboard elements found), performing login...")
        else:
            print(f"   >> On login page, performing login...")
        
        # Perform login
        from steps.maven_steps import get_base_url, get_login_url, MAVEN_APP_BASE_URL
        
        # Set base URL on context first
        base_url = get_base_url(context_obj)
        context_obj.base_url = base_url
        
        # Get login URL
        login_url = get_login_url(context_obj)
        driver.get(login_url)
        
        # Wait for page to load
        from selenium.webdriver.support.ui import WebDriverWait
        wait = WebDriverWait(driver, 5)
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        
        # Enter credentials
        email = "wishma.khurram@rolustech.com"
        password = "Lorem123"
        
        # Enter email
        context_obj.input_handler.fill_input('email', email, identifier_type='auto', timeout=3)
        
        # Enter password
        context_obj.input_handler.fill_input('password', password, identifier_type='auto', timeout=3)
        
        # Click login button
        button_clicked = context_obj.button_handler.click_button('Log In', identifier_type='auto')
        if not button_clicked:
            context_obj.button_handler.click_button('Log In', identifier_type='text')
        
        # Wait for navigation away from login page
        login_url_before = driver.current_url.lower()
        wait = WebDriverWait(driver, 10)
        try:
            def navigation_complete(driver):
                current_url = driver.current_url.lower()
                if current_url != login_url_before and 'login' not in current_url:
                    return True
                if 'dashboard' in current_url or 'firms' in current_url or 'users' in current_url:
                    return True
                return False
            
            wait.until(navigation_complete)
            current_url = driver.current_url
            print(f"   >> Login successful, navigated to: {current_url}")
            
            # Wait for page to fully load
            wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
            import time
            time.sleep(0.3)  # Minimal wait for speed
            
            context_obj.logged_in = True
            return True
        except Exception as e:
            current_url = driver.current_url
            print(f"   >> Login navigation wait completed, current URL: {current_url}")
            if 'login' not in current_url.lower():
                context_obj.logged_in = True
                return True
            else:
                print(f"   >> Login may have failed - still on login page")
                return False
    except Exception as e:
        print(f"   >> Error during login: {str(e)}")
        return False


@pytest.fixture(scope="function")
def context(driver, request):
    """
    Create context object with all handlers for step definitions
    This fixture is automatically injected into all step definitions
    For ADMIN-* scenarios, automatically ensures user is logged in
    For LOGIN-* scenarios, executes naturally without login
    """
    # Create element context for storing elements
    element_context = ElementContext()
    
    # Create handlers with shared element context
    input_handler = InputHandler(driver, context=element_context)
    button_handler = ButtonHandler(driver, context=element_context)
    dropdown_handler = DropdownHandler(driver, context=element_context)
    menu_handler = MenuHandler(driver, context=element_context)
    pagination_handler = PaginationHandler(driver, context=element_context)
    upload_handler = UploadHandler(driver, context=element_context)
    table_handler = TableHandler(driver, context=element_context)
    checkbox_handler = CheckboxHandler(driver, context=element_context)
    treeselect_handler = TreeSelectHandler(driver, context=element_context)
    datepicker_handler = DatePickerHandler(driver, context=element_context)
    
    # Create PatternDiscovery instance for shared use
    from framework.utils.pattern_discovery import PatternDiscovery
    pattern_discovery = PatternDiscovery(driver)
    
    # Create context object with all required attributes
    class Context:
        def __init__(self):
            self.driver = driver
            self.element_context = element_context
            self.context = element_context  # Alias for compatibility with step definitions
            self.input_handler = input_handler
            self.button_handler = button_handler
            self.dropdown_handler = dropdown_handler
            self.menu_handler = menu_handler
            self.pagination_handler = pagination_handler
            self.upload_handler = upload_handler
            self.table_handler = table_handler
            self.checkbox_handler = checkbox_handler
            self.treeselect_handler = treeselect_handler
            self.datepicker_handler = datepicker_handler
            self.pattern_discovery = pattern_discovery
            self.logged_in = False
    
    context_obj = Context()
    
    # Check if this is an ADMIN-* scenario that needs login
    # Only auto-login for ADMIN-* scenarios, NOT for LOGIN-* scenarios
    test_name = request.node.name if hasattr(request, 'node') else ''
    
    # Detect ADMIN-* scenarios (but NOT LOGIN-* scenarios)
    is_admin_scenario = (
        'admin_lands' in test_name.lower() or
        'admin_can_access' in test_name.lower() or
        'admin_panel' in test_name.lower() or
        'firms_list' in test_name.lower() or
        ('firms' in test_name.lower() and 'navigate' not in test_name.lower() and 'login' not in test_name.lower()) or
        ('users' in test_name.lower() and 'navigate' not in test_name.lower() and 'login' not in test_name.lower())
    ) and 'login' not in test_name.lower()  # Exclude LOGIN-* scenarios
    
    # For ADMIN-* scenarios, ensure user is logged in
    if is_admin_scenario:
        print(f"   >> ADMIN scenario detected: {test_name}")
        print(f"   >> Checking login status and logging in if needed...")
        _perform_login_if_needed(driver, context_obj)
    
    yield context_obj
    
    # Cleanup if needed
    # Context is automatically cleaned up after each test


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    """
    Sort tests by their line number in the feature file to ensure execution order
    Tests will execute in the order they appear in the feature file
    """
    def get_scenario_line_number(item):
        """Get the line number of the scenario from the feature file"""
        try:
            if hasattr(item, 'scenario'):
                scenario = item.scenario
                if hasattr(scenario, 'line_number'):
                    return scenario.line_number
            # Fallback: try to get from location
            if hasattr(item, 'location') and len(item.location) >= 2:
                return item.location[1] if isinstance(item.location[1], int) else 0
        except:
            pass
        return 0
    
    # Sort items by their scenario line number
    items.sort(key=get_scenario_line_number)


@pytest.hookimpl(tryfirst=True)
def pytest_bdd_before_step(request, feature, scenario, step, step_func):
    """
    Hook called before each step execution
    Displays test case name, line number, and step statement
    """
    global _current_step_name
    try:
        # Get scenario name
        scenario_name = scenario.name if hasattr(scenario, 'name') else 'Unknown Scenario'
        
        # Get feature file path
        feature_file = feature.filename if hasattr(feature, 'filename') else 'Unknown Feature'
        feature_file_short = feature_file.split('\\')[-1] if '\\' in feature_file else feature_file.split('/')[-1]
        
        # Get step line number
        step_line = step.line_number if hasattr(step, 'line_number') else 'Unknown'
        
        # Get step statement
        step_statement = step.name if hasattr(step, 'name') else str(step)
        
        # Store current step name globally for data-attr-id logging
        _current_step_name = step_statement
        
        # Print formatted output (condensed for speed)
        print(f"\n>> STEP: {step_statement}")
    except Exception as e:
        # Fallback if hook fails - try to get info from request
        try:
            test_name = request.node.name if hasattr(request, 'node') and hasattr(request.node, 'name') else 'Unknown'
            _current_step_name = test_name
            print(f"\n>> STEP: {test_name}")
        except:
            _current_step_name = "Unknown Step"
            print(f"\n>> STEP: Unknown Step")


@pytest.hookimpl(tryfirst=True)
def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    """
    Hook called after each step execution
    """
    try:
        step_statement = step.name if hasattr(step, 'name') else str(step)
        # ANSI color codes: \033[92m = bright green, \033[0m = reset
        green = '\033[92m'
        reset = '\033[0m'
        print(f"   {green}✓ PASSED: {step_statement}{reset}")
    except:
        pass


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """
    Hook called before each test starts
    Displays test case information
    """
    try:
        # Get test name
        test_name = item.name if hasattr(item, 'name') else 'Unknown Test'
        
        # Try to get scenario info from pytest-bdd
        scenario_name = test_name
        feature_file = None
        feature_line = None
        
        if hasattr(item, 'scenario'):
            scenario = item.scenario
            if hasattr(scenario, 'name'):
                scenario_name = scenario.name
            if hasattr(scenario, 'feature'):
                feature = scenario.feature
                if hasattr(feature, 'filename'):
                    feature_file = feature.filename
            if hasattr(scenario, 'line_number'):
                feature_line = scenario.line_number
        
        # Print test case info
        print(f"\n{'='*80}")
        print(f"STARTING TEST CASE: {scenario_name}")
        if feature_file:
            feature_file_short = feature_file.split('\\')[-1] if '\\' in feature_file else feature_file.split('/')[-1]
            print(f"FEATURE FILE: {feature_file_short}")
        if feature_line:
            print(f"LINE: {feature_line}")
        print(f"{'='*80}")
    except:
        pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test results and print feature statement with line numbers
    """
    outcome = yield
    rep = outcome.get_result()
    
    # Get feature file and line number information from pytest-bdd
    try:
        # Get scenario name
        scenario_name = item.name if hasattr(item, 'name') else str(item)
        
        # Try to extract feature file path and line from pytest-bdd
        feature_file = None
        feature_line = None
        feature_statement = None
        
        # Method 1: Get from item location (pytest-bdd stores feature file info here)
        if hasattr(item, 'location'):
            location = item.location
            if len(location) >= 2:
                feature_file = location[0]
                feature_line = location[1] if len(location) > 1 else None
        
        # Method 2: Try to get from pytest-bdd scenario attribute
        if hasattr(item, 'scenario'):
            scenario = item.scenario
            if hasattr(scenario, 'feature'):
                feature = scenario.feature
                if hasattr(feature, 'filename'):
                    feature_file = feature.filename
                if hasattr(scenario, 'line_number'):
                    feature_line = scenario.line_number
                if hasattr(scenario, 'name'):
                    feature_statement = scenario.name
        
        # Method 3: Try to get from item's own attributes
        if not feature_file and hasattr(item, 'fspath'):
            feature_file = str(item.fspath)
        
        # Get feature statement from scenario if available
        if not feature_statement:
            feature_statement = scenario_name
        
        # Attach to Allure report (only if Allure is available)
        if HAS_ALLURE and rep.when == 'call':
            # Add feature file and line to Allure
            if feature_file:
                allure.dynamic.label("feature_file", feature_file)
            if feature_line:
                allure.dynamic.label("feature_line", str(feature_line))
            
            # Add test description
            allure.dynamic.description(f"Feature: {feature_file}\nLine: {feature_line}\nScenario: {feature_statement}")
        
        # Print test execution info during call phase
        if rep.when == 'call':
            status = "✓ PASSED" if rep.outcome == 'passed' else "✗ FAILED" if rep.outcome == 'failed' else "⊘ SKIPPED"
            # Show full test case info
            print(f"\n{'='*80}")
            print(f"{status}: {feature_statement}")
            if feature_file:
                feature_file_short = feature_file.split('\\')[-1] if '\\' in feature_file else feature_file.split('/')[-1]
                print(f"Feature: {feature_file_short}")
            if feature_line:
                print(f"Line: {feature_line}")
            print(f"{'='*80}\n")
            
            # Track results
            test_info = {
                'name': feature_statement,
                'file': feature_file or 'Unknown',
                'line': feature_line or 'Unknown',
                'status': status,
                'duration': rep.duration if hasattr(rep, 'duration') else 0,
                'error': str(rep.longrepr) if rep.outcome == 'failed' and hasattr(rep, 'longrepr') else None
            }
            
            if rep.outcome == 'passed':
                test_results['passed'].append(test_info)
            elif rep.outcome == 'failed':
                test_results['failed'].append(test_info)
                # Attach error to Allure (only if available)
                if HAS_ALLURE and allure is not None and rep.longrepr:
                    try:
                        allure.attach(
                            str(rep.longrepr),
                            name="Error Details",
                            attachment_type=allure.attachment_type.TEXT
                        )
                    except Exception:
                        # Do not break tests if Allure attachment fails
                        pass
            else:
                test_results['skipped'].append(test_info)
            
            test_results['total'] += 1
    except Exception as e:
        # Fallback: at least capture basic info
        if rep.when == 'call':
            scenario_name = item.name if hasattr(item, 'name') else str(item)
            status = "PASSED" if rep.outcome == 'passed' else "FAILED" if rep.outcome == 'failed' else "SKIPPED"
            print(f"\n{'='*80}")
            print(f"EXECUTING TEST: {scenario_name}")
            print(f"STATUS: {status}")
            print(f"{'='*80}\n")
    
    return rep


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Called before each test item runs - minimal output for speed"""
    # Removed verbose output for speed - only track results
    pass


@pytest.hookimpl(trylast=True)
def pytest_sessionstart(session):
    """Called after the Session object has been created"""
    test_results['start_time'] = datetime.now()
    print(f"\n{'='*80}")
    print(f"TEST EXECUTION STARTED: {test_results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished"""
    test_results['end_time'] = datetime.now()
    duration = test_results['end_time'] - test_results['start_time'] if test_results['start_time'] else None
    
    # Generate and print report
    print_report()
    
    # Save report to file
    save_report_to_file()
    
    # Automatically generate Allure report
    try:
        from generate_allure_report import generate_allure_report, open_allure_report
        from pathlib import Path
        
        allure_results_dir = Path("reports/allure-results")
        
        # Check if Allure results exist
        if allure_results_dir.exists() and list(allure_results_dir.glob("*.json")):
            print(f"\n{'='*80}")
            print("GENERATING ALLURE REPORT")
            print(f"{'='*80}")
            if generate_allure_report():
                print("[OK] Allure report generated successfully!")
                print(f"   Report location: reports/allure-report/index.html")
                # Try to open the report automatically
                try:
                    open_allure_report()
                    print("   [OK] Report opened in browser")
                except:
                    print("   [INFO] Report generated but could not open automatically")
                    print("   Open manually: reports/allure-report/index.html")
            else:
                print("[WARNING] Allure report generation failed")
                print("   To generate manually, run: python generate_allure_report.py")
            print(f"{'='*80}\n")
        else:
            print(f"\n[WARNING] No Allure results found in {allure_results_dir}")
            print("   Make sure tests are run with --alluredir option")
            print("   Or use: python run_tests_with_allure.py")
            print(f"{'='*80}\n")
    except ImportError as e:
        print(f"\n[WARNING] Could not import Allure report generator: {str(e)}")
        print("   To generate manually, run: python generate_allure_report.py")
        print(f"{'='*80}\n")
    except Exception as e:
        print(f"\n[WARNING] Could not generate Allure report automatically: {str(e)}")
        print("   To generate manually, run: python generate_allure_report.py")
        print(f"{'='*80}\n")


def print_report():
    """Print test execution report to console"""
    print(f"\n{'='*80}")
    print("TEST EXECUTION REPORT")
    print(f"{'='*80}")
    
    if test_results['start_time'] and test_results['end_time']:
        duration = test_results['end_time'] - test_results['start_time']
        print(f"Start Time: {test_results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Time: {test_results['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration}")
        print()
    
    print(f"TOTAL TESTS: {test_results['total']}")
    print(f"PASSED: {len(test_results['passed'])}")
    print(f"FAILED: {len(test_results['failed'])}")
    print(f"SKIPPED: {len(test_results['skipped'])}")
    print()
    
    if test_results['passed']:
        print(f"{'='*80}")
        print("PASSED TESTS:")
        print(f"{'='*80}")
        for i, test in enumerate(test_results['passed'], 1):
            print(f"{i}. {test['name']}")
            print(f"   File: {test['file']}")
            print(f"   Line: {test['line']}")
            print(f"   Duration: {test['duration']:.2f}s")
            print()
    
    if test_results['failed']:
        print(f"{'='*80}")
        print("FAILED TESTS:")
        print(f"{'='*80}")
        for i, test in enumerate(test_results['failed'], 1):
            print(f"{i}. {test['name']}")
            print(f"   File: {test['file']}")
            print(f"   Line: {test['line']}")
            print(f"   Duration: {test['duration']:.2f}s")
            if test['error']:
                error_lines = test['error'].split('\n')[:5]  # First 5 lines of error
                print(f"   Error: {error_lines[0]}")
                for line in error_lines[1:]:
                    print(f"          {line}")
            print()
    
    if test_results['skipped']:
        print(f"{'='*80}")
        print("SKIPPED TESTS:")
        print(f"{'='*80}")
        for i, test in enumerate(test_results['skipped'], 1):
            print(f"{i}. {test['name']}")
            print(f"   File: {test['file']}")
            print(f"   Line: {test['line']}")
            print()
    
    print(f"{'='*80}\n")


def save_report_to_file():
    """Save test report to a file"""
    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    
    report_file = f"reports/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("TEST EXECUTION REPORT\n")
        f.write("="*80 + "\n\n")
        
        if test_results['start_time'] and test_results['end_time']:
            duration = test_results['end_time'] - test_results['start_time']
            f.write(f"Start Time: {test_results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"End Time: {test_results['end_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {duration}\n\n")
        
        f.write(f"TOTAL TESTS: {test_results['total']}\n")
        f.write(f"PASSED: {len(test_results['passed'])}\n")
        f.write(f"FAILED: {len(test_results['failed'])}\n")
        f.write(f"SKIPPED: {len(test_results['skipped'])}\n\n")
        
        if test_results['passed']:
            f.write("="*80 + "\n")
            f.write("PASSED TESTS:\n")
            f.write("="*80 + "\n")
            for i, test in enumerate(test_results['passed'], 1):
                f.write(f"{i}. {test['name']}\n")
                f.write(f"   File: {test['file']}\n")
                f.write(f"   Line: {test['line']}\n")
                f.write(f"   Duration: {test['duration']:.2f}s\n\n")
        
        if test_results['failed']:
            f.write("="*80 + "\n")
            f.write("FAILED TESTS:\n")
            f.write("="*80 + "\n")
            for i, test in enumerate(test_results['failed'], 1):
                f.write(f"{i}. {test['name']}\n")
                f.write(f"   File: {test['file']}\n")
                f.write(f"   Line: {test['line']}\n")
                f.write(f"   Duration: {test['duration']:.2f}s\n")
                if test['error']:
                    f.write(f"   Error:\n{test['error']}\n")
                f.write("\n")
        
        if test_results['skipped']:
            f.write("="*80 + "\n")
            f.write("SKIPPED TESTS:\n")
            f.write("="*80 + "\n")
            for i, test in enumerate(test_results['skipped'], 1):
                f.write(f"{i}. {test['name']}\n")
                f.write(f"   File: {test['file']}\n")
                f.write(f"   Line: {test['line']}\n\n")
    
    print(f"Report saved to: {report_file}")

