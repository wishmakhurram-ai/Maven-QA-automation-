"""
Test file for Ant Design Switch automation
Uses pytest-bdd to run Gherkin scenarios from switch_automation.feature
"""
from pytest_bdd import scenarios

# Import step definitions to register them with pytest-bdd
import steps.switch_steps  # noqa: F401

# Load all scenarios from the feature file
scenarios('../features/switch_automation.feature')




