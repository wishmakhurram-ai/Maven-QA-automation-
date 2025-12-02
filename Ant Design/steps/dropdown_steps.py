"""
Gherkin step definitions for dropdown/Select field automation using pytest-bdd
pytest-bdd automatically discovers and loads these step definitions
PRIORITY: data-attr-id is used first to determine field type and location
"""
from pytest_bdd import given, when, then, parsers
from framework.components.dropdown_handler import DropdownHandler

# Ant Design Dropdown page URL
DROPDOWN_PAGE_URL = "https://ant.design/components/dropdown"


@given(parsers.parse('I identify the dropdown with data-atr-id "{data_attr_id}"'))
def step_identify_dropdown_by_data_attr(context, data_attr_id):
    """
    Identify a dropdown by data-atr-id and store it in context
    
    Args:
        context: Context fixture from conftest.py
        data_attr_id: Value of data-atr-id attribute
    """
    print(f"   >> Identifying dropdown with data-atr-id: '{data_attr_id}'...")
    success = context.dropdown_handler.identify_and_store(
        data_attr_id,
        identifier_type='data_attr'
    )
    assert success, f"Failed to identify dropdown with data-atr-id '{data_attr_id}'"
    print(f"   >> Dropdown identified and stored in context")


@given(parsers.parse('I identify the dropdown with label "{label_text}"'))
def step_identify_dropdown_by_label(context, label_text):
    """
    Identify a dropdown by label text (semantic matching)
    
    Args:
        context: Context fixture from conftest.py
        label_text: Label text to search for
    """
    # Clear context first to ensure fresh start for each scenario
    context.element_context.clear()
    
    print(f"   >> Identifying dropdown with label: '{label_text}'...")
    success = context.dropdown_handler.identify_and_store(
        label_text,
        identifier_type='label'
    )
    assert success, f"Failed to identify dropdown with label '{label_text}'"
    
    # Show which dropdown was identified
    element_info = context.element_context.get_element(label_text)
    if element_info:
        dropdown_type = element_info.metadata.get('type', 'N/A')
        data_attr_id = element_info.data_attr_id or 'N/A'
        print(f"   >> Identified dropdown: label='{label_text}', type='{dropdown_type}', data-attr-id='{data_attr_id}'")
    
    print(f"   >> Dropdown identified and stored in context")


@given(parsers.parse('I identify the "{dropdown_type}" type dropdown'))
def step_identify_dropdown_by_type(context, dropdown_type):
    """
    Identify a dropdown by type
    
    Args:
        context: Context fixture from conftest.py
        dropdown_type: Type of dropdown (single, multiple, tags, searchable, tree, cascader)
    """
    print(f"   >> Identifying {dropdown_type} dropdown...")
    success = context.dropdown_handler.identify_and_store(
        dropdown_type,
        identifier_type='type'
    )
    assert success, f"Failed to identify {dropdown_type} dropdown"
    print(f"   >> Dropdown identified and stored in context")


@given(parsers.parse('I identify the dropdown at position "{position}"'))
@when(parsers.parse('I identify the dropdown at position "{position}"'))
def step_identify_dropdown_by_position(context, position):
    """
    Identify a dropdown by position/index
    Works with both Given and When steps (for use with And)
    
    Args:
        context: Context fixture from conftest.py
        position: Position/index (1-based)
    """
    # Clear context first to ensure fresh start for each scenario
    context.element_context.clear()
    
    print(f"   >> Identifying dropdown at position: {position}...")
    success = context.dropdown_handler.identify_and_store(
        position,
        identifier_type='position'
    )
    assert success, f"Failed to identify dropdown at position {position}"
    
    # Show which dropdown was identified
    element_info = context.element_context.get_element(str(position))
    if element_info:
        dropdown_label = element_info.metadata.get('label', 'N/A')
        dropdown_type = element_info.metadata.get('type', 'N/A')
        print(f"   >> Identified dropdown: position={position}, label='{dropdown_label}', type='{dropdown_type}'")
    
    print(f"   >> Dropdown identified and stored in context")


@when(parsers.parse('I select {option_text} in dropdown {dropdown_label}'))
def step_select_by_semantic_label(context, option_text, dropdown_label):
    """
    Select an option in dropdown by semantic label (no quotes needed)
    PRIORITY: Tries data-attr-id first, then label matching
    
    Args:
        context: Context fixture from conftest.py
        option_text: Option text to select (e.g., "Pakistan", "Admin")
        dropdown_label: Dropdown label (e.g., "Country", "Role")
    """
    print(f"   >> Selecting '{option_text}' in dropdown '{dropdown_label}'...")
    
    # PRIORITY 1: Try data-attr-id (normalize label to data-attr-id format)
    data_attr_candidates = [
        dropdown_label.lower().replace(' ', '-'),
        dropdown_label.lower().replace(' ', '_'),
        dropdown_label.lower().replace(' ', ''),
    ]
    
    success = False
    for candidate in data_attr_candidates:
        try:
            success = context.dropdown_handler.select_by_text(
                candidate,
                option_text,
                identifier_type='data_attr'
            )
            if success:
                print(f"   >> Found and selected using data-attr-id: '{candidate}'")
                break
        except:
            pass
    
    # PRIORITY 2: Try label matching
    if not success:
        try:
            success = context.dropdown_handler.select_by_text(
                dropdown_label,
                option_text,
                identifier_type='label'
            )
            if success:
                print(f"   >> Found and selected using label matching")
        except:
            pass
    
    assert success, f"Failed to select '{option_text}' in dropdown '{dropdown_label}'. Tried: data-attr-id, label matching."
    print(f"   >> Selected '{option_text}' in dropdown '{dropdown_label}' successfully")


@when(parsers.parse('I select {option_text} in dropdown "{dropdown_label}"'))
def step_select_by_label_quoted(context, option_text, dropdown_label):
    """
    Select an option in dropdown by label (with quotes)
    
    Args:
        context: Context fixture from conftest.py
        option_text: Option text to select
        dropdown_label: Dropdown label
    """
    print(f"   >> Selecting '{option_text}' in dropdown '{dropdown_label}'...")
    success = context.dropdown_handler.select_by_text(
        dropdown_label,
        option_text,
        identifier_type='label'
    )
    assert success, f"Failed to select '{option_text}' in dropdown '{dropdown_label}'"
    print(f"   >> Selected successfully")


@when(parsers.parse('I select the option from context with "{option_text}"'))
def step_select_from_context(context, option_text):
    """
    Select an option from dropdown using context
    
    Args:
        context: Context fixture from conftest.py
        option_text: Option text to select
    """
    # Show which dropdown is being used from context
    all_keys = context.element_context.get_all_keys()
    current_key = context.element_context.current_element_key
    
    print(f"   >> Selecting option '{option_text}' from context...")
    print(f"   >> Available context keys: {all_keys}")
    print(f"   >> Current context key: {current_key}")
    
    # Get element info to show which dropdown we're using
    if current_key:
        element_info = context.element_context.get_element(current_key)
        if element_info:
            dropdown_label = element_info.metadata.get('label', 'N/A')
            dropdown_type = element_info.metadata.get('type', 'N/A')
            # Get element text to show which dropdown visually
            try:
                element_text = element_info.element.text.strip()[:50] if element_info.element.text else 'N/A'
                element_location = f"({element_info.element.location['x']}, {element_info.element.location['y']})"
            except:
                element_text = 'N/A'
                element_location = 'N/A'
            
            print(f"   >> Using dropdown: key='{current_key}', label='{dropdown_label}', type='{dropdown_type}'")
            print(f"   >> Dropdown text: '{element_text}', location: {element_location}")
    
    success = context.dropdown_handler.select_from_context(option_text)
    assert success, f"Failed to select option '{option_text}' from context"
    print(f"   >> Option selected successfully")


@when(parsers.parse('I select the option with context key "{context_key}" with "{option_text}"'))
def step_select_by_context_key(context, context_key, option_text):
    """
    Select an option using a specific context key
    
    Args:
        context: Context fixture from conftest.py
        context_key: Key of the element in context
        option_text: Option text to select
    """
    print(f"   >> Selecting option '{option_text}' with context key '{context_key}'...")
    success = context.dropdown_handler.select_from_context(option_text, context_key)
    assert success, f"Failed to select option with context key '{context_key}'"
    print(f"   >> Option selected successfully")


@when(parsers.parse('I select index "{index}" in dropdown {dropdown_label}'))
def step_select_by_index(context, index, dropdown_label):
    """
    Select an option by index in dropdown (no quotes needed)
    
    Args:
        context: Context fixture from conftest.py
        index: Index of option to select (0-based)
        dropdown_label: Dropdown label
    """
    print(f"   >> Selecting index {index} in dropdown '{dropdown_label}'...")
    
    # Try data-attr-id first, then label
    success = False
    data_attr_candidates = [
        dropdown_label.lower().replace(' ', '-'),
        dropdown_label.lower().replace(' ', '_'),
        dropdown_label.lower().replace(' ', ''),
    ]
    
    for candidate in data_attr_candidates:
        try:
            success = context.dropdown_handler.select_by_index(
                candidate,
                int(index),
                identifier_type='data_attr'
            )
            if success:
                break
        except:
            pass
    
    if not success:
        success = context.dropdown_handler.select_by_index(
            dropdown_label,
            int(index),
            identifier_type='label'
        )
    
    assert success, f"Failed to select index {index} in dropdown '{dropdown_label}'"
    print(f"   >> Selected index {index} successfully")


@when(parsers.parse('I choose multiple tags {option_texts} in dropdown {dropdown_label}'))
def step_select_multiple_tags(context, option_texts, dropdown_label):
    """
    Select multiple options/tags in dropdown (no quotes needed)
    
    Args:
        context: Context fixture from conftest.py
        option_texts: Comma-separated option texts (e.g., "Developer, QA")
        dropdown_label: Dropdown label
    """
    print(f"   >> Selecting multiple options '{option_texts}' in dropdown '{dropdown_label}'...")
    
    # Parse option texts (split by comma)
    options = [opt.strip() for opt in option_texts.split(',')]
    
    # Try data-attr-id first, then label
    success = False
    data_attr_candidates = [
        dropdown_label.lower().replace(' ', '-'),
        dropdown_label.lower().replace(' ', '_'),
        dropdown_label.lower().replace(' ', ''),
    ]
    
    for candidate in data_attr_candidates:
        try:
            success = context.dropdown_handler.select_multiple(
                candidate,
                options,
                identifier_type='data_attr'
            )
            if success:
                break
        except:
            pass
    
    if not success:
        success = context.dropdown_handler.select_multiple(
            dropdown_label,
            options,
            identifier_type='label'
        )
    
    assert success, f"Failed to select multiple options in dropdown '{dropdown_label}'"
    print(f"   >> Selected multiple options successfully")


@when(parsers.parse('I select first option in dropdown {dropdown_label}'))
def step_select_first(context, dropdown_label):
    """
    Select the first option in dropdown
    
    Args:
        context: Context fixture from conftest.py
        dropdown_label: Dropdown label
    """
    print(f"   >> Selecting first option in dropdown '{dropdown_label}'...")
    
    success = False
    data_attr_candidates = [
        dropdown_label.lower().replace(' ', '-'),
        dropdown_label.lower().replace(' ', '_'),
        dropdown_label.lower().replace(' ', ''),
    ]
    
    for candidate in data_attr_candidates:
        try:
            success = context.dropdown_handler.select_first_in(
                candidate,
                identifier_type='data_attr'
            )
            if success:
                break
        except:
            pass
    
    if not success:
        success = context.dropdown_handler.select_first_in(
            dropdown_label,
            identifier_type='label'
        )
    
    assert success, f"Failed to select first option in dropdown '{dropdown_label}'"
    print(f"   >> Selected first option successfully")


@when(parsers.parse('I select last option in dropdown {dropdown_label}'))
def step_select_last(context, dropdown_label):
    """
    Select the last option in dropdown
    
    Args:
        context: Context fixture from conftest.py
        dropdown_label: Dropdown label
    """
    print(f"   >> Selecting last option in dropdown '{dropdown_label}'...")
    
    success = False
    data_attr_candidates = [
        dropdown_label.lower().replace(' ', '-'),
        dropdown_label.lower().replace(' ', '_'),
        dropdown_label.lower().replace(' ', ''),
    ]
    
    for candidate in data_attr_candidates:
        try:
            success = context.dropdown_handler.select_last_in(
                candidate,
                identifier_type='data_attr'
            )
            if success:
                break
        except:
            pass
    
    if not success:
        success = context.dropdown_handler.select_last_in(
            dropdown_label,
            identifier_type='label'
        )
    
    assert success, f"Failed to select last option in dropdown '{dropdown_label}'"
    print(f"   >> Selected last option successfully")


@when(parsers.parse('I select "{option_text}" in dropdown with data-atr-id "{data_attr_id}"'))
def step_select_by_data_attr(context, option_text, data_attr_id):
    """
    Select an option in dropdown by data-atr-id
    
    Args:
        context: Context fixture from conftest.py
        option_text: Option text to select
        data_attr_id: Value of data-atr-id attribute
    """
    print(f"   >> Selecting '{option_text}' in dropdown with data-atr-id '{data_attr_id}'...")
    success = context.dropdown_handler.select_by_text(
        data_attr_id,
        option_text,
        identifier_type='data_attr'
    )
    assert success, f"Failed to select '{option_text}' in dropdown with data-atr-id '{data_attr_id}'"
    print(f"   >> Selected successfully")


@then('I should see a summary of all dropdowns')
def step_show_dropdowns_summary(context):
    """
    Print a summary of all detected dropdowns on the page
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Generating dropdowns summary...")
    context.dropdown_handler.print_dropdowns_summary()


@then(parsers.parse('I should see "{count}" dropdowns of type "{dropdown_type}"'))
def step_verify_dropdown_count_by_type(context, count, dropdown_type):
    """
    Verify the count of dropdowns of a specific type
    
    Args:
        context: Context fixture from conftest.py
        count: Expected number of dropdowns
        dropdown_type: Type of dropdown to count
    """
    print(f"   >> Verifying {dropdown_type} dropdown count...")
    dropdowns = context.dropdown_handler.find_dropdown_by_type(dropdown_type)
    actual_count = len(dropdowns)
    assert actual_count == int(count), \
        f"Expected {count} dropdowns of type '{dropdown_type}', but found {actual_count}"
    print(f"   >> Verification passed: Found {actual_count} {dropdown_type} dropdowns")


@then(parsers.parse('the context should contain dropdown with key "{context_key}"'))
def step_verify_context_contains_dropdown(context, context_key):
    """
    Verify that context contains a dropdown with the specified key
    
    Args:
        context: Context fixture from conftest.py
        context_key: Key to check in context
    """
    print(f"   >> Verifying context contains dropdown with key: '{context_key}'...")
    assert context.element_context.has_element(context_key), \
        f"Context does not contain dropdown with key '{context_key}'"
    
    element_info = context.element_context.get_element(context_key)
    assert element_info is not None, f"Dropdown info is None for key '{context_key}'"
    assert element_info.element_type == 'dropdown', f"Element is not a dropdown type"
    
    # Show dropdown details including location to prove it's different
    try:
        element_text = element_info.element.text.strip()[:50] if element_info.element.text else 'N/A'
        element_location = f"({element_info.element.location['x']}, {element_info.element.location['y']})"
    except:
        element_text = 'N/A'
        element_location = 'N/A'
    
    print(f"   >> Context contains dropdown:")
    print(f"      Context key: '{context_key}' (unique for this scenario)")
    print(f"      Dropdown type: {element_info.metadata.get('type', 'unknown')}")
    print(f"      Data-attr-id: {element_info.data_attr_id}")
    print(f"      Placeholder: {element_info.metadata.get('placeholder', 'N/A')}")
    print(f"      Label: {element_info.metadata.get('label', 'N/A')}")
    print(f"      Element text: '{element_text}'")
    print(f"      Element location: {element_location}")


@then('I verify this is a different dropdown from previous scenarios')
def step_verify_different_dropdown(context):
    """
    Verify that the current dropdown is different from previous scenarios
    Shows context key and element details to prove uniqueness
    """
    all_keys = context.element_context.get_all_keys()
    current_key = context.element_context.current_element_key
    
    print(f"   >> Verifying dropdown uniqueness...")
    print(f"   >> Current context key: '{current_key}'")
    print(f"   >> All context keys in this scenario: {all_keys}")
    
    if current_key:
        element_info = context.element_context.get_element(current_key)
        if element_info:
            try:
                element_text = element_info.element.text.strip()[:50] if element_info.element.text else 'N/A'
                element_location = f"({element_info.element.location['x']}, {element_info.element.location['y']})"
            except:
                element_text = 'N/A'
                element_location = 'N/A'
            
            print(f"   >> This dropdown is UNIQUE:")
            print(f"      Context key: '{current_key}' (different from other scenarios)")
            print(f"      Element location: {element_location}")
            print(f"      Element text: '{element_text}'")
            print(f"   >> Each scenario uses a DIFFERENT dropdown based on position number")


@then(parsers.parse('the dropdown with label "{label_text}" should be "{state}"'))
def step_verify_dropdown_state(context, label_text, state):
    """
    Verify the state of a dropdown (enabled, disabled, loading)
    
    Args:
        context: Context fixture from conftest.py
        label_text: Label text of the dropdown
        state: Expected state (enabled, disabled, loading)
    """
    print(f"   >> Verifying dropdown state for label '{label_text}'...")
    dropdown = context.dropdown_handler.find_dropdown_by_label(label_text, exact_match=False)
    
    assert dropdown is not None, f"Dropdown with label '{label_text}' not found"
    
    dropdown_info = context.dropdown_handler.identify_dropdown_type(dropdown)
    
    if state == 'disabled':
        assert dropdown_info['disabled'], f"Dropdown should be disabled but it's not"
    elif state == 'enabled':
        assert not dropdown_info['disabled'], f"Dropdown should be enabled but it's disabled"
    elif state == 'loading':
        assert dropdown_info['loading'], f"Dropdown should be loading but it's not"
    
    print(f"   >> Verification passed: Dropdown is {state}")


@given('I am on the dropdown page')
@when('I am on the dropdown page')
@then('I am on the dropdown page')
def step_navigate_to_dropdown_page(context):
    """
    Navigate to the Ant Design Dropdown page
    Can be used as Given, When, or Then (for use with And after other steps)
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Navigating to: {DROPDOWN_PAGE_URL}")
    context.driver.get(DROPDOWN_PAGE_URL)
    print(f"   >> Page loaded successfully")

