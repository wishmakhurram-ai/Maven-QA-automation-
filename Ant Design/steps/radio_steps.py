"""
Gherkin step definitions for Ant Design Radio automation using pytest-bdd
pytest-bdd automatically discovers and loads these step definitions
PRIORITY: data-attr-id is used first to determine radio location
"""
from pytest_bdd import given, when, then, parsers
from framework.components.radio_handler import RadioHandler

# Ant Design Radio demo page URL
RADIO_PAGE_URL = "https://ant.design/components/radio"


@given('I am on a page with Ant Design Radio components')
def step_on_page_with_radios(context):
    """
    Navigate to a page with Ant Design Radio components
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Navigating to page with radios...")
    context.driver.get(RADIO_PAGE_URL)
    # Wait for page to load
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    wait = WebDriverWait(context.driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-radio, .ant-radio-wrapper, input[type="radio"]')))
    print(f"   >> Page loaded with radios")


@when('I navigate to a page with radios')
def step_navigate_to_page_with_radios(context):
    """
    Navigate to a page with Ant Design Radio components
    
    Args:
        context: Context fixture from conftest.py
    """
    step_on_page_with_radios(context)


@given(parsers.parse('I identify the radio with data-atr-id "{data_attr_id}"'))
def step_identify_radio_by_data_attr(context, data_attr_id):
    """
    Identify a radio by data-atr-id and store it in context
    
    Args:
        context: Context fixture from conftest.py
        data_attr_id: Value of data-atr-id attribute
    """
    print(f"   >> Identifying radio with data-atr-id: '{data_attr_id}'...")
    success = context.radio_handler.identify_and_store(
        data_attr_id,
        identifier_type='data_attr_id'
    )
    assert success, f"Failed to identify radio with data-atr-id '{data_attr_id}'"
    print(f"   >> Radio identified and stored in context")


@given(parsers.parse('I identify the radio with label "{label_text}"'))
@when(parsers.parse('I identify the radio with label "{label_text}"'))
@then(parsers.parse('I identify the radio with label "{label_text}"'))
def step_identify_radio_by_label(context, label_text):
    """
    Identify a radio by label text (semantic matching)
    
    Args:
        context: Context fixture from conftest.py
        label_text: Label text to search for
    """
    print(f"   >> Identifying radio with label: '{label_text}'...")
    success = context.radio_handler.identify_and_store(
        label_text,
        identifier_type='label'
    )
    assert success, f"Failed to identify radio with label '{label_text}'"
    print(f"   >> Radio identified and stored in context")


@when(parsers.parse('I select "{label_text}" radio option'))
def step_select_radio_by_label(context, label_text):
    """
    Select a radio option by label
    
    Args:
        context: Context fixture from conftest.py
        label_text: Radio label text (e.g., "Male", "Visa")
    """
    print(f"   >> Selecting radio option: '{label_text}'...")
    success = context.radio_handler.select_radio(label_text, identifier_type='auto')
    assert success, f"Failed to select radio option '{label_text}'"
    print(f"   >> Radio option selected successfully")


@when(parsers.parse('I select "{label_text}" radio from "{group_name}" group'))
def step_select_radio_from_group(context, label_text, group_name):
    """
    Select a radio option from a specific group
    
    Args:
        context: Context fixture from conftest.py
        label_text: Radio label text (e.g., "Visa")
        group_name: Radio group name (e.g., "Payment Method")
    """
    print(f"   >> Selecting radio '{label_text}' from group '{group_name}'...")
    success = context.radio_handler.select_radio(label_text, group_name=group_name, identifier_type='auto')
    assert success, f"Failed to select radio '{label_text}' from group '{group_name}'"
    print(f"   >> Radio selected successfully")


@when(parsers.parse('I select the radio at position {position:d}'))
def step_select_radio_by_position(context, position):
    """
    Select radio by position/index (1-based)
    
    Args:
        context: Context fixture from conftest.py
        position: Position of radio (1-based)
    """
    print(f"   >> Selecting radio at position {position}...")
    success = context.radio_handler.select_radio(str(position), identifier_type='position')
    assert success, f"Failed to select radio at position {position}"
    print(f"   >> Radio at position {position} selected successfully")


@then(parsers.parse('"{label_text}" radio option should be selected'))
def step_radio_should_be_selected(context, label_text):
    """
    Assert that a radio option is selected
    
    Args:
        context: Context fixture from conftest.py
        label_text: Radio label text
    """
    print(f"   >> Verifying radio '{label_text}' is selected...")
    is_selected = context.radio_handler.is_radio_selected(label_text, identifier_type='auto')
    assert is_selected is not None, f"Radio '{label_text}' not found"
    assert is_selected, f"Radio '{label_text}' should be selected but is not"
    print(f"   >> Radio '{label_text}' is selected (verified)")


@then(parsers.parse('"{group_name}" group should have "{label_text}" selected'))
def step_group_should_have_selected(context, group_name, label_text):
    """
    Assert that a radio group has a specific option selected
    
    Args:
        context: Context fixture from conftest.py
        group_name: Radio group name
        label_text: Selected option label
    """
    print(f"   >> Verifying group '{group_name}' has '{label_text}' selected...")
    group_info = context.radio_handler.get_group_info(group_name)
    assert group_info is not None, f"Radio group '{group_name}' not found"
    assert group_info['selected_option'] is not None, f"Radio group '{group_name}' has no option selected"
    assert label_text.lower() in group_info['selected_option'].lower(), \
        f"Group '{group_name}' should have '{label_text}' selected but has '{group_info['selected_option']}'"
    print(f"   >> Group '{group_name}' has '{label_text}' selected (verified)")


@then(parsers.parse('only one radio option should be selected in "{group_name}" group'))
def step_only_one_selected_in_group(context, group_name):
    """
    Assert that only one radio option is selected in a group
    
    Args:
        context: Context fixture from conftest.py
        group_name: Radio group name
    """
    print(f"   >> Verifying only one option is selected in group '{group_name}'...")
    group_info = context.radio_handler.get_group_info(group_name)
    assert group_info is not None, f"Radio group '{group_name}' not found"
    
    selected_count = sum(1 for radio in group_info['radios'] if radio.get('selected'))
    assert selected_count == 1, \
        f"Group '{group_name}' should have exactly one option selected but has {selected_count}"
    print(f"   >> Group '{group_name}' has exactly one option selected (verified)")


@then(parsers.parse('I should see {count:d} radio(s) on the page'))
def step_should_see_radios_count(context, count):
    """
    Assert that a specific number of radios are visible on the page
    
    Args:
        context: Context fixture from conftest.py
        count: Expected number of radios
    """
    print(f"   >> Verifying {count} radio(s) on the page...")
    summary = context.radio_handler.get_all_radios_summary()
    actual_count = summary['total_count']
    assert actual_count == count, f"Expected {count} radio(s) but found {actual_count}"
    print(f"   >> Found {actual_count} radio(s) (verified)")


@then('I should see a summary of all radios')
def step_should_see_radios_summary(context):
    """
    Print a summary of all radios on the page
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Generating radio summary...")
    context.radio_handler.print_radios_summary()
    print(f"   >> Radio summary displayed")


@then(parsers.parse('the radio "{identifier}" should be disabled'))
def step_radio_should_be_disabled(context, identifier):
    """
    Assert that a radio is disabled
    
    Args:
        context: Context fixture from conftest.py
        identifier: Radio identifier
    """
    print(f"   >> Verifying radio '{identifier}' is disabled...")
    state = context.radio_handler.get_radio_state(identifier, identifier_type='auto')
    assert state is not None, f"Radio '{identifier}' not found"
    assert state['disabled'], f"Radio '{identifier}' should be disabled but is enabled"
    print(f"   >> Radio '{identifier}' is disabled (verified)")


@then(parsers.parse('the radio "{identifier}" should be enabled'))
def step_radio_should_be_enabled(context, identifier):
    """
    Assert that a radio is enabled (not disabled)
    
    Args:
        context: Context fixture from conftest.py
        identifier: Radio identifier
    """
    print(f"   >> Verifying radio '{identifier}' is enabled...")
    state = context.radio_handler.get_radio_state(identifier, identifier_type='auto')
    assert state is not None, f"Radio '{identifier}' not found"
    assert not state['disabled'], f"Radio '{identifier}' should be enabled but is disabled"
    print(f"   >> Radio '{identifier}' is enabled (verified)")


@then(parsers.parse('"{group_name}" group should have {count:d} option(s)'))
def step_group_should_have_options_count(context, group_name, count):
    """
    Assert that a radio group has a specific number of options
    
    Args:
        context: Context fixture from conftest.py
        group_name: Radio group name
        count: Expected number of options
    """
    print(f"   >> Verifying group '{group_name}' has {count} option(s)...")
    group_info = context.radio_handler.get_group_info(group_name)
    assert group_info is not None, f"Radio group '{group_name}' not found"
    actual_count = group_info['total_options']
    assert actual_count == count, f"Group '{group_name}' should have {count} option(s) but has {actual_count}"
    print(f"   >> Group '{group_name}' has {actual_count} option(s) (verified)")


@then(parsers.parse('"{label_text}" radio option should not be selected'))
def step_radio_should_not_be_selected(context, label_text):
    """
    Assert that a radio option is not selected
    
    Args:
        context: Context fixture from conftest.py
        label_text: Radio label text
    """
    print(f"   >> Verifying radio '{label_text}' is not selected...")
    is_selected = context.radio_handler.is_radio_selected(label_text, identifier_type='auto')
    assert is_selected is not None, f"Radio '{label_text}' not found"
    assert not is_selected, f"Radio '{label_text}' should not be selected but is selected"
    print(f"   >> Radio '{label_text}' is not selected (verified)")


@then(parsers.parse('I should see at least {count:d} radio(s) on the page'))
def step_should_see_at_least_radios_count(context, count):
    """
    Assert that at least a specific number of radios are visible on the page
    
    Args:
        context: Context fixture from conftest.py
        count: Minimum expected number of radios
    """
    print(f"   >> Verifying at least {count} radio(s) on the page...")
    summary = context.radio_handler.get_all_radios_summary()
    actual_count = summary['total_count']
    assert actual_count >= count, f"Expected at least {count} radio(s) but found {actual_count}"
    print(f"   >> Found {actual_count} radio(s) (verified)")

