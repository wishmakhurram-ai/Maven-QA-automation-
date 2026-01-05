"""
Test file for Ant Design Checkbox automation
Uses pytest-bdd to run Gherkin scenarios from checkbox_automation.feature
"""
from pytest_bdd import scenarios

# Import step definitions to register them with pytest-bdd
import steps.checkbox_steps  # noqa: F401

# Load all scenarios from the feature file
scenarios('../features/checkbox_automation.feature')

