"""
Gherkin step definitions for button automation using pytest-bdd
pytest-bdd automatically discovers and loads these step definitions
"""
from pytest_bdd import given, when, then, parsers
from framework.components.button_handler import ButtonHandler

# Ant Design Button page URL
DEFAULT_URL = "https://ant.design/components/button"


@given('I am on the button page')
def step_navigate_to_button_page(context):
    """
    Navigate to the default button page
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Navigating to: {DEFAULT_URL}")
    context.driver.get(DEFAULT_URL)
    print(f"   >> Page loaded successfully")


@given(parsers.parse('I am on the "{page_url}" page'))
def step_navigate_to_page(context, page_url):
    """
    Navigate to a specific page
    
    Args:
        context: Context fixture from conftest.py
        page_url: URL of the page to navigate to
    """
    context.driver.get(page_url)


@when(parsers.parse('I click the button with data-atr-id "{data_attr_id}"'))
def step_click_button_by_data_attr(context, data_attr_id):
    """
    Click a button using its data-atr-id attribute
    
    Args:
        context: Context fixture from conftest.py
        data_attr_id: Value of data-atr-id attribute
    """
    context.button_clicked = context.button_handler.click_button(
        data_attr_id, 
        identifier_type='data_attr'
    )


@when(parsers.parse('I click the button with text "{button_text}"'))
def step_click_button_by_text(context, button_text):
    """
    Click a button using its text content
    
    Args:
        context: Context fixture from conftest.py
        button_text: Text content of the button
    """
    context.button_clicked = context.button_handler.click_button(
        button_text, 
        identifier_type='text'
    )


@when(parsers.parse('I click the "{button_type}" type button'))
def step_click_button_by_type(context, button_type):
    """
    Click a button by its type (primary, default, dashed, etc.)
    
    Args:
        context: Context fixture from conftest.py
        button_type: Type of button (primary, default, dashed, text, link, danger)
    """
    # Find and click the button, storing its info
    # Use click_button which will handle finding and clicking, then get info after
    context.button_clicked = context.button_handler.click_button(
        button_type, 
        identifier_type='type'
    )
    
    # Get button info after clicking (re-find to avoid stale elements)
    if context.button_clicked:
        try:
            buttons = context.button_handler.find_button_by_type(button_type)
            if buttons:
                context.last_clicked_button_info = context.button_handler.identify_button_type(buttons[0])
            else:
                context.last_clicked_button_info = None
        except Exception as e:
            print(f"   >> Warning: Could not get button info after click: {str(e)}")
            context.last_clicked_button_info = None
    else:
        context.button_clicked = False
        context.last_clicked_button_info = None


@when('I click the primary button')
@then('I click the primary button')
def step_click_primary_button(context):
    """Click the first primary button on the page. Can be used as When or Then (for use with And after other steps)"""
    print(f"   >> Clicking primary button...")
    step_click_button_by_type(context, 'primary')
    print(f"   >> Primary button click {'successful' if context.button_clicked else 'failed'}")


@when('I click the default button')
@then('I click the default button')
def step_click_default_button(context):
    """Click the first default button on the page. Can be used as When or Then (for use with And after other steps)"""
    print(f"   >> Clicking default button...")
    step_click_button_by_type(context, 'default')
    print(f"   >> Default button click {'successful' if context.button_clicked else 'failed'}")


@when('I click the dashed button')
@then('I click the dashed button')
def step_click_dashed_button(context):
    """Click the first dashed button on the page. Can be used as When or Then (for use with And after other steps)"""
    print(f"   >> Clicking dashed button...")
    step_click_button_by_type(context, 'dashed')
    print(f"   >> Dashed button click {'successful' if context.button_clicked else 'failed'}")


@when('I click the text button')
def step_click_text_button(context):
    """Click the first text button on the page"""
    print(f"   >> Clicking text button...")
    step_click_button_by_type(context, 'text')
    print(f"   >> Text button click {'successful' if context.button_clicked else 'failed'}")


@when('I click the link button')
def step_click_link_button(context):
    """Click the first link button on the page"""
    print(f"   >> Clicking link button...")
    step_click_button_by_type(context, 'link')
    print(f"   >> Link button click {'successful' if context.button_clicked else 'failed'}")


@when('I click the danger button')
def step_click_danger_button(context):
    """Click the first danger button on the page"""
    print(f"   >> Clicking danger button...")
    step_click_button_by_type(context, 'danger')
    print(f"   >> Danger button click {'successful' if context.button_clicked else 'failed'}")


@when(parsers.parse('I auto-detect and click the button "{identifier}"'))
def step_auto_detect_click_button(context, identifier):
    """
    Auto-detect and click a button using multiple strategies
    
    Args:
        context: Context fixture from conftest.py
        identifier: Identifier for the button (tries data-attr-id, text, type)
    """
    context.button_clicked = context.button_handler.click_button_by_auto_detect(identifier)


@then('the button should be clicked successfully')
def step_verify_button_clicked(context):
    """
    Verify that the button was clicked successfully
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Verifying button click was successful...")
    assert hasattr(context, 'button_clicked'), "Button click was not attempted"
    assert context.button_clicked, "Button click failed"
    print(f"   >> Verification passed: Button was clicked successfully")


@then(parsers.parse('I should see the button type is "{expected_type}"'))
def step_verify_button_type(context, expected_type):
    """
    Verify that the clicked button has the expected type
    
    Args:
        context: Context fixture from conftest.py
        expected_type: Expected button type (primary, default, dashed, text, link, danger)
    """
    print(f"   >> Verifying button type is '{expected_type}'...")
    assert hasattr(context, 'last_clicked_button_info'), "No button was clicked in this scenario"
    assert context.last_clicked_button_info is not None, "Button information is not available"
    
    actual_type = context.last_clicked_button_info.get('type', '').lower()
    expected_type_lower = expected_type.lower()
    
    print(f"   >> Actual button type: '{actual_type}'")
    print(f"   >> Expected button type: '{expected_type_lower}'")
    
    assert actual_type == expected_type_lower, \
        f"Expected button type '{expected_type_lower}' but got '{actual_type}'"
    
    print(f"   >> Verification passed: Button type matches expected '{expected_type}'")


@then(parsers.parse('the button with data-atr-id "{data_attr_id}" should be "{state}"'))
def step_verify_button_state(context, data_attr_id, state):
    """
    Verify the state of a button (enabled, disabled, loading)
    
    Args:
        context: Context fixture from conftest.py
        data_attr_id: Value of data-atr-id attribute
        state: Expected state (enabled, disabled, loading)
    """
    button_info = context.button_handler.get_button_info(data_attr_id, identifier_type='data_attr')
    
    assert button_info is not None, f"Button with data-atr-id '{data_attr_id}' not found"
    
    if state == 'disabled':
        assert button_info['disabled'], f"Button should be disabled but it's not"
    elif state == 'enabled':
        assert not button_info['disabled'], f"Button should be enabled but it's disabled"
    elif state == 'loading':
        assert button_info['loading'], f"Button should be in loading state but it's not"


@then(parsers.parse('I should see "{count}" buttons of type "{button_type}"'))
def step_verify_button_count(context, count, button_type):
    """
    Verify the count of buttons of a specific type
    
    Args:
        context: Context fixture from conftest.py
        count: Expected number of buttons
        button_type: Type of button to count
    """
    buttons = context.button_handler.find_button_by_type(button_type)
    assert len(buttons) == int(count), f"Expected {count} buttons of type '{button_type}', but found {len(buttons)}"


# Context-driven steps
@given(parsers.parse('I identify the button with data-atr-id "{data_attr_id}"'))
def step_identify_button_by_data_attr(context, data_attr_id):
    """
    Identify a button by data-atr-id and store it in context
    This automatically populates the context with element information
    
    Args:
        context: Context fixture from conftest.py
        data_attr_id: Value of data-atr-id attribute
    """
    print(f"   >> Identifying button with data-atr-id: '{data_attr_id}'...")
    success = context.button_handler.identify_and_store(
        data_attr_id,
        identifier_type='data_attr'
    )
    assert success, f"Failed to identify button with data-atr-id '{data_attr_id}'"
    print(f"   >> Button identified and stored in context")


@given(parsers.parse('I identify the button with text "{button_text}"'))
def step_identify_button_by_text(context, button_text):
    """
    Identify a button by text and store it in context
    
    Args:
        context: Context fixture from conftest.py
        button_text: Text content of the button
    """
    print(f"   >> Identifying button with text: '{button_text}'...")
    success = context.button_handler.identify_and_store(
        button_text,
        identifier_type='text'
    )
    assert success, f"Failed to identify button with text '{button_text}'"
    print(f"   >> Button identified and stored in context")


@given(parsers.parse('I identify the "{button_type}" type button'))
def step_identify_button_by_type(context, button_type):
    """
    Identify a button by type and store it in context
    
    Args:
        context: Context fixture from conftest.py
        button_type: Type of button (primary, default, dashed, text, link, danger)
    """
    print(f"   >> Identifying {button_type} button...")
    success = context.button_handler.identify_and_store(
        button_type,
        identifier_type='type'
    )
    assert success, f"Failed to identify {button_type} button"
    print(f"   >> Button identified and stored in context")


@when('I click the button from context')
def step_click_button_from_context(context):
    """
    Click the current button from context (context-driven interaction)
    Uses the element stored in context instead of manually locating it
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Clicking button from context...")
    context.button_clicked = context.button_handler.click_from_context()
    if context.button_clicked:
        # Store button info for verification
        current_element = context.element_context.get_current()
        if current_element:
            context.last_clicked_button_info = current_element.metadata
        print(f"   >> Button clicked successfully from context")
    else:
        print(f"   >> Failed to click button from context")


@when(parsers.parse('I click the button with context key "{context_key}"'))
def step_click_button_by_context_key(context, context_key):
    """
    Click a button using a specific context key
    
    Args:
        context: Context fixture from conftest.py
        context_key: Key of the element in context
    """
    print(f"   >> Clicking button with context key: '{context_key}'...")
    context.button_clicked = context.button_handler.click_from_context(context_key)
    if context.button_clicked:
        # Store button info for verification
        element_info = context.element_context.get_element(context_key)
        if element_info:
            context.last_clicked_button_info = element_info.metadata
        print(f"   >> Button clicked successfully")
    else:
        print(f"   >> Failed to click button with context key '{context_key}'")


@then(parsers.parse('the context should contain element with key "{context_key}"'))
def step_verify_context_contains_element(context, context_key):
    """
    Verify that context contains an element with the specified key
    
    Args:
        context: Context fixture from conftest.py
        context_key: Key to check in context
    """
    print(f"   >> Verifying context contains element with key: '{context_key}'...")
    assert context.element_context.has_element(context_key), \
        f"Context does not contain element with key '{context_key}'"
    
    element_info = context.element_context.get_element(context_key)
    assert element_info is not None, f"Element info is None for key '{context_key}'"
    print(f"   >> Context contains element:")
    print(f"      Element type: {element_info.element_type}")
    print(f"      Application type: {element_info.application_type}")
    print(f"      Data-attr-id: {element_info.data_attr_id}")


@then(parsers.parse('the context element "{context_key}" should have application type "{expected_type}"'))
def step_verify_context_element_application_type(context, context_key, expected_type):
    """
    Verify that a context element has the expected application type (from data-type attribute)
    
    Args:
        context: Context fixture from conftest.py
        context_key: Key of the element in context
        expected_type: Expected application type
    """
    print(f"   >> Verifying application type for context key '{context_key}'...")
    element_info = context.element_context.get_element(context_key)
    assert element_info is not None, f"Element not found in context with key '{context_key}'"
    
    actual_type = element_info.application_type
    assert actual_type == expected_type, \
        f"Expected application type '{expected_type}' but got '{actual_type}'"
    print(f"   >> Application type verified: '{expected_type}'")
