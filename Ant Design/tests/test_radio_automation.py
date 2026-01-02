"""
Test file for Ant Design Radio automation
Uses pytest-bdd to run Gherkin scenarios from radio_automation.feature
"""
from pytest_bdd import scenarios

# Import step definitions to register them with pytest-bdd
import steps.radio_steps  # noqa: F401

# Load all scenarios from the feature file
scenarios('../features/radio_automation.feature')

