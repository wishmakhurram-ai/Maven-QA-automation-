"""
Quick runner script - Automatically identifies and clicks all buttons on a page
"""
import sys
import os
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework.components.button_handler import ButtonHandler
from framework.utils.driver_setup import DriverSetup

# Global URL variable - Change this to your target URL
DEFAULT_URL = "https://ant.design/components/button"


def get_button_identifier(button_handler, button, index):
    """
    Get a comprehensive identifier for a button that can be used to re-find it
    
    Returns:
        Dictionary with multiple identifiers to re-find the button
    """
    identifier = {'index': index}
    try:
        button_info = button_handler.identify_button_type(button)
        identifier['data_attr_id'] = button_info.get('data_attr_id')
        identifier['text'] = button_info.get('text', '').strip()
        identifier['type'] = button_info.get('type', 'default')
        identifier['class'] = button.get_attribute('class') or ''
        identifier['id'] = button.get_attribute('id')
        identifier['tag_name'] = button.tag_name
        identifier['href'] = button.get_attribute('href')
        
        # Get XPath for more reliable finding
        try:
            identifier['xpath'] = button_handler.execute_js("""
                function getXPath(element) {
                    if (element.id !== '') {
                        return '//*[@id="' + element.id + '"]';
                    }
                    if (element === document.body) {
                        return '/html/body';
                    }
                    var ix = 0;
                    var siblings = element.parentNode.childNodes;
                    for (var i = 0; i < siblings.length; i++) {
                        var sibling = siblings[i];
                        if (sibling === element) {
                            return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            ix++;
                        }
                    }
                }
                return getXPath(arguments[0]);
            """, button)
        except:
            identifier['xpath'] = None
        
        # Store initial info for reference
        identifier['initial_info'] = button_info
    except Exception as e:
        # Fallback: at least store index
        pass
    return identifier


def buttons_match(identifier, candidate):
    """
    Check if a candidate element matches the stored identifier
    
    Args:
        identifier: Stored button identifier
        candidate: Candidate WebElement to check
        
    Returns:
        True if candidate matches identifier
    """
    try:
        # Check data-attr-id (most unique)
        if identifier.get('data_attr_id'):
            candidate_attr = candidate.get_attribute('data-atr-id')
            if candidate_attr == identifier['data_attr_id']:
                return True
        
        # Check ID attribute
        if identifier.get('id'):
            candidate_id = candidate.get_attribute('id')
            if candidate_id and candidate_id == identifier['id']:
                return True
        
        # Check text content (exact match)
        if identifier.get('text'):
            candidate_text = (candidate.text or '').strip()
            if candidate_text and candidate_text == identifier['text']:
                # Also check tag and class to ensure it's the same button type
                if identifier.get('tag_name'):
                    if candidate.tag_name.lower() != identifier['tag_name'].lower():
                        return False
                # Check if classes match (at least ant-btn should be present)
                candidate_class = candidate.get_attribute('class') or ''
                if 'ant-btn' in candidate_class and 'ant-btn' in (identifier.get('class') or ''):
                    return True
        
        # Check href for link buttons
        if identifier.get('href'):
            candidate_href = candidate.get_attribute('href')
            if candidate_href and candidate_href == identifier['href']:
                return True
        
        # Check class signature (partial match for robustness)
        if identifier.get('class'):
            candidate_class = candidate.get_attribute('class') or ''
            identifier_class = identifier['class']
            # Check if key classes match
            key_classes = ['ant-btn']
            if identifier.get('type'):
                key_classes.append(f"ant-btn-{identifier['type']}")
            if all(cls in candidate_class for cls in key_classes if cls):
                # If text also matches, it's likely the same button
                if identifier.get('text'):
                    candidate_text = (candidate.text or '').strip()
                    if candidate_text == identifier['text']:
                        return True
    except:
        return False
    
    return False


def re_find_button(button_handler, identifier, all_buttons_cache=None):
    """
    Re-find a button using stored identifiers with multiple strategies
    
    Args:
        button_handler: ButtonHandler instance
        identifier: Dictionary with button identifiers
        all_buttons_cache: Optional cached list of all buttons
        
    Returns:
        WebElement if found, None otherwise
    """
    # Strategy 1: Try data-attr-id first (most reliable)
    if identifier.get('data_attr_id'):
        try:
            button = button_handler.find_button_by_data_attr(identifier['data_attr_id'], timeout=2)
            if button:
                return button
        except:
            pass
    
    # Strategy 2: Try by ID attribute
    if identifier.get('id'):
        try:
            from selenium.webdriver.common.by import By
            button = button_handler.find_element(By.ID, identifier['id'], timeout=2)
            if button:
                return button
        except:
            pass
    
    # Strategy 3: Try by XPath (if available)
    if identifier.get('xpath'):
        try:
            from selenium.webdriver.common.by import By
            button = button_handler.find_element(By.XPATH, identifier['xpath'], timeout=2)
            if button:
                return button
        except:
            pass
    
    # Strategy 4: Try by exact text match
    if identifier.get('text'):
        try:
            button = button_handler.find_button_by_text(identifier['text'], exact_match=True, timeout=2)
            if button:
                return button
        except:
            pass
    
    # Strategy 5: Scan all buttons and match by signature
    try:
        if all_buttons_cache is None:
            buttons = button_handler.find_all_ant_buttons(timeout=2)
        else:
            buttons = all_buttons_cache
        
        for candidate in buttons:
            if buttons_match(identifier, candidate):
                return candidate
    except:
        pass
    
    # Strategy 6: Fallback to index (if page structure hasn't changed much)
    if identifier.get('index') is not None:
        try:
            buttons = button_handler.find_all_ant_buttons(timeout=2)
            idx = identifier['index']
            if idx < len(buttons):
                # Verify it's likely the same button by checking text or class
                candidate = buttons[idx]
                if identifier.get('text'):
                    if (candidate.text or '').strip() == identifier['text']:
                        return candidate
                elif identifier.get('class'):
                    candidate_class = candidate.get_attribute('class') or ''
                    if 'ant-btn' in candidate_class:
                        return candidate
        except:
            pass
    
    return None


def click_all_buttons(page_url: str = None, delay: float = 1.0):
    """
    Automatically identify and click ALL buttons on a page
    Handles stale element references by re-finding elements
    
    Args:
        page_url: URL of the page to test
        delay: Delay between button clicks in seconds
    """
    print("=" * 70)
    print("Button Automation - Auto Click All Buttons")
    print("=" * 70)
    print()
    
    # Use global URL if not provided
    if page_url is None:
        page_url = DEFAULT_URL
    
    # Setup driver
    driver = DriverSetup.get_chrome_driver(headless=False, maximize=True)
    
    try:
        print(f"Navigating to: {page_url}")
        driver.get(page_url)
        time.sleep(2)  # Wait for page to load
        
        # Initialize button handler
        button_handler = ButtonHandler(driver)
        
        # Find all Ant Design buttons and store identifiers
        print("\n" + "-" * 70)
        print("Scanning page for Ant Design buttons...")
        print("-" * 70)
        
        buttons = button_handler.find_all_ant_buttons()
        
        if not buttons:
            print("No Ant Design buttons found on the page.")
            return
        
        print(f"\nFound {len(buttons)} button(s) on the page")
        
        # Store button identifiers to avoid stale element references
        button_identifiers = []
        for idx, button in enumerate(buttons):
            try:
                identifier = get_button_identifier(button_handler, button, idx)
                button_identifiers.append(identifier)
            except Exception as e:
                # Skip buttons we can't identify
                print(f"Warning: Could not extract identifier for button {idx+1}: {str(e)[:50]}")
                continue
        
        print(f"Stored {len(button_identifiers)} button identifier(s) for processing\n")
        
        # Identify and click each button
        clicked_count = 0
        skipped_count = 0
        
        for idx, identifier in enumerate(button_identifiers, 1):
            button = None
            button_info = None
            
            try:
                # Refresh button list cache periodically (every 10 buttons) to handle page changes
                all_buttons_cache = None
                if idx % 10 == 0 or idx == 1:
                    try:
                        all_buttons_cache = button_handler.find_all_ant_buttons(timeout=2)
                    except:
                        pass
                
                # Re-find the button right before interacting (prevents stale element errors)
                button = re_find_button(button_handler, identifier, all_buttons_cache)
                
                # If not found, try refreshing the cache and retry
                if not button:
                    try:
                        all_buttons_cache = button_handler.find_all_ant_buttons(timeout=2)
                        button = re_find_button(button_handler, identifier, all_buttons_cache)
                    except:
                        pass
                
                if not button:
                    print(f"\n[{idx}/{len(button_identifiers)}] ⚠️  SKIPPED: Could not re-find button")
                    if identifier.get('text') or identifier.get('data_attr_id'):
                        print(f"  Identifier: {identifier.get('data_attr_id') or identifier.get('text', 'Unknown')[:50]}")
                    skipped_count += 1
                    continue
                
                # Identify button type automatically (re-identify in case it changed)
                try:
                    button_info = button_handler.identify_button_type(button)
                except StaleElementReferenceException:
                    # If stale, try to re-find and re-identify
                    button = re_find_button(button_handler, identifier, identifier.get('index'))
                    if button:
                        button_info = button_handler.identify_button_type(button)
                    else:
                        button_info = identifier.get('initial_info', {})
                except:
                    # Fallback to stored info
                    button_info = identifier.get('initial_info', {})
                
                print(f"\n[{idx}/{len(button_identifiers)}] Button Information:")
                print(f"  Type: {button_info.get('type', 'unknown')}")
                print(f"  Size: {button_info.get('size', 'unknown')}")
                print(f"  Shape: {button_info.get('shape', 'unknown')}")
                print(f"  Text: '{button_info.get('text', '')}'")
                print(f"  Data-attr-id: {button_info.get('data_attr_id') or 'Not set'}")
                print(f"  Disabled: {button_info.get('disabled', False)}")
                print(f"  Loading: {button_info.get('loading', False)}")
                print(f"  Has Icon: {button_info.get('icon', False)}")
                
                # Skip disabled buttons
                if button_info.get('disabled', False):
                    print(f"  ⚠️  SKIPPED: Button is disabled")
                    skipped_count += 1
                    continue
                
                # Wait if button is loading
                if button_info.get('loading', False):
                    print(f"  ⏳ Waiting for loading to complete...")
                    try:
                        button_handler.wait_for_loading_complete(button, timeout=30)
                    except:
                        pass
                
                # Scroll button into view
                try:
                    button_handler.execute_js("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", button)
                    time.sleep(0.3)
                except:
                    pass
                
                # Click the button with retry logic for stale elements
                print(f"  🖱️  Clicking button...")
                click_success = False
                max_retries = 3
                
                for retry in range(max_retries):
                    try:
                        # Re-find button before each click attempt (especially after retries)
                        if retry > 0:
                            # Refresh cache and re-find
                            try:
                                fresh_cache = button_handler.find_all_ant_buttons(timeout=2)
                                button = re_find_button(button_handler, identifier, fresh_cache)
                            except:
                                button = re_find_button(button_handler, identifier)
                            
                            if not button:
                                # Last attempt: try all strategies again
                                if retry == max_retries - 1:
                                    break
                                time.sleep(0.3)
                                continue
                        
                        # Try normal click
                        button.click()
                        click_success = True
                        break
                    except StaleElementReferenceException:
                        if retry < max_retries - 1:
                            # Re-find and retry
                            time.sleep(0.3)
                            try:
                                fresh_cache = button_handler.find_all_ant_buttons(timeout=2)
                                button = re_find_button(button_handler, identifier, fresh_cache)
                            except:
                                button = re_find_button(button_handler, identifier)
                            continue
                        else:
                            # Last retry with JavaScript
                            try:
                                fresh_cache = button_handler.find_all_ant_buttons(timeout=2)
                                button = re_find_button(button_handler, identifier, fresh_cache)
                                if button:
                                    button_handler.execute_js("arguments[0].click();", button)
                                    click_success = True
                            except Exception as js_error:
                                error_msg = str(js_error)
                                if 'stale' not in error_msg.lower():
                                    print(f"  ❌ FAILED: Could not click button - {error_msg[:100]}")
                    except Exception as click_error:
                        # Try JavaScript click as fallback
                        try:
                            button_handler.execute_js("arguments[0].click();", button)
                            click_success = True
                            break
                        except Exception as js_error:
                            if retry == max_retries - 1:
                                error_msg = str(click_error)
                                if 'stale' not in error_msg.lower():
                                    print(f"  ❌ FAILED: Could not click button - {error_msg[:100]}")
                            else:
                                time.sleep(0.3)
                                # Re-find button for next retry
                                try:
                                    fresh_cache = button_handler.find_all_ant_buttons(timeout=2)
                                    button = re_find_button(button_handler, identifier, fresh_cache)
                                except:
                                    button = re_find_button(button_handler, identifier)
                                continue
                
                if click_success:
                    clicked_count += 1
                    print(f"  ✅ SUCCESS: Button clicked!")
                else:
                    skipped_count += 1
                
                # Wait between clicks
                if idx < len(button_identifiers):
                    time.sleep(delay)
                    
            except Exception as e:
                error_msg = str(e)
                if 'stale' in error_msg.lower():
                    print(f"  ⚠️  SKIPPED: Element became stale (page may have changed)")
                else:
                    print(f"  ❌ ERROR processing button {idx}: {error_msg[:100]}")
                skipped_count += 1
                continue
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total buttons found: {len(button_identifiers)}")
        print(f"Successfully clicked: {clicked_count}")
        print(f"Skipped/Failed: {skipped_count}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\nKeeping browser open for 5 seconds to see results...")
        time.sleep(5)
        driver.quit()
        print("Browser closed.")


if __name__ == "__main__":
    # You can change the DEFAULT_URL global variable at the top of the file
    # Or pass URL as command line argument
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = DEFAULT_URL  # Use global variable
    
    click_all_buttons(page_url=url, delay=1.0)

