"""
Pytest test file for Ant Design Menu automation
Uses pytest-bdd to run Gherkin feature files
"""
# CRITICAL: Import step definitions FIRST, before anything else
# This ensures step definitions are registered with pytest-bdd BEFORE scenarios() is called
import steps.menu_steps  # noqa: F401

# Now import scenarios and link the feature file
from pytest_bdd import scenarios

# Link feature file to pytest-bdd
# pytest-bdd will automatically match feature file steps to step definitions in steps/
scenarios('../features/menu_automation.feature')

