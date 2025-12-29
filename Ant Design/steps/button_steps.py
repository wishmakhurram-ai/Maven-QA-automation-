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


@when(parsers.parse('I click the button with text {button_text}'))
def step_click_button_by_text_no_quotes(context, button_text):
    """
    Click a button by its visible text (without quotes)
    Automatically discovers data-attr-id patterns if text search fails
    
    Args:
        context: Context fixture from conftest.py
        button_text: Text visible on the button
    """
    print(f"   >> Clicking button with text: '{button_text}'...")
    
    # Use 'auto' identifier type which tries pattern discovery first
    context.button_clicked = context.button_handler.click_button(
        button_text,
        identifier_type='auto'
    )
    
    # If auto failed, try text as fallback
    if not context.button_clicked:
        context.button_clicked = context.button_handler.click_button(
            button_text,
            identifier_type='text'
        )
    
    context.last_clicked_button_info = context.button_handler.get_button_info(button_text, identifier_type='auto')
    if not context.last_clicked_button_info:
        context.last_clicked_button_info = context.button_handler.get_button_info(button_text, identifier_type='text')
    
    assert context.button_clicked, f"Failed to click button with text '{button_text}'"
    print(f"   >> Button clicked successfully")


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
@when('I pressed the primary button')
@then('I click the primary button')
@then('I pressed the primary button')
def step_click_primary_button(context):
    """Click the first primary button on the page. Can be used as When or Then (for use with And after other steps)"""
    print(f"   >> Clicking primary button...")
    step_click_button_by_type(context, 'primary')
    print(f"   >> Primary button click {'successful' if context.button_clicked else 'failed'}")


@when('I pressed the default button')
@then('I pressed the default button')
def step_pressed_default_button(context):
    """Press the default button"""
    print(f"   >> Pressing default button...")
    step_click_button_by_type(context, 'default')
    print(f"   >> Default button press {'successful' if context.button_clicked else 'failed'}")


@when('I pressed the dashed button')
@then('I pressed the dashed button')
def step_pressed_dashed_button(context):
    """Press the dashed button"""
    print(f"   >> Pressing dashed button...")
    step_click_button_by_type(context, 'dashed')
    print(f"   >> Dashed button press {'successful' if context.button_clicked else 'failed'}")


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
    button_info = context.button_handler.get_button_info(data_attr_id, identifier_type='data_attr_id')
    
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
        identifier_type='data_attr_id'
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


@when(parsers.parse('I click the "{button_text}" button'))
@then(parsers.parse('I click the "{button_text}" button'))
def step_click_button_with_text_maven(context, button_text):
    """
    Click a button by text and wait for navigation if it's a login/submit button
    Uses data-attr-id pattern discovery
    """
    print(f"   >> Clicking button: {button_text}")
    
    # Store current URL before clicking (for navigation detection)
    current_url_before = context.driver.current_url
    
    context.button_clicked = context.button_handler.click_button(
        button_text,
        identifier_type='auto'
    )
    if not context.button_clicked:
        context.button_clicked = context.button_handler.click_button(
            button_text,
            identifier_type='text'
        )
    assert context.button_clicked, f"Failed to click button '{button_text}'"
    print(f"   >> Button clicked successfully")
    
    # Wait for navigation if this is a login/submit button
    if button_text.lower() in ['log in', 'login', 'sign in', 'signin', 'submit', 'log in button']:
        print(f"   >> Waiting for navigation after login button click...")
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.keys import Keys
            import time
            
            # Small wait to let button click register
            time.sleep(0.2)  # Faster wait
            
            # Check if we're already navigated
            current_url_after_click = context.driver.current_url.lower()
            if current_url_after_click != current_url_before.lower() and 'login' not in current_url_after_click:
                print(f"   >> Navigation already happened: {context.driver.current_url}")
                return
            
            # Try to submit form if button click didn't trigger navigation
            try:
                from selenium.webdriver.common.by import By
                # Find the form and try to submit it
                forms = context.driver.find_elements(By.TAG_NAME, "form")
                if forms:
                    form = forms[0]  # Get first form
                    # Try pressing Enter on the submit button first
                    try:
                        submit_button = form.find_element(By.XPATH, ".//button[@type='submit'] | .//input[@type='submit'] | .//button[contains(text(), 'Log In')] | .//button[contains(text(), 'Login')]")
                        if submit_button:
                            # Try JavaScript click first (more reliable)
                            try:
                                context.driver.execute_script("arguments[0].click();", submit_button)
                                print(f"   >> Form submit button clicked using JavaScript")
                                time.sleep(0.2)  # Faster wait
                            except:
                                submit_button.send_keys(Keys.RETURN)
                                print(f"   >> Form submitted using Enter key")
                                time.sleep(0.2)  # Faster wait
                    except:
                        # Try JavaScript form submission as fallback
                        try:
                            context.driver.execute_script("arguments[0].submit();", form)
                            print(f"   >> Form submitted using JavaScript")
                            time.sleep(0.2)  # Faster wait
                        except:
                            pass
            except Exception as e:
                print(f"   >> Form submission attempt: {str(e)}")
            
            # Wait for URL to change or page to load (increased timeout to 30 seconds)
            wait = WebDriverWait(context.driver, 30)  # Increased from 20 to 30 seconds
            
            # Wait for URL to change (navigation happened) - check that we're no longer on login page
            def url_changed_or_not_login(driver):
                current_url = driver.current_url.lower()
                # Check if URL changed
                if current_url != current_url_before.lower():
                    return True
                # Check if we're no longer on login page
                if 'login' not in current_url:
                    return True
                # Check if we're on dashboard/firms/users page
                if 'dashboard' in current_url or 'firms' in current_url or 'users' in current_url:
                    return True
                # Check if there are any error messages (login might have failed)
                try:
                    page_source = driver.page_source.lower()
                    # If there are common error indicators, navigation might not happen
                    if 'invalid' in page_source or 'error' in page_source or 'incorrect' in page_source:
                        # Still wait a bit more in case it's just a delay
                        return False
                except:
                    pass
                return False
            
            try:
                wait.until(url_changed_or_not_login)
                current_url = context.driver.current_url
                print(f"   >> Navigation detected: {current_url}")
                
                # Additional wait for page to be fully loaded
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                print(f"   >> Page loaded completely")
                
                # Wait a bit more for any dynamic content (tables, menus, etc.)
                time.sleep(0.2)  # Faster wait  # Faster wait for dynamic content
                print(f"   >> Dynamic content loaded")
                
                # Set global login state for session reuse (happy case login)
                try:
                    from conftest import _login_state
                    _login_state['logged_in'] = True
                    _login_state['login_url'] = current_url
                    print(f"   >> Login state set for session reuse")
                except:
                    pass
            except Exception as e:
                # Check current URL - might still be on login if credentials are wrong
                current_url = context.driver.current_url.lower()
                print(f"   >> Navigation wait completed. Current URL: {current_url}")
                print(f"   >> Wait result: {str(e)}")
                if 'login' in current_url:
                    print(f"   >> Still on login page - login may have failed or credentials incorrect")
                # Still wait for page to load even if URL didn't change
                try:
                    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                    time.sleep(0.3)  # Faster wait for dynamic content
                except:
                    pass
                # Don't fail here, let verification steps handle it
        except Exception as e:
            print(f"   >> Navigation wait error: {str(e)}")
            # Check current URL
            current_url = context.driver.current_url
            print(f"   >> Current URL after login click: {current_url}")
            # Don't fail here, let the verification steps handle it


# ==================== COMMON BUTTON STEPS FOR MAVEN & ADMIN DASHBOARD ====================

@when(parsers.parse('I click on the "{link_text}" link'))
@when(parsers.parse('I click on "{link_text}" link'))
def step_click_link(context, link_text):
    """
    Click on a link by text
    Common step used in both maven_automation.feature and admin_dashboard.feature
    PRIORITY: data-attr-id pattern discovery FIRST, then fallback strategies
    """
    print(f"   >> Clicking on link: '{link_text}' (using data-attr-id pattern discovery)")
    context.button_clicked = False
    
    # Strategy 1: PATTERN DISCOVERY - Find link by data-attr-id (HIGHEST PRIORITY)
    try:
        from framework.utils.pattern_discovery import PatternDiscovery
        pattern_discovery = PatternDiscovery(context.driver)
        
        # Normalize link text for pattern matching
        normalized_text = link_text.lower().replace(' ', '-').replace('_', '-').replace('?', '').replace('!', '').replace('.', '')
        
        # Special handling for "Forgot password" links
        if 'forgot' in link_text.lower() and 'password' in link_text.lower():
            # Try multiple variations for forgot password links
            password_variations = [
                'forgot-password',
                'forgotpassword',
                'forgot_password',
                'password-reset',
                'passwordreset',
                'password_reset',
                'reset-password',
                'resetpassword',
                'reset_password'
            ]
            matching_attr_id = None
            for variation in password_variations:
                matching_attr_id = pattern_discovery.find_matching_data_attr_id(variation, 'link')
                if matching_attr_id:
                    normalized_text = variation
                    print(f"   >> Found forgot password link using variation: '{variation}'")
                    break
        else:
            # Try to find matching data-attr-id using pattern discovery
            matching_attr_id = pattern_discovery.find_matching_data_attr_id(normalized_text, 'link')
        
        print(f"   >> Searching for link using pattern discovery (normalized: '{normalized_text}')...")
        
        if matching_attr_id:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            wait = WebDriverWait(context.driver, 3)  # Faster timeout
            try:
                link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-attr-id="{matching_attr_id}"]')))
                # Try normal click first
                try:
                    link.click()
                    context.button_clicked = True
                    print(f"   >> ✓ Link clicked using pattern discovery (data-attr-id: '{matching_attr_id}')")
                except:
                    # Fallback to JavaScript click if normal click fails
                    context.driver.execute_script("arguments[0].click();", link)
                    context.button_clicked = True
                    print(f"   >> ✓ Link clicked using pattern discovery (JavaScript click, data-attr-id: '{matching_attr_id}')")
            except:
                try:
                    link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-atr-id="{matching_attr_id}"]')))
                    # Try normal click first
                    try:
                        link.click()
                        context.button_clicked = True
                        print(f"   >> ✓ Link clicked using pattern discovery (data-atr-id: '{matching_attr_id}')")
                    except:
                        # Fallback to JavaScript click
                        context.driver.execute_script("arguments[0].click();", link)
                        context.button_clicked = True
                        print(f"   >> ✓ Link clicked using pattern discovery (JavaScript click, data-atr-id: '{matching_attr_id}')")
                except:
                    pass
        
        # If direct match not found, generate candidates
        if not context.button_clicked:
            print(f"   >> Direct match not found, generating pattern candidates...")
            candidates = pattern_discovery.generate_candidates(normalized_text, 'link')
            for candidate in candidates[:5]:  # Try first 5 candidates
                try:
                    from selenium.webdriver.common.by import By
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    wait = WebDriverWait(context.driver, 2)
                    try:
                        link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-attr-id="{candidate}"]')))
                        # Verify link text matches
                        link_text_lower = link.text.strip().lower()
                        if normalized_text.replace('-', ' ') in link_text_lower or link_text.lower() in link_text_lower:
                            link.click()
                            context.button_clicked = True
                            print(f"   >> ✓ Link clicked using pattern candidate (data-attr-id: '{candidate}')")
                            break
                    except:
                        try:
                            link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-atr-id="{candidate}"]')))
                            link_text_lower = link.text.strip().lower()
                            if normalized_text.replace('-', ' ') in link_text_lower or link_text.lower() in link_text_lower:
                                link.click()
                                context.button_clicked = True
                                print(f"   >> ✓ Link clicked using pattern candidate (data-atr-id: '{candidate}')")
                                break
                        except:
                            continue
                except:
                    continue
    except Exception as e:
        print(f"   >> Pattern discovery error: {str(e)}")
    
    # Strategy 2: Use button handler with pattern discovery (links can be styled as buttons)
    if not context.button_clicked:
        try:
            # Store initial URL before click
            initial_url = context.driver.current_url
            
            context.button_clicked = context.button_handler.click_button(
                link_text,
                identifier_type='auto'  # This also uses pattern discovery internally
            )
            if context.button_clicked:
                print(f"   >> ✓ Link clicked using button handler (pattern discovery)")
                
                # Wait for navigation to start (if it's a navigation link) - faster
                import time
                time.sleep(0.3)  # Faster wait for navigation
                
                # Check if URL changed
                try:
                    new_url = context.driver.current_url
                    if new_url != initial_url:
                        print(f"   >> Navigation detected: {initial_url} -> {new_url}")
                    else:
                        print(f"   >> Note: URL unchanged after click (might be modal/popup or same page)")
                except:
                    pass
        except Exception as e:
            print(f"   >> Button handler failed: {str(e)}")
    
    # Strategy 3: Try as text with button handler
    if not context.button_clicked:
        try:
            context.button_clicked = context.button_handler.click_button(
                link_text,
                identifier_type='text'
            )
            if context.button_clicked:
                print(f"   >> Link clicked using text search")
        except:
            pass
    
    # Strategy 4: Use Selenium's link locators (for actual <a> tags) - FALLBACK ONLY
    if not context.button_clicked:
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(context.driver, 3)
            # Try exact link text
            try:
                link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, link_text)))
                link.click()
                context.button_clicked = True
                print(f"   >> Link clicked using LINK_TEXT (fallback)")
            except:
                # Try partial link text
                try:
                    link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, link_text)))
                    link.click()
                    context.button_clicked = True
                    print(f"   >> Link clicked using PARTIAL_LINK_TEXT (fallback)")
                except:
                    # Try XPath with contains
                    try:
                        link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{link_text}')]")))
                        link.click()
                        context.button_clicked = True
                        print(f"   >> Link clicked using XPath (fallback)")
                    except:
                        # Try XPath for buttons styled as links
                        try:
                            link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{link_text}')] | //a[contains(text(), '{link_text}')]")))
                            link.click()
                            context.button_clicked = True
                            print(f"   >> Link clicked using button/link XPath (fallback)")
                        except:
                            pass
        except Exception as e:
            print(f"   >> Error clicking link with Selenium: {str(e)}")
    
    assert context.button_clicked, f"Failed to click link '{link_text}' - tried all strategies (pattern discovery FIRST, then button handler, then Selenium locators)"
    
    # Verify click actually triggered navigation or action
    # Wait a moment for navigation/action to start
    import time
    time.sleep(0.2)  # Faster wait for navigation
    
    # Check if URL changed (for navigation links)
    try:
        current_url = context.driver.current_url
        # If it's a navigation link, URL should change
        # For now, just log the URL
        print(f"   >> Current URL after click: {current_url}")
    except:
        pass
    
    print(f"   >> Link clicked successfully")


@when(parsers.parse('I click on the "{icon_name}" icon'))
@when(parsers.parse('I click on the "{icon_name}" icon in the {location}'))
def step_click_icon(context, icon_name, location=None):
    """
    Click on an icon by name
    Common step used in admin_dashboard.feature
    Handles patterns like:
    - "I click on the User Profile Icon in the header"
    - "I click on the delete icon"
    Uses data-attr-id pattern discovery
    """
    print(f"   >> Clicking on icon: '{icon_name}'" + (f" in the {location}" if location else ""))
    # Clean icon name (remove descriptions in parentheses like "(dustbin/trash can)")
    clean_icon_name = icon_name.split('(')[0].strip()
    
    # Icons might be buttons or clickable elements
    context.button_clicked = context.button_handler.click_button(
        clean_icon_name,
        identifier_type='auto'
    )
    if not context.button_clicked:
        # Try with "icon" suffix/prefix variations
        icon_variations = [
            f"{clean_icon_name} icon",
            f"icon {clean_icon_name}",
            clean_icon_name.replace(' icon', ''),
            clean_icon_name.replace('icon ', ''),
            icon_name  # Try original with parentheses
        ]
        for variation in icon_variations:
            context.button_clicked = context.button_handler.click_button(
                variation,
                identifier_type='auto'
            )
            if context.button_clicked:
                break
    
    # If still not found and location is specified, try to find in that location
    if not context.button_clicked and location:
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(context.driver, 5)  # Faster timeout
            # Find element in the specified location (e.g., header)
            location_xpath = f"//*[contains(@class, '{location.lower()}')]//*[contains(@aria-label, '{clean_icon_name}') or contains(@title, '{clean_icon_name}')]"
            icon = wait.until(EC.element_to_be_clickable((By.XPATH, location_xpath)))
            icon.click()
            context.button_clicked = True
        except:
            pass
    
    assert context.button_clicked, f"Failed to click icon '{icon_name}'"
    print(f"   >> Icon clicked successfully")


@when(parsers.parse('I click on the "{icon_name}" icon for the {item_type} "{item_name}"'))
@when(parsers.parse('I click on the "{icon_name}" icon for the {item_type} "{item_name}" again'))
def step_click_icon_for_item(context, icon_name, item_type, item_name):
    """
    Click on an icon for a specific item (e.g., delete icon for a firm)
    Common step used in admin_dashboard.feature
    Handles patterns like:
    - "I click on the delete icon (dustbin/trash can) for the firm "Smith & Associates Law""
    - "I click on the suspend icon (circle with slash) for the firm "Smith & Associates Law" again"
    Uses data-attr-id pattern discovery
    """
    print(f"   >> Clicking on '{icon_name}' icon for {item_type} '{item_name}'")
    # Clean icon name (remove descriptions in parentheses like "(dustbin/trash can)")
    clean_icon_name = icon_name.split('(')[0].strip()
    
    # First try to find the item row, then find the icon within that row
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(context.driver, 10)
        
        # Find the row containing the item name
        item_row_xpath = f"//tr[contains(., '{item_name}')] | //*[contains(@class, 'row')][contains(., '{item_name}')]"
        item_row = wait.until(EC.presence_of_element_located((By.XPATH, item_row_xpath)))
        
        # Within that row, find the icon
        # Try different icon identification methods
        icon_keywords = [clean_icon_name.lower(), 'delete', 'suspend', 'edit', 'remove']
        icon_selectors = []
        for keyword in icon_keywords:
            icon_selectors.extend([
                f".//*[contains(@class, '{keyword}')]",
                f".//*[contains(@aria-label, '{keyword}')]",
                f".//*[contains(@title, '{keyword}')]",
                f".//button[contains(@aria-label, '{keyword}')]",
                f".//*[contains(@data-attr-id, '{keyword.replace(' ', '-')}')]"
            ])
        
        icon_found = False
        for selector in icon_selectors:
            try:
                icon = item_row.find_element(By.XPATH, selector)
                icon.click()
                context.button_clicked = True
                icon_found = True
                break
            except:
                continue
        
        if not icon_found:
            # Fallback: try button handler with icon name
            context.button_clicked = context.button_handler.click_button(
                clean_icon_name,
                identifier_type='auto'
            )
    except Exception as e:
        print(f"   >> Error finding item row, trying direct icon click: {str(e)}")
        # Fallback: try direct icon click
        context.button_clicked = context.button_handler.click_button(
            clean_icon_name,
            identifier_type='auto'
        )
    
    assert context.button_clicked, f"Failed to click '{icon_name}' icon for {item_type} '{item_name}'"
    print(f"   >> Icon clicked successfully")


# ==================== PASSWORD RECOVERY / FORGOT PASSWORD STEPS ====================

@when(parsers.parse('I click the "{button_text}" button'))
@when(parsers.parse('I click "{button_text}" button'))
@when(parsers.parse('I click "{button_text}"'))
@then(parsers.parse('I click the "{button_text}" button'))
@then(parsers.parse('I click "{button_text}" button'))
@then(parsers.parse('I click "{button_text}"'))
def step_click_button_generic(context, button_text):
    """
    Generic button click step that handles all button actions
    Handles patterns like:
    - "I click the Send Verification Code button"
    - "I click Send Verification Code"
    - "I click Verify or Continue button"
    Uses data-attr-id pattern discovery
    """
    print(f"   >> Clicking button: '{button_text}'")
    
    # Handle "or" patterns (e.g., "Verify or Continue")
    if ' or ' in button_text.lower():
        button_options = [opt.strip() for opt in button_text.split(' or ')]
        for option in button_options:
            context.button_clicked = context.button_handler.click_button(
                option,
                identifier_type='auto'
            )
            if context.button_clicked:
                print(f"   >> Clicked button: '{option}'")
                break
    else:
        context.button_clicked = context.button_handler.click_button(
            button_text,
            identifier_type='auto'
        )
        if not context.button_clicked:
            context.button_clicked = context.button_handler.click_button(
                button_text,
                identifier_type='text'
            )
    
    assert context.button_clicked, f"Failed to click button '{button_text}'"
    print(f"   >> Button clicked successfully")


@when(parsers.parse('I click on the "{link_text}" or "{alt_link_text}" link'))
@when(parsers.parse('I click on "{link_text}" or "{alt_link_text}" link'))
def step_click_link_or_alt(context, link_text, alt_link_text):
    """
    Click on a link with alternative text
    Handles patterns like:
    - "I click on the Back to Login or Cancel link"
    Uses data-attr-id pattern discovery
    """
    print(f"   >> Clicking on link: '{link_text}' or '{alt_link_text}'")
    
    # Try first link
    context.button_clicked = context.button_handler.click_button(
        link_text,
        identifier_type='auto'
    )
    
    # If first fails, try alternative
    if not context.button_clicked:
        context.button_clicked = context.button_handler.click_button(
            alt_link_text,
            identifier_type='auto'
        )
    
    # Fallback to Selenium link locators
    if not context.button_clicked:
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(context.driver, 5)  # Faster timeout
            for link_option in [link_text, alt_link_text]:
                try:
                    link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, link_option)))
                    link.click()
                    context.button_clicked = True
                    break
                except:
                    continue
        except Exception as e:
            print(f"   >> Error clicking link: {str(e)}")
    
    assert context.button_clicked, f"Failed to click link '{link_text}' or '{alt_link_text}'"
    print(f"   >> Link clicked successfully")


# ==================== TABLE AND ROW ACTIONS ====================

@when(parsers.parse('I click on the firm name "{firm_name}" or the firm row'))
@when(parsers.parse('I click on the firm name "{firm_name}"'))
def step_click_firm_name_or_row(context, firm_name):
    """
    Click on firm name or firm row
    Uses data-attr-id pattern discovery
    """
    print(f"   >> Clicking on firm name or row: '{firm_name}'")
    
    # Try clicking as button/link
    context.button_clicked = context.button_handler.click_button(
        firm_name,
        identifier_type='auto'
    )
    
    # If not found, try finding the row and clicking it
    if not context.button_clicked:
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(context.driver, 5)  # Faster timeout
            # Find row containing firm name
            row_xpath = f"//tr[contains(., '{firm_name}')] | //*[contains(@class, 'row')][contains(., '{firm_name}')]"
            row = wait.until(EC.element_to_be_clickable((By.XPATH, row_xpath)))
            row.click()
            context.button_clicked = True
        except Exception as e:
            print(f"   >> Error clicking firm row: {str(e)}")
    
    assert context.button_clicked, f"Failed to click firm name or row '{firm_name}'"
    print(f"   >> Firm name or row clicked successfully")


@when(parsers.parse('I click on the edit icon for the firm "{firm_name}"'))
@when(parsers.parse('I click on the edit icon (pencil) for the firm "{firm_name}"'))
def step_click_edit_icon_for_firm(context, firm_name):
    """
    Click on edit icon for a specific firm
    Uses data-attr-id pattern discovery
    """
    print(f"   >> Clicking on edit icon for firm: '{firm_name}'")
    
    # Use the existing icon click step logic
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(context.driver, 10)
        
        # Find the row containing the firm name
        item_row_xpath = f"//tr[contains(., '{firm_name}')] | //*[contains(@class, 'row')][contains(., '{firm_name}')]"
        item_row = wait.until(EC.presence_of_element_located((By.XPATH, item_row_xpath)))
        
        # Find edit icon in the row
        edit_selectors = [
            ".//*[contains(@class, 'edit')]",
            ".//*[contains(@aria-label, 'edit')]",
            ".//*[contains(@title, 'edit')]",
            ".//button[contains(@aria-label, 'edit')]",
            ".//*[contains(@data-attr-id, 'edit')]",
            ".//*[contains(@class, 'pencil')]"
        ]
        
        icon_found = False
        for selector in edit_selectors:
            try:
                icon = item_row.find_element(By.XPATH, selector)
                icon.click()
                context.button_clicked = True
                icon_found = True
                break
            except:
                continue
        
        if not icon_found:
            context.button_clicked = context.button_handler.click_button('edit', identifier_type='auto')
    except Exception as e:
        print(f"   >> Error finding firm row, trying direct edit click: {str(e)}")
        context.button_clicked = context.button_handler.click_button('edit', identifier_type='auto')
    
    assert context.button_clicked, f"Failed to click edit icon for firm '{firm_name}'"
    print(f"   >> Edit icon clicked successfully")


@when(parsers.parse('I click on the remove icon for "{email}"'))
@when(parsers.parse('I click on the remove icon (trash can) for "{email}"'))
@when(parsers.parse('I click on the delete icon for "{email}"'))
@when(parsers.parse('I click on the remove or delete icon for "{email}"'))
def step_click_remove_icon_for_email(context, email):
    """
    Click on remove/delete icon for a specific email
    Uses data-attr-id pattern discovery
    """
    print(f"   >> Clicking on remove/delete icon for email: '{email}'")
    
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(context.driver, 10)
        
        # Find the row containing the email
        item_row_xpath = f"//tr[contains(., '{email}')] | //*[contains(@class, 'row')][contains(., '{email}')]"
        item_row = wait.until(EC.presence_of_element_located((By.XPATH, item_row_xpath)))
        
        # Find remove/delete icon in the row
        icon_keywords = ['remove', 'delete', 'trash']
        icon_selectors = []
        for keyword in icon_keywords:
            icon_selectors.extend([
                f".//*[contains(@class, '{keyword}')]",
                f".//*[contains(@aria-label, '{keyword}')]",
                f".//*[contains(@title, '{keyword}')]",
                f".//button[contains(@aria-label, '{keyword}')]",
                f".//*[contains(@data-attr-id, '{keyword}')]"
            ])
        
        icon_found = False
        for selector in icon_selectors:
            try:
                icon = item_row.find_element(By.XPATH, selector)
                icon.click()
                context.button_clicked = True
                icon_found = True
                break
            except:
                continue
        
        if not icon_found:
            context.button_clicked = context.button_handler.click_button('remove', identifier_type='auto')
    except Exception as e:
        print(f"   >> Error finding email row, trying direct remove click: {str(e)}")
        context.button_clicked = context.button_handler.click_button('remove', identifier_type='auto')
    
    assert context.button_clicked, f"Failed to click remove/delete icon for email '{email}'"
    print(f"   >> Remove/delete icon clicked successfully")


@when(parsers.parse('I click on a user row'))
def step_click_user_row(context):
    """
    Click on a user row in the table
    """
    print(f"   >> Clicking on a user row")
    
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(context.driver, 10)
        # Find first clickable user row (skip header)
        row = wait.until(EC.element_to_be_clickable((By.XPATH, "//tbody//tr | //*[contains(@class, 'user-row')] | //*[contains(@class, 'table-row')]")))
        row.click()
        context.button_clicked = True
    except Exception as e:
        assert False, f"Failed to click user row: {str(e)}"
    
    print(f"   >> User row clicked successfully")


@when(parsers.parse('I right-click on a user row'))
def step_right_click_user_row(context):
    """
    Right-click on a user row in the table
    """
    print(f"   >> Right-clicking on a user row")
    
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(context.driver, 10)
        # Find first clickable user row (skip header)
        row = wait.until(EC.element_to_be_clickable((By.XPATH, "//tbody//tr | //*[contains(@class, 'user-row')] | //*[contains(@class, 'table-row')]")))
        ActionChains(context.driver).context_click(row).perform()
        context.button_clicked = True
    except Exception as e:
        assert False, f"Failed to right-click user row: {str(e)}"
    
    print(f"   >> User row right-clicked successfully")


@when(parsers.parse('I click on the "{column_name}" column header'))
def step_click_column_header(context, column_name):
    """
    Click on a table column header
    Handles patterns like:
    - "I click on the First Name column header"
    - "I click on the Email column header"
    """
    print(f"   >> Clicking on column header: '{column_name}'")
    
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(context.driver, 10)
        # Find column header
        header_xpath = f"//th[contains(text(), '{column_name}')] | //thead//th[contains(text(), '{column_name}')] | //*[contains(@class, 'column-header')][contains(text(), '{column_name}')]"
        header = wait.until(EC.element_to_be_clickable((By.XPATH, header_xpath)))
        header.click()
        context.button_clicked = True
    except Exception as e:
        assert False, f"Failed to click column header '{column_name}': {str(e)}"
    
    print(f"   >> Column header clicked successfully")


@when(parsers.parse('I click on the next page arrow'))
def step_click_next_page_arrow(context):
    """
    Click on the next page arrow in pagination
    """
    print(f"   >> Clicking on next page arrow")
    
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(context.driver, 10)
        # Find next page arrow
        arrow_xpath = "//*[contains(@class, 'pagination')]//*[contains(@class, 'next')] | //*[contains(@aria-label, 'next')] | //button[contains(@aria-label, 'next')]"
        arrow = wait.until(EC.element_to_be_clickable((By.XPATH, arrow_xpath)))
        arrow.click()
        context.button_clicked = True
    except Exception as e:
        assert False, f"Failed to click next page arrow: {str(e)}"
    
    print(f"   >> Next page arrow clicked successfully")


@when(parsers.parse('I click on a Recent Meeting card'))
def step_click_recent_meeting_card(context):
    """
    Click on a Recent Meeting card
    """
    print(f"   >> Clicking on a Recent Meeting card")
    
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(context.driver, 10)
        # Find first meeting card
        card_xpath = "//*[contains(@class, 'meeting-card')] | //*[contains(@class, 'recent-meeting')] | //*[contains(text(), 'Meeting')]"
        card = wait.until(EC.element_to_be_clickable((By.XPATH, card_xpath)))
        card.click()
        context.button_clicked = True
    except Exception as e:
        assert False, f"Failed to click Recent Meeting card: {str(e)}"
    
    print(f"   >> Recent Meeting card clicked successfully")


# ==================== POPUP/DIALOG ACTIONS ====================

@when(parsers.parse('I click "{button_text}" in the popup'))
@when(parsers.parse('I click "{button_text}" in the confirmation dialog'))
@then(parsers.parse('I click "{button_text}" in the popup'))
@then(parsers.parse('I click "{button_text}" in the confirmation dialog'))
def step_click_button_in_popup(context, button_text):
    """
    Click a button in a popup or confirmation dialog
    Handles patterns like:
    - "I click Cancel in the popup"
    - "I click Confirm or Remove in the confirmation dialog"
    Uses data-attr-id pattern discovery
    """
    print(f"   >> Clicking '{button_text}' in popup/dialog")
    
    # Handle "or" patterns
    if ' or ' in button_text.lower():
        button_options = [opt.strip() for opt in button_text.split(' or ')]
        for option in button_options:
            context.button_clicked = context.button_handler.click_button(
                option,
                identifier_type='auto'
            )
            if context.button_clicked:
                print(f"   >> Clicked button in popup: '{option}'")
                break
    else:
        context.button_clicked = context.button_handler.click_button(
            button_text,
            identifier_type='auto'
        )
    
    # If not found, try finding in modal/dialog
    if not context.button_clicked:
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(context.driver, 5)  # Faster timeout
            # Find button in modal/dialog
            button_xpath = f"//*[contains(@class, 'modal') or contains(@class, 'dialog')]//button[contains(text(), '{button_text}')] | //*[contains(@role, 'dialog')]//button[contains(text(), '{button_text}')]"
            button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
            button.click()
            context.button_clicked = True
        except Exception as e:
            print(f"   >> Error clicking button in popup: {str(e)}")
    
    assert context.button_clicked, f"Failed to click '{button_text}' in popup/dialog"
    print(f"   >> Button in popup clicked successfully")


# ==================== NAVIGATION SIDEBAR ACTIONS ====================

@when(parsers.parse('I click on the "{section_name}" section in the navigation sidebar'))
def step_click_navigation_sidebar_section(context, section_name):
    """
    Click on a navigation section in the sidebar
    Handles patterns like:
    - "I click on the Firms section in the navigation sidebar"
    - "I click on the Users section in the navigation sidebar"
    Uses data-attr-id pattern discovery
    """
    print(f"   >> Clicking on navigation sidebar section: '{section_name}'")
    
    # Use the existing navigation section click logic
    context.button_clicked = context.button_handler.click_button(
        section_name,
        identifier_type='auto'
    )
    if not context.button_clicked:
        context.button_clicked = context.button_handler.click_button(
            section_name,
            identifier_type='text'
        )
    if not context.button_clicked:
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(context.driver, 5)  # Faster timeout
            # Look for navigation items in sidebar
            nav_xpath = f"//*[contains(@class, 'sidebar') or contains(@class, 'nav') or contains(@class, 'menu')]//*[contains(text(), '{section_name}')]"
            nav_item = wait.until(EC.element_to_be_clickable((By.XPATH, nav_xpath)))
            nav_item.click()
            context.button_clicked = True
        except Exception as e:
            print(f"   >> Error clicking navigation sidebar section: {str(e)}")
    
    assert context.button_clicked, f"Failed to click navigation sidebar section '{section_name}'"
    print(f"   >> Navigation sidebar section clicked successfully")


# ==================== DROPDOWN CLICK ACTIONS ====================

@when(parsers.parse('I click on the "{dropdown_text}" dropdown'))
def step_click_dropdown(context, dropdown_text):
    """
    Click on a dropdown to open it
    Handles patterns like:
    - "I click on the 10 / page dropdown"
    - "I click on the Choose Firm dropdown"
    Uses data-attr-id pattern discovery
    """
    print(f"   >> Clicking on dropdown: '{dropdown_text}'")
    
    # Try clicking as button first
    context.button_clicked = context.button_handler.click_button(
        dropdown_text,
        identifier_type='auto'
    )
    
    # If not found, try finding dropdown element
    if not context.button_clicked:
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(context.driver, 5)  # Faster timeout
            # Find dropdown by text or class
            dropdown_xpath = f"//*[contains(text(), '{dropdown_text}')] | //*[contains(@class, 'dropdown')][contains(text(), '{dropdown_text}')] | //select[contains(text(), '{dropdown_text}')]"
            dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath)))
            dropdown.click()
            context.button_clicked = True
        except Exception as e:
            print(f"   >> Error clicking dropdown: {str(e)}")
    
    assert context.button_clicked, f"Failed to click dropdown '{dropdown_text}'"
    print(f"   >> Dropdown clicked successfully")
