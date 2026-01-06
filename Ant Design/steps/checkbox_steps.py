"""
Gherkin step definitions for Ant Design Checkbox automation using pytest-bdd
pytest-bdd automatically discovers and loads these step definitions
PRIORITY: data-attr-id is used first to determine checkbox location
"""
from pytest_bdd import given, when, then, parsers
from framework.components.checkbox_handler import CheckboxHandler

# Ant Design Checkbox demo page URL
CHECKBOX_PAGE_URL = "https://ant.design/components/checkbox"


@given('I am on a page with Ant Design Checkbox components')
def step_on_page_with_checkboxes(context):
    """
    Navigate to a page with Ant Design Checkbox components
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Navigating to page with checkboxes...")
    context.driver.get(CHECKBOX_PAGE_URL)
    # Wait for page to load
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    wait = WebDriverWait(context.driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-checkbox, .ant-checkbox-wrapper, input[type="checkbox"]')))
    print(f"   >> Page loaded with checkboxes")


@when('I navigate to a page with checkboxes')
def step_navigate_to_page_with_checkboxes(context):
    """
    Navigate to a page with Ant Design Checkbox components
    
    Args:
        context: Context fixture from conftest.py
    """
    step_on_page_with_checkboxes(context)


@given(parsers.parse('I identify the checkbox with data-atr-id "{data_attr_id}"'))
def step_identify_checkbox_by_data_attr(context, data_attr_id):
    """
    Identify a checkbox by data-atr-id and store it in context
    
    Args:
        context: Context fixture from conftest.py
        data_attr_id: Value of data-atr-id attribute
    """
    print(f"   >> Identifying checkbox with data-atr-id: '{data_attr_id}'...")
    success = context.checkbox_handler.identify_and_store(
        data_attr_id,
        identifier_type='data_attr_id'
    )
    assert success, f"Failed to identify checkbox with data-atr-id '{data_attr_id}'"
    print(f"   >> Checkbox identified and stored in context")


@given(parsers.parse('I identify the checkbox with label "{label_text}"'))
@when(parsers.parse('I identify the checkbox with label "{label_text}"'))
@then(parsers.parse('I identify the checkbox with label "{label_text}"'))
def step_identify_checkbox_by_label(context, label_text):
    """
    Identify a checkbox by label text (semantic matching)
    
    Args:
        context: Context fixture from conftest.py
        label_text: Label text to search for
    """
    print(f"   >> Identifying checkbox with label: '{label_text}'...")
    success = context.checkbox_handler.identify_and_store(
        label_text,
        identifier_type='label'
    )
    assert success, f"Failed to identify checkbox with label '{label_text}'"
    print(f"   >> Checkbox identified and stored in context")


@when(parsers.parse('I check "{label_text}" checkbox'))
def step_check_checkbox_by_label(context, label_text):
    """
    Check a checkbox by label
    
    Args:
        context: Context fixture from conftest.py
        label_text: Checkbox label text (e.g., "Accept Terms", "Email Notifications")
    """
    print(f"   >> Checking checkbox: '{label_text}'...")
    success = context.checkbox_handler.check_checkbox(label_text, identifier_type='auto')
    assert success, f"Failed to check checkbox '{label_text}'"
    print(f"   >> Checkbox checked successfully")


@when(parsers.parse('I uncheck "{label_text}" checkbox'))
def step_uncheck_checkbox_by_label(context, label_text):
    """
    Uncheck a checkbox by label
    
    Args:
        context: Context fixture from conftest.py
        label_text: Checkbox label text
    """
    print(f"   >> Unchecking checkbox: '{label_text}'...")
    success = context.checkbox_handler.uncheck_checkbox(label_text, identifier_type='auto')
    assert success, f"Failed to uncheck checkbox '{label_text}'"
    print(f"   >> Checkbox unchecked successfully")


@when(parsers.parse('I check "{label_text}" from "{group_name}" checkbox group'))
def step_check_checkbox_from_group(context, label_text, group_name):
    """
    Check a checkbox from a specific group
    
    Args:
        context: Context fixture from conftest.py
        label_text: Checkbox label text (e.g., "Option A")
        group_name: Checkbox group name (e.g., "Preferences")
    """
    print(f"   >> Checking checkbox '{label_text}' from group '{group_name}'...")
    success = context.checkbox_handler.check_checkbox(label_text, group_name=group_name, identifier_type='auto')
    assert success, f"Failed to check checkbox '{label_text}' from group '{group_name}'"
    print(f"   >> Checkbox checked successfully")


@when(parsers.parse('I uncheck "{label_text}" from "{group_name}" checkbox group'))
def step_uncheck_checkbox_from_group(context, label_text, group_name):
    """
    Uncheck a checkbox from a specific group
    
    Args:
        context: Context fixture from conftest.py
        label_text: Checkbox label text
        group_name: Checkbox group name
    """
    print(f"   >> Unchecking checkbox '{label_text}' from group '{group_name}'...")
    success = context.checkbox_handler.uncheck_checkbox(label_text, group_name=group_name, identifier_type='auto')
    assert success, f"Failed to uncheck checkbox '{label_text}' from group '{group_name}'"
    print(f"   >> Checkbox unchecked successfully")


@when(parsers.parse('I toggle "{label_text}" checkbox'))
def step_toggle_checkbox_by_label(context, label_text):
    """
    Toggle a checkbox by label (check if unchecked, uncheck if checked)
    
    Args:
        context: Context fixture from conftest.py
        label_text: Checkbox label text
    """
    print(f"   >> Toggling checkbox: '{label_text}'...")
    success = context.checkbox_handler.toggle_checkbox(label_text, identifier_type='auto')
    assert success, f"Failed to toggle checkbox '{label_text}'"
    print(f"   >> Checkbox toggled successfully")


@when(parsers.parse('I check the checkbox at position {position:d}'))
def step_check_checkbox_by_position(context, position):
    """
    Check checkbox by position/index (1-based)
    
    Args:
        context: Context fixture from conftest.py
        position: Position of checkbox (1-based)
    """
    print(f"   >> Checking checkbox at position {position}...")
    success = context.checkbox_handler.check_checkbox(str(position), identifier_type='position')
    assert success, f"Failed to check checkbox at position {position}"
    print(f"   >> Checkbox at position {position} checked successfully")


@then(parsers.parse('"{label_text}" checkbox should be checked'))
def step_checkbox_should_be_checked(context, label_text):
    """
    Assert that a checkbox is checked
    
    Args:
        context: Context fixture from conftest.py
        label_text: Checkbox label text
    """
    print(f"   >> Verifying checkbox '{label_text}' is checked...")
    is_checked = context.checkbox_handler.is_checkbox_checked(label_text, identifier_type='auto')
    assert is_checked is not None, f"Checkbox '{label_text}' not found"
    assert is_checked, f"Checkbox '{label_text}' should be checked but is not"
    print(f"   >> Checkbox '{label_text}' is checked (verified)")


@then(parsers.parse('"{label_text}" checkbox should be unchecked'))
def step_checkbox_should_be_unchecked(context, label_text):
    """
    Assert that a checkbox is unchecked
    
    Args:
        context: Context fixture from conftest.py
        label_text: Checkbox label text
    """
    print(f"   >> Verifying checkbox '{label_text}' is unchecked...")
    is_checked = context.checkbox_handler.is_checkbox_checked(label_text, identifier_type='auto')
    assert is_checked is not None, f"Checkbox '{label_text}' not found"
    assert not is_checked, f"Checkbox '{label_text}' should be unchecked but is checked"
    print(f"   >> Checkbox '{label_text}' is unchecked (verified)")


@then(parsers.parse('"{label_text}" checkbox should be indeterminate'))
def step_checkbox_should_be_indeterminate(context, label_text):
    """
    Assert that a checkbox is in indeterminate state
    
    Args:
        context: Context fixture from conftest.py
        label_text: Checkbox label text
    """
    print(f"   >> Verifying checkbox '{label_text}' is indeterminate...")
    is_indeterminate = context.checkbox_handler.is_checkbox_indeterminate(label_text, identifier_type='auto')
    assert is_indeterminate is not None, f"Checkbox '{label_text}' not found"
    assert is_indeterminate, f"Checkbox '{label_text}' should be indeterminate but is not"
    print(f"   >> Checkbox '{label_text}' is indeterminate (verified)")


@then(parsers.parse('"{group_name}" group should have {count:d} option(s) checked'))
def step_group_should_have_options_checked(context, group_name, count):
    """
    Assert that a checkbox group has a specific number of options checked
    
    Args:
        context: Context fixture from conftest.py
        group_name: Checkbox group name
        count: Expected number of checked options
    """
    print(f"   >> Verifying group '{group_name}' has {count} option(s) checked...")
    group_info = context.checkbox_handler.get_group_info(group_name)
    assert group_info is not None, f"Checkbox group '{group_name}' not found"
    actual_count = group_info['checked_count']
    assert actual_count == count, f"Group '{group_name}' should have {count} option(s) checked but has {actual_count}"
    print(f"   >> Group '{group_name}' has {actual_count} option(s) checked (verified)")


@then(parsers.parse('"{group_name}" group should have {count:d} option(s)'))
def step_group_should_have_options_count(context, group_name, count):
    """
    Assert that a checkbox group has a specific number of options
    
    Args:
        context: Context fixture from conftest.py
        group_name: Checkbox group name
        count: Expected number of options
    """
    print(f"   >> Verifying group '{group_name}' has {count} option(s)...")
    group_info = context.checkbox_handler.get_group_info(group_name)
    assert group_info is not None, f"Checkbox group '{group_name}' not found"
    actual_count = group_info['total_options']
    assert actual_count == count, f"Group '{group_name}' should have {count} option(s) but has {actual_count}"
    print(f"   >> Group '{group_name}' has {actual_count} option(s) (verified)")


@then(parsers.parse('I should see {count:d} checkbox(es) on the page'))
def step_should_see_checkboxes_count(context, count):
    """
    Assert that a specific number of checkboxes are visible on the page
    
    Args:
        context: Context fixture from conftest.py
        count: Expected number of checkboxes
    """
    print(f"   >> Verifying {count} checkbox(es) on the page...")
    summary = context.checkbox_handler.get_all_checkboxes_summary()
    actual_count = summary['total_count']
    assert actual_count == count, f"Expected {count} checkbox(es) but found {actual_count}"
    print(f"   >> Found {actual_count} checkbox(es) (verified)")


@then('I should see a summary of all checkboxes')
def step_should_see_checkboxes_summary(context):
    """
    Print a summary of all checkboxes on the page
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Generating checkbox summary...")
    context.checkbox_handler.print_checkboxes_summary()
    print(f"   >> Checkbox summary displayed")


@then(parsers.parse('the checkbox "{identifier}" should be disabled'))
def step_checkbox_should_be_disabled(context, identifier):
    """
    Assert that a checkbox is disabled
    
    Args:
        context: Context fixture from conftest.py
        identifier: Checkbox identifier
    """
    print(f"   >> Verifying checkbox '{identifier}' is disabled...")
    state = context.checkbox_handler.get_checkbox_state(identifier, identifier_type='auto')
    assert state is not None, f"Checkbox '{identifier}' not found"
    assert state['disabled'], f"Checkbox '{identifier}' should be disabled but is enabled"
    print(f"   >> Checkbox '{identifier}' is disabled (verified)")


@then(parsers.parse('the checkbox "{identifier}" should be enabled'))
def step_checkbox_should_be_enabled(context, identifier):
    """
    Assert that a checkbox is enabled (not disabled)
    
    Args:
        context: Context fixture from conftest.py
        identifier: Checkbox identifier
    """
    print(f"   >> Verifying checkbox '{identifier}' is enabled...")
    state = context.checkbox_handler.get_checkbox_state(identifier, identifier_type='auto')
    assert state is not None, f"Checkbox '{identifier}' not found"
    assert not state['disabled'], f"Checkbox '{identifier}' should be enabled but is disabled"
    print(f"   >> Checkbox '{identifier}' is enabled (verified)")


@then(parsers.parse('I should see at least {count:d} checkbox(es) on the page'))
def step_should_see_at_least_checkboxes_count(context, count):
    """
    Assert that at least a specific number of checkboxes are visible on the page
    
    Args:
        context: Context fixture from conftest.py
        count: Minimum expected number of checkboxes
    """
    print(f"   >> Verifying at least {count} checkbox(es) on the page...")
    summary = context.checkbox_handler.get_all_checkboxes_summary()
    actual_count = summary['total_count']
    assert actual_count >= count, f"Expected at least {count} checkbox(es) but found {actual_count}"
    print(f"   >> Found {actual_count} checkbox(es) (verified)")


@then(parsers.parse('"{label_text}" checkbox should have "Check All" behavior'))
def step_checkbox_should_have_check_all(context, label_text):
    """
    Assert that a checkbox has "Check All" behavior
    
    Args:
        context: Context fixture from conftest.py
        label_text: Checkbox label text
    """
    print(f"   >> Verifying checkbox '{label_text}' has 'Check All' behavior...")
    state = context.checkbox_handler.get_checkbox_state(label_text, identifier_type='auto')
    assert state is not None, f"Checkbox '{label_text}' not found"
    assert state.get('has_check_all', False), f"Checkbox '{label_text}' should have 'Check All' behavior but does not"
    print(f"   >> Checkbox '{label_text}' has 'Check All' behavior (verified)")

