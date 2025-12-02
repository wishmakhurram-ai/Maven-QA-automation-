"""
Conftest for tests directory
This ensures step definitions are imported before scenarios are processed
"""
# CRITICAL: Import step definitions here
# This must happen before pytest-bdd processes @scenario decorators
import steps.button_steps  # noqa: F401




