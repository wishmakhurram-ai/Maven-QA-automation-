"""
Gherkin step definitions for Ant Design Switch automation using pytest-bdd
pytest-bdd automatically discovers and loads these step definitions
PRIORITY: data-attr-id is used first to determine switch location
"""
from pytest_bdd import given, when, then, parsers
from framework.components.switch_handler import SwitchHandler

# Ant Design Switch demo page URL
SWITCH_PAGE_URL = "https://ant.design/components/switch"


@given('I am on a page with Ant Design Switch components')
def step_on_page_with_switches(context):
    """
    Navigate to a page with Ant Design Switch components
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Navigating to page with switches...")
    context.driver.get(SWITCH_PAGE_URL)
    # Wait for page to load
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    wait = WebDriverWait(context.driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-switch, [role="switch"]')))
    print(f"   >> Page loaded with switches")


@when('I navigate to a page with switches')
def step_navigate_to_page_with_switches(context):
    """
    Navigate to a page with Ant Design Switch components
    
    Args:
        context: Context fixture from conftest.py
    """
    step_on_page_with_switches(context)


@given(parsers.parse('I identify the switch with data-atr-id "{data_attr_id}"'))
def step_identify_switch_by_data_attr(context, data_attr_id):
    """
    Identify a switch by data-atr-id and store it in context
    
    Args:
        context: Context fixture from conftest.py
        data_attr_id: Value of data-atr-id attribute
    """
    print(f"   >> Identifying switch with data-atr-id: '{data_attr_id}'...")
    success = context.switch_handler.identify_and_store(
        data_attr_id,
        identifier_type='data_attr_id'
    )
    assert success, f"Failed to identify switch with data-atr-id '{data_attr_id}'"
    print(f"   >> Switch identified and stored in context")


@given(parsers.parse('I identify the switch with label "{label_text}"'))
@when(parsers.parse('I identify the switch with label "{label_text}"'))
@then(parsers.parse('I identify the switch with label "{label_text}"'))
def step_identify_switch_by_label(context, label_text):
    """
    Identify a switch by label text (semantic matching)
    
    Args:
        context: Context fixture from conftest.py
        label_text: Label text to search for
    """
    print(f"   >> Identifying switch with label: '{label_text}'...")
    success = context.switch_handler.identify_and_store(
        label_text,
        identifier_type='label'
    )
    assert success, f"Failed to identify switch with label '{label_text}'"
    print(f"   >> Switch identified and stored in context")


@when(parsers.parse('I toggle the switch "{identifier}"'))
def step_toggle_switch(context, identifier):
    """
    Toggle a switch (turn ON if OFF, turn OFF if ON)
    
    Args:
        context: Context fixture from conftest.py
        identifier: Switch identifier (label, data-attr-id, or position)
    """
    print(f"   >> Toggling switch: '{identifier}'...")
    success = context.switch_handler.toggle_switch(identifier, identifier_type='auto')
    assert success, f"Failed to toggle switch '{identifier}'"
    print(f"   >> Switch toggled successfully")


@when(parsers.parse('I turn on the switch "{identifier}"'))
def step_turn_on_switch(context, identifier):
    """
    Turn switch ON (idempotent - does nothing if already ON)
    
    Args:
        context: Context fixture from conftest.py
        identifier: Switch identifier (label, data-attr-id, or position)
    """
    print(f"   >> Turning ON switch: '{identifier}'...")
    success = context.switch_handler.turn_on(identifier, identifier_type='auto')
    assert success, f"Switch '{identifier}' should be ON"
    print(f"   >> Switch is ON")


@when(parsers.parse('I turn off the switch "{identifier}"'))
def step_turn_off_switch(context, identifier):
    """
    Turn switch OFF (idempotent - does nothing if already OFF)
    
    Args:
        context: Context fixture from conftest.py
        identifier: Switch identifier (label, data-attr-id, or position)
    """
    print(f"   >> Turning OFF switch: '{identifier}'...")
    success = context.switch_handler.turn_off(identifier, identifier_type='auto')
    assert success, f"Switch '{identifier}' should be OFF"
    print(f"   >> Switch is OFF")


@when('I toggle the first switch')
def step_toggle_first_switch(context):
    """
    Toggle the first switch on the page
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Toggling first switch...")
    success = context.switch_handler.toggle_first_switch()
    assert success, "Failed to toggle first switch"
    print(f"   >> First switch toggled successfully")


@when(parsers.parse('I toggle the switch at position {position:d}'))
def step_toggle_switch_by_position(context, position):
    """
    Toggle switch by position/index (1-based)
    
    Args:
        context: Context fixture from conftest.py
        position: Position of switch (1-based)
    """
    print(f"   >> Toggling switch at position {position}...")
    success = context.switch_handler.toggle_switch_by_index(position)
    assert success, f"Failed to toggle switch at position {position}"
    print(f"   >> Switch at position {position} toggled successfully")


@then(parsers.parse('the switch "{identifier}" should be ON'))
def step_switch_should_be_on(context, identifier):
    """
    Assert that a switch is ON (checked)
    
    Args:
        context: Context fixture from conftest.py
        identifier: Switch identifier
    """
    print(f"   >> Verifying switch '{identifier}' is ON...")
    is_on = context.switch_handler.is_switch_on(identifier, identifier_type='auto')
    assert is_on is not None, f"Switch '{identifier}' not found"
    assert is_on, f"Switch '{identifier}' should be ON but is OFF"
    print(f"   >> Switch '{identifier}' is ON (verified)")


@then(parsers.parse('the switch "{identifier}" should be OFF'))
def step_switch_should_be_off(context, identifier):
    """
    Assert that a switch is OFF (unchecked)
    
    Args:
        context: Context fixture from conftest.py
        identifier: Switch identifier
    """
    print(f"   >> Verifying switch '{identifier}' is OFF...")
    is_off = context.switch_handler.is_switch_off(identifier, identifier_type='auto')
    assert is_off is not None, f"Switch '{identifier}' not found"
    assert is_off, f"Switch '{identifier}' should be OFF but is ON"
    print(f"   >> Switch '{identifier}' is OFF (verified)")


@then(parsers.parse('I should see {count:d} switch(es) on the page'))
def step_should_see_switches_count(context, count):
    """
    Assert that a specific number of switches are visible on the page
    
    Args:
        context: Context fixture from conftest.py
        count: Expected number of switches
    """
    print(f"   >> Verifying {count} switch(es) on the page...")
    summary = context.switch_handler.get_all_switches_summary()
    actual_count = summary['total_count']
    assert actual_count == count, f"Expected {count} switch(es) but found {actual_count}"
    print(f"   >> Found {actual_count} switch(es) (verified)")


@then('I should see a summary of all switches')
def step_should_see_switches_summary(context):
    """
    Print a summary of all switches on the page
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Generating switch summary...")
    context.switch_handler.print_switches_summary()
    print(f"   >> Switch summary displayed")


@then(parsers.parse('the switch "{identifier}" should be disabled'))
def step_switch_should_be_disabled(context, identifier):
    """
    Assert that a switch is disabled
    
    Args:
        context: Context fixture from conftest.py
        identifier: Switch identifier
    """
    print(f"   >> Verifying switch '{identifier}' is disabled...")
    state = context.switch_handler.get_switch_state(identifier, identifier_type='auto')
    assert state is not None, f"Switch '{identifier}' not found"
    assert state['disabled'], f"Switch '{identifier}' should be disabled but is enabled"
    print(f"   >> Switch '{identifier}' is disabled (verified)")


@then(parsers.parse('the switch "{identifier}" should be enabled'))
def step_switch_should_be_enabled(context, identifier):
    """
    Assert that a switch is enabled (not disabled)
    
    Args:
        context: Context fixture from conftest.py
        identifier: Switch identifier
    """
    print(f"   >> Verifying switch '{identifier}' is enabled...")
    state = context.switch_handler.get_switch_state(identifier, identifier_type='auto')
    assert state is not None, f"Switch '{identifier}' not found"
    assert not state['disabled'], f"Switch '{identifier}' should be enabled but is disabled"
    print(f"   >> Switch '{identifier}' is enabled (verified)")


@then(parsers.parse('the switch "{identifier}" should be in loading state'))
def step_switch_should_be_loading(context, identifier):
    """
    Assert that a switch is in loading state
    
    Args:
        context: Context fixture from conftest.py
        identifier: Switch identifier
    """
    print(f"   >> Verifying switch '{identifier}' is loading...")
    state = context.switch_handler.get_switch_state(identifier, identifier_type='auto')
    assert state is not None, f"Switch '{identifier}' not found"
    assert state['loading'], f"Switch '{identifier}' should be loading but is not"
    print(f"   >> Switch '{identifier}' is loading (verified)")


@then(parsers.parse('the switch "{identifier}" should have size "{size}"'))
def step_switch_should_have_size(context, identifier, size):
    """
    Assert that a switch has a specific size
    
    Args:
        context: Context fixture from conftest.py
        identifier: Switch identifier
        size: Expected size ('default' or 'small')
    """
    print(f"   >> Verifying switch '{identifier}' has size '{size}'...")
    state = context.switch_handler.get_switch_state(identifier, identifier_type='auto')
    assert state is not None, f"Switch '{identifier}' not found"
    assert state['size'] == size, f"Switch '{identifier}' should have size '{size}' but has '{state['size']}'"
    print(f"   >> Switch '{identifier}' has size '{size}' (verified)")

