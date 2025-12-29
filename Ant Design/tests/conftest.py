"""
Conftest for tests directory
This ensures step definitions are imported before scenarios are processed
"""
# CRITICAL: Import step definitions here
# This must happen before pytest-bdd processes @scenario decorators
# Import all step definition files to register them with pytest-bdd
# Use pytest_plugins to ensure step definitions are loaded as plugins
pytest_plugins = [
    'steps.maven_steps',
    'steps.button_steps',
    'steps.input_steps',
    'steps.dropdown_steps',
    'steps.menu_steps',
    'steps.pagination_steps',
    'steps.upload_steps',
    'steps.table_steps',
]

