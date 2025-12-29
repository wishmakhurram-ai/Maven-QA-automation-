"""
Pytest test file for MavenAI Admin Dashboard automation
Uses pytest-bdd to run Gherkin feature files
"""
# CRITICAL: Import step definitions FIRST, before anything else
# This ensures step definitions are registered with pytest-bdd BEFORE scenarios() is called
# Import order matters - button steps FIRST (most specific), then menu steps (less specific)
import steps.button_steps  # noqa: F401 - Import FIRST for button steps (most specific)
import steps.input_steps  # noqa: F401
import steps.dropdown_steps  # noqa: F401
import steps.maven_steps  # noqa: F401
import steps.menu_steps  # noqa: F401 - Import AFTER button steps (less specific)
import steps.pagination_steps  # noqa: F401

# Now import scenarios and link the feature file
from pytest_bdd import scenarios

# Link feature file to pytest-bdd
# pytest-bdd will automatically match feature file steps to step definitions in steps/
scenarios('../features/admin_dashboard.feature')

