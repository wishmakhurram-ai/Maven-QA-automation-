"""
Test file that links pagination feature file to pytest-bdd step definitions
Step definitions are automatically matched from steps/pagination_steps.py
"""
# CRITICAL: Import step definitions FIRST, before anything else
# This ensures step definitions are registered with pytest-bdd BEFORE scenarios() is called
import steps.pagination_steps  # noqa: F401

# Now import scenarios and link the feature file
from pytest_bdd import scenarios

# Link feature file to pytest-bdd
# pytest-bdd will automatically match feature file steps to step definitions in steps/pagination_steps.py
scenarios('../features/pagination_automation.feature')

