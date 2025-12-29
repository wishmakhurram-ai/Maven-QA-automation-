"""
Pytest test file for MavenAI Admin Portal automation
Uses pytest-bdd to run Gherkin feature files
"""
# CRITICAL: Import step definitions FIRST, before anything else
# This ensures step definitions are registered with pytest-bdd BEFORE scenarios() is called
# Import maven_steps FIRST (other files depend on it)
import steps.maven_steps  # noqa: F401
import steps.button_steps  # noqa: F401
import steps.input_steps  # noqa: F401
import steps.dropdown_steps  # noqa: F401

# Now import scenarios and link the feature file
from pytest_bdd import scenarios

# Link feature file to pytest-bdd
# pytest-bdd will automatically match feature file steps to step definitions in steps/
# Step definitions are already imported in conftest.py, so they should be registered
scenarios('../features/maven_automation.feature')




