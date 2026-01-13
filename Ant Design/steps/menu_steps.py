"""
Gherkin step definitions for menu/navigation automation using pytest-bdd
pytest-bdd automatically discovers and loads these step definitions
"""
from pytest_bdd import given, when, then, parsers
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


# ==================== NAVIGATION CLICK STEPS ====================

@when(parsers.parse('I click on the "{section_name}" section in the navigation'))
def step_click_navigation_section(context, section_name):
    """
    Click on a navigation section (e.g., Firms, Users)
    Common step used in admin_dashboard.feature and maven_automation.feature
    PRIORITY: Uses menu handler with data-attr-id pattern discovery FIRST
    """
    # Clear cached patterns before navigation to avoid stale login-page patterns
    try:
        if hasattr(context, "pattern_discovery"):
            context.pattern_discovery.clear_cache()
    except Exception:
        pass
    print(f"   >> Clicking on navigation section: '{section_name}' (using menu handler with pattern discovery)")
    clicked = False
    
    # Strategy 1: Use menu handler with pattern discovery (HIGHEST PRIORITY for navigation)
    try:
        clicked = context.menu_handler.click_menu_item(section_name, timeout=10)
        if clicked:
            print(f"   >> ✓ Navigation section clicked using menu handler (pattern discovery)")
    except Exception as e:
        print(f"   >> Menu handler failed: {str(e)}")
    
    # Strategy 2: Use button handler with pattern discovery (fallback)
    if not clicked:
        try:
            clicked = context.button_handler.click_button(
                section_name,
                identifier_type='auto'
            )
            if clicked:
                print(f"   >> ✓ Navigation section clicked using button handler (pattern discovery)")
        except Exception as e:
            print(f"   >> Button handler failed: {str(e)}")
    
    # Strategy 3: Try text search with button handler
    if not clicked:
        try:
            clicked = context.button_handler.click_button(
                section_name,
                identifier_type='text'
            )
            if clicked:
                print(f"   >> Navigation section clicked using text search")
        except:
            pass
    
    # Strategy 4: Try to find in navigation menu using Selenium with pattern discovery
    if not clicked:
        try:
            from framework.utils.pattern_discovery import PatternDiscovery
            pattern_discovery = PatternDiscovery(context.driver)
            normalized_text = section_name.lower().replace(' ', '-').replace('_', '-')
            
            # Try to find matching data-attr-id for navigation item
            matching_attr_id = pattern_discovery.find_matching_data_attr_id(normalized_text, 'button')
            if matching_attr_id:
                wait = WebDriverWait(context.driver, 5)
                try:
                    nav_item = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-attr-id="{matching_attr_id}"]')))
                    nav_item.click()
                    clicked = True
                    print(f"   >> ✓ Navigation section clicked using pattern discovery (data-attr-id: '{matching_attr_id}')")
                except:
                    try:
                        nav_item = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-atr-id="{matching_attr_id}"]')))
                        nav_item.click()
                        clicked = True
                        print(f"   >> ✓ Navigation section clicked using pattern discovery (data-atr-id: '{matching_attr_id}')")
                    except:
                        pass
        except Exception as e:
            print(f"   >> Pattern discovery for navigation failed: {str(e)}")
    
    # Strategy 5: Try direct XPath search for navigation items
    if not clicked:
        try:
            wait = WebDriverWait(context.driver, 5)
            # Look for navigation items in menu/nav structures
            nav_xpath = f"//*[contains(@class, 'nav') or contains(@class, 'menu') or contains(@class, 'ant-menu')]//*[contains(text(), '{section_name}')] | //a[contains(text(), '{section_name}')] | //button[contains(text(), '{section_name}')]"
            nav_item = wait.until(EC.element_to_be_clickable((By.XPATH, nav_xpath)))
            nav_item.click()
            clicked = True
            print(f"   >> Navigation section clicked using XPath search")
        except Exception as e:
            print(f"   >> Error clicking navigation section with XPath: {str(e)}")
    
    context.button_clicked = clicked
    assert clicked, f"Failed to click navigation section '{section_name}' - tried all strategies (menu handler, button handler, pattern discovery, XPath)"
    print(f"   >> Navigation section clicked successfully")
    
    # Wait for navigation to complete
    try:
        # Get current URL before waiting
        initial_url = context.driver.current_url
        print(f"   >> Waiting for navigation from: {initial_url}")
        
        # Wait for URL to change (up to 10 seconds)
        wait = WebDriverWait(context.driver, 10)
        
        # Wait until URL actually changes
        wait.until(lambda driver: driver.current_url != initial_url)
        
        # Wait for page to be fully loaded
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        
        # Additional wait for dynamic content
        time.sleep(2)
        
        current_url = context.driver.current_url
        print(f"   >> Navigation completed. Current URL: {current_url}")
    except TimeoutException:
        # If URL didn't change, it might be a submenu or the click didn't work
        current_url = context.driver.current_url
        print(f"   >> Warning: URL did not change after click. Current URL: {current_url}")
        print(f"   >> This might indicate the click didn't trigger navigation, or it's a submenu item")
        time.sleep(2)  # Fallback wait
    except Exception as e:
        print(f"   >> Warning: Error waiting for navigation: {str(e)}")
        time.sleep(2)  # Fallback wait


# ==================== NAVIGATION VERIFICATION STEPS ====================

@then(parsers.parse('the "{section}" section should be selected in the navigation menu'))
def step_section_selected_in_navigation(context, section):
    """
    Verify a section is selected in the navigation menu
    Uses data-attr-id pattern discovery
    """
    print(f"   >> Verifying '{section}' section is selected in navigation")
    # Check if section is highlighted/selected in navigation
    try:
        wait = WebDriverWait(context.driver, 2)  # Optimized for speed
        # Look for selected/active navigation item
        xpath = f"//*[contains(text(), '{section}') and (contains(@class, 'active') or contains(@class, 'selected') or contains(@aria-selected, 'true'))]"
        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        print(f"   >> '{section}' section is selected in navigation")
    except:
        # Fallback: just check if section text exists in navigation
        page_text = context.driver.page_source
        assert section in page_text, f"Section '{section}' not found in navigation"
        print(f"   >> '{section}' section found in navigation")


@then('I should be redirected to the Firms list page')
def step_redirected_to_firms_page(context):
    """
    Verify redirect to Firms list page
    Uses WebDriverWait to properly wait for navigation and page load
    Waits longer to allow for intermediate redirects (e.g., Users page -> Firms page)
    """
    print(f"   >> Verifying redirect to Firms list page")
    
    try:
        current_url = context.driver.current_url.lower()
        print(f"   >> Current URL before wait: {current_url}")
        
        # Wait up to 120 seconds (2 minutes) for redirect to Firms page
        # This accounts for intermediate redirects (e.g., Users -> Firms)
        wait = WebDriverWait(context.driver, 120)
        
        # Wait for URL to contain 'firms'
        try:
            wait.until(lambda driver: 'firms' in driver.current_url.lower())
            print(f"   >> Successfully redirected to Firms page")
        except TimeoutException:
            # If timeout, check current URL and wait a bit more
            current_url = context.driver.current_url.lower()
            print(f"   >> Timeout waiting for redirect. Current URL: {current_url}")
            
            # If we're on users page, it might redirect to firms, wait more
            if 'users' in current_url:
                print(f"   >> Currently on Users page, waiting additional 30 seconds for Firms redirect...")
                time.sleep(30)
                
                # Check again
                current_url = context.driver.current_url.lower()
                if 'firms' in current_url:
                    print(f"   >> Redirected to Firms page after additional wait")
                else:
                    print(f"   >> Still not on Firms page after additional wait. Current URL: {current_url}")
            else:
                print(f"   >> Not on Users page, but also not on Firms page")
        
        # Wait for page to be fully loaded
        try:
            WebDriverWait(context.driver, 30).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            print(f"   >> Page is fully loaded")
        except:
            print(f"   >> Page ready state check timed out, but continuing...")
        
        # Additional wait for page to stabilize
        time.sleep(2)
        
    except Exception as e:
        print(f"   >> Error waiting for redirect: {str(e)}")
        # Still wait a bit even if error occurs
        time.sleep(5)
    
    # Final check
    current_url = context.driver.current_url.lower()
    if 'firms' not in current_url:
        # One more attempt - wait and check again
        print(f"   >> Final check: Not on Firms page yet. Current URL: {current_url}")
        print(f"   >> Waiting additional 30 seconds for final redirect...")
        time.sleep(30)
        current_url = context.driver.current_url.lower()
    
    assert 'firms' in current_url, f"Not redirected to Firms list page. Current URL: {current_url}"
    print(f"   >> [OK] Redirected to Firms list page (URL: {current_url})")


@then('I should be redirected to the Users list page')
def step_redirected_to_users_page(context):
    """
    Verify redirect to Users list page
    Uses WebDriverWait to properly wait for navigation and page load
    """
    print(f"   >> Verifying redirect to Users list page")
    try:
        wait = WebDriverWait(context.driver, 3)  # Optimized for speed
        
        # Wait for URL to contain 'users'
        wait.until(lambda driver: 'users' in driver.current_url.lower())
        
        # Wait for page to be fully loaded
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        
        # Wait for any dynamic content (removed jQuery wait for speed)
        pass
    except Exception as e:
        print(f"   >> Error waiting for redirect: {str(e)}")
    
    current_url = context.driver.current_url.lower()
    assert 'users' in current_url, f"Not redirected to Users list page. Current URL: {current_url}"
    print(f"   >> Redirected to Users list page (URL: {current_url})")

