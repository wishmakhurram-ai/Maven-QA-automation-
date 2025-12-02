"""
Pytest configuration and fixtures for pytest-bdd
This file is automatically discovered by pytest
"""
import pytest
from framework.components.button_handler import ButtonHandler
from framework.components.input_handler import InputHandler
from framework.components.dropdown_handler import DropdownHandler
from framework.components.pagination_handler import PaginationHandler
from framework.utils.driver_setup import DriverSetup
from framework.context.element_context import ElementContext

# CRITICAL: Import step definitions at module level
# This ensures steps are registered BEFORE pytest-bdd processes scenarios
# pytest-bdd will automatically discover steps from steps/ directory via bdd_step_paths in pytest.ini
import steps.button_steps  # noqa: F401
import steps.input_steps  # noqa: F401
import steps.dropdown_steps  # noqa: F401
import steps.pagination_steps  # noqa: F401

# Alternative: Use pytest_plugins to ensure steps are loaded
pytest_plugins = ['steps.button_steps', 'steps.input_steps', 'steps.dropdown_steps', 'steps.pagination_steps']


@pytest.fixture(scope="function")
def driver():
    """
    Create and yield a WebDriver instance
    Automatically closes after each test
    """
    driver = DriverSetup.get_chrome_driver(headless=False, maximize=True)
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def element_context():
    """
    Create an ElementContext instance for storing element information
    """
    return ElementContext()


@pytest.fixture(scope="function")
def button_handler(driver, element_context):
    """
    Create a ButtonHandler instance using the driver fixture
    Passes element_context for context-driven interactions
    """
    return ButtonHandler(driver, context=element_context)


@pytest.fixture(scope="function")
def input_handler(driver, element_context):
    """
    Create an InputHandler instance using the driver fixture
    Passes element_context for context-driven interactions
    """
    return InputHandler(driver, context=element_context)


@pytest.fixture(scope="function")
def dropdown_handler(driver, element_context):
    """
    Create a DropdownHandler instance using the driver fixture
    Passes element_context for context-driven interactions
    """
    return DropdownHandler(driver, context=element_context)


@pytest.fixture(scope="function")
def pagination_handler(driver, element_context):
    """
    Create a PaginationHandler instance using the driver fixture
    Passes element_context for context-driven interactions
    """
    return PaginationHandler(driver, context=element_context)


@pytest.fixture(scope="function")
def context(driver, button_handler, input_handler, dropdown_handler, pagination_handler, element_context):
    """
    Create a context object similar to behave's context
    This allows step definitions to access driver, handlers, and element_context
    """
    class Context:
        def __init__(self):
            self.driver = driver
            self.button_handler = button_handler
            self.input_handler = input_handler
            self.dropdown_handler = dropdown_handler
            self.pagination_handler = pagination_handler
            self.element_context = element_context  # ElementContext for storing elements
            self.button_clicked = None
            self.last_clicked_button_info = None
    
    return Context()


# Hook to show step execution with feature file line numbers
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_bdd_before_step(request, feature, scenario, step, step_func):
    """
    Hook executed before each step
    Shows which feature file line is being executed
    """
    # Get step type (Given/When/Then/And)
    step_type = step.type.name if hasattr(step.type, 'name') else str(step.type)
    
    # Print step information
    print(f"\n{'='*70}")
    print(f">>> EXECUTING STEP: {step_type.upper()}")
    print(f"   Feature File: {feature.filename}")
    print(f"   Scenario: {scenario.name} (Line {scenario.line_number})")
    print(f"   Step Line: {step.line_number}")
    print(f"   Step Text: {step.name}")
    print(f"{'='*70}")
    
    outcome = yield
    
    # After step execution
    try:
        result = outcome.get_result()
        if hasattr(result, 'excinfo') and result.excinfo is None:
            print(f">>> STEP PASSED: {step.name}")
        elif hasattr(result, 'excinfo') and result.excinfo:
            print(f">>> STEP FAILED: {step.name}")
            if result.excinfo:
                print(f"   Error: {result.excinfo[1]}")
        else:
            # Step completed successfully
            print(f">>> STEP PASSED: {step.name}")
    except Exception:
        # If we can't determine status, assume it passed if we got here
        print(f">>> STEP PASSED: {step.name}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture and display test execution details
    """
    outcome = yield
    rep = outcome.get_result()
    
    # Show scenario summary
    if rep.when == "call" and hasattr(item, 'scenario'):
        scenario = item.scenario
        feature = scenario.feature
        
        if rep.outcome == "passed":
            print(f"\n{'='*70}")
            print(f">>> SCENARIO PASSED: {scenario.name}")
            print(f"   Feature: {feature.filename}")
            print(f"   Scenario Line: {scenario.line_number}")
            print(f"{'='*70}\n")
        elif rep.outcome == "failed":
            print(f"\n{'='*70}")
            print(f">>> SCENARIO FAILED: {scenario.name}")
            print(f"   Feature: {feature.filename}")
            print(f"   Scenario Line: {scenario.line_number}")
            print(f"{'='*70}\n")

