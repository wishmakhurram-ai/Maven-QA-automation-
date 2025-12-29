"""
Pytest test file for custom application component automation (edge cases)
Uses pytest-bdd to run Gherkin feature files
"""
# CRITICAL: Import step definitions FIRST, before anything else
# This ensures step definitions are registered with pytest-bdd BEFORE scenarios() is called
import steps.maven_steps  # noqa: F401
import steps.button_steps  # noqa: F401
import steps.input_steps  # noqa: F401

# Now import scenarios and link the feature file
from pytest_bdd import scenarios

# Link feature file to pytest-bdd
# pytest-bdd will automatically match feature file steps to step definitions in steps/
scenarios('../features/custom_app_automation.feature')

