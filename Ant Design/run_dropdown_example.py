"""
Simple Python script to run dropdown automation examples
Run this directly without Gherkin: python run_dropdown_example.py
"""
from framework.utils.driver_setup import DriverSetup
from framework.components.dropdown_handler import DropdownHandler
from framework.context.element_context import ElementContext

# Ant Design Dropdown page URL
DROPDOWN_PAGE_URL = "https://ant.design/components/dropdown"


def main():
    """Main function to demonstrate dropdown automation"""
    print("="*70)
    print("DROPDOWN AUTOMATION EXAMPLE")
    print("="*70)
    
    # Setup driver
    print("\n>>> Setting up Chrome driver...")
    driver = DriverSetup.get_chrome_driver(headless=False, maximize=True)
    
    try:
        # Create context and handler
        context = ElementContext()
        dropdown_handler = DropdownHandler(driver, context=context)
        
        # Navigate to dropdown page
        print(f"\n>>> Navigating to: {DROPDOWN_PAGE_URL}")
        driver.get(DROPDOWN_PAGE_URL)
        print(">>> Page loaded successfully")
        
        # Wait for page to fully load and scroll to see examples
        import time
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        print(">>> Waiting for page to load...")
        # Wait for page to be ready
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(3)  # Additional wait for dynamic content
        
        # Scroll down to see examples
        print(">>> Scrolling to see examples...")
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 1500);")
        time.sleep(1)
        
        # Example 1: Print summary of all dropdowns
        print("\n" + "="*70)
        print("EXAMPLE 1: Print summary of all dropdowns")
        print("="*70)
        
        # First, let's see what we can find
        print(">>> Searching for dropdown elements...")
        all_dropdowns = dropdown_handler.find_all_ant_dropdowns(include_all=True)
        print(f">>> Found {len(all_dropdowns)} dropdown elements")
        
        if len(all_dropdowns) == 0:
            print(">>> No dropdowns found. Trying alternative detection...")
            # Try to find any elements that might be dropdowns
            try:
                from selenium.webdriver.common.by import By
                # Look for common dropdown patterns
                test_selectors = [
                    ('span[class*="dropdown"]', 'span with dropdown class'),
                    ('button[class*="dropdown"]', 'button with dropdown class'),
                    ('div[class*="dropdown"]', 'div with dropdown class'),
                    ('[aria-haspopup="menu"]', 'aria-haspopup menu'),
                    ('[role="button"]', 'role button'),
                    ('span.ant-dropdown-trigger', 'ant-dropdown-trigger span'),
                    ('button.ant-dropdown-trigger', 'ant-dropdown-trigger button'),
                    ('[class*="ant-dropdown-trigger"]', 'any ant-dropdown-trigger'),
                    ('span:contains("Hover me")', 'Hover me text'),
                    ('button:contains("Click me")', 'Click me text'),
                ]
                for selector, desc in test_selectors:
                    try:
                        if ':contains(' in selector:
                            # Use XPath for text contains
                            text = selector.split('"')[1]
                            tag = selector.split(':')[0]
                            xpath = f"//{tag}[contains(text(), '{text}')]"
                            test_elems = driver.find_elements(By.XPATH, xpath)
                        else:
                            test_elems = driver.find_elements(By.CSS_SELECTOR, selector)
                        if test_elems:
                            print(f">>> Found {len(test_elems)} elements: {desc}")
                            for idx, elem in enumerate(test_elems[:5], 1):
                                try:
                                    class_attr = elem.get_attribute('class') or 'None'
                                    text_content = elem.text[:50] if elem.text else 'None'
                                    print(f"  Element {idx}: tag={elem.tag_name}, class={class_attr[:60]}, text={text_content}")
                                except:
                                    pass
                    except Exception as e:
                        print(f">>> Error with selector '{desc}': {str(e)}")
                
                # Also try JavaScript to find elements
                print("\n>>> Trying JavaScript detection...")
                js_result = driver.execute_script("""
                    var elements = [];
                    // Find all elements with dropdown-related classes
                    var selectors = [
                        '.ant-dropdown-trigger',
                        '[class*="ant-dropdown"]',
                        '[aria-haspopup="menu"]',
                        'span:contains("Hover me")',
                        'button:contains("Click me")'
                    ];
                    
                    // Try querySelectorAll for each
                    document.querySelectorAll('.ant-dropdown-trigger, [class*="ant-dropdown"], [aria-haspopup="menu"]').forEach(function(el) {
                        if (el.offsetParent !== null) { // Check if visible
                            elements.push({
                                tag: el.tagName,
                                class: el.className,
                                text: el.textContent.trim().substring(0, 50),
                                id: el.id || 'no-id'
                            });
                        }
                    });
                    
                    return elements.slice(0, 10);
                """)
                if js_result:
                    print(f">>> JavaScript found {len(js_result)} potential dropdown elements:")
                    for idx, elem_info in enumerate(js_result, 1):
                        print(f"  {idx}. {elem_info['tag']} - class: {elem_info['class'][:60]}, text: {elem_info['text']}")
            except Exception as e:
                print(f">>> Error in alternative detection: {str(e)}")
                import traceback
                traceback.print_exc()
        
        dropdown_handler.print_dropdowns_summary(include_all=True)
        
        # Example 2: Find dropdown by label and interact with it
        print("\n" + "="*70)
        print("EXAMPLE 2: Find dropdown by label and interact with it")
        print("="*70)
        
        # Try to find a dropdown by label
        try:
            # Try to find dropdown by label "Hover me" or "Click me"
            for label in ["Hover me", "Click me", "Cascading menu"]:
                dropdown = dropdown_handler.find_dropdown_by_label(label, exact_match=False)
                if dropdown:
                    print(f">>> Found dropdown with label '{label}'")
                    # Get dropdown info
                    dropdown_info = dropdown_handler.identify_dropdown_type(dropdown)
                    print(f">>> Dropdown type: {dropdown_info.get('type')}")
                    print(f">>> Dropdown disabled: {dropdown_info.get('disabled')}")
                    
                    # Try to select an option from the dropdown
                    if dropdown_info.get('type') == 'dropdown':
                        print(f">>> This is a Dropdown menu component - attempting to select first option...")
                        # Try to select first option (empty string or "first" will select first item)
                        success = dropdown_handler.select_by_text(label, "", identifier_type='label')
                        if success:
                            print(">>> Successfully selected option from dropdown menu")
                        else:
                            # Try with "first" as option text
                            success = dropdown_handler.select_by_text(label, "first", identifier_type='label')
                            if success:
                                print(">>> Successfully selected first option from dropdown menu")
                            else:
                                print(">>> Could not select option")
                    else:
                        # For Select components, try selecting first option
                        success = dropdown_handler.select_first_in(label, identifier_type='label')
                        if success:
                            print(">>> Successfully selected first option")
                        else:
                            print(">>> Could not select option")
                    break
            else:
                print(">>> Could not find any testable dropdowns")
        except Exception as e:
            print(f">>> Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Example 3: Identify and store dropdown in context
        print("\n" + "="*70)
        print("EXAMPLE 3: Identify and store dropdown in context")
        print("="*70)
        
        try:
            # Try to identify a dropdown by type
            success = dropdown_handler.identify_and_store("single", identifier_type='type')
            if success:
                print(">>> Successfully identified and stored 'single' type dropdown in context")
                
                # Get all keys in context
                all_keys = context.get_all_keys()
                print(f">>> Context keys: {all_keys}")
                
                # Try to select from context
                if all_keys:
                    context_key = all_keys[0]
                    print(f">>> Attempting to select option from context key: '{context_key}'")
                    # Note: This will try to select, but might fail if dropdown has no options
                    # or is in a demo state
            else:
                print(">>> Could not identify dropdown")
        except Exception as e:
            print(f">>> Error: {str(e)}")
        
        # Example 4: Automatically interact with ALL dropdowns
        print("\n" + "="*70)
        print("EXAMPLE 4: Automatically interact with ALL dropdowns")
        print("="*70)
        
        # Scroll more to load all content
        print(">>> Scrolling page to load all dropdowns...")
        for scroll_pos in [0, 500, 1000, 1500, 2000, 2500, 3000]:
            driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
            time.sleep(0.5)
        
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        all_dropdowns = dropdown_handler.find_all_ant_dropdowns(include_all=True)
        print(f">>> Found {len(all_dropdowns)} dropdowns on the page")
        
        # Print details of found dropdowns
        if all_dropdowns:
            print(f">>> Dropdown details:")
            for idx, dd in enumerate(all_dropdowns[:10], 1):  # Show first 10
                try:
                    dd_info = dropdown_handler.identify_dropdown_type(dd)
                    label = dd_info.get('label') or dd_info.get('placeholder') or f"Dropdown #{idx}"
                    dd_type = dd_info.get('type', 'unknown')
                    print(f"  {idx}. {label[:40]} (type: {dd_type})")
                except:
                    print(f"  {idx}. Dropdown #{idx} (could not identify)")
        
        print(f"\n>>> Attempting to interact with each dropdown...\n")
        
        success_count = 0
        skipped_count = 0
        failed_count = 0
        
        for idx, dropdown in enumerate(all_dropdowns, 1):
            try:
                # Handle stale element references by re-finding if needed
                try:
                    dropdown_info = dropdown_handler.identify_dropdown_type(dropdown)
                except Exception as stale_error:
                    if 'stale' in str(stale_error).lower():
                        print(f"  Dropdown #{idx}: Stale element, skipping...")
                        failed_count += 1
                        continue
                    else:
                        raise
                
                dropdown_type = dropdown_info.get('type')
                dropdown_label = dropdown_info.get('label') or dropdown_info.get('placeholder') or f"Dropdown #{idx}"
                
                print(f"  Dropdown #{idx}: {dropdown_label[:30]} (type: {dropdown_type})")
                
                # Skip disabled or loading dropdowns
                if dropdown_info.get('disabled'):
                    print(f"    >> SKIPPED: Dropdown is disabled")
                    skipped_count += 1
                    continue
                
                if dropdown_info.get('loading'):
                    print(f"    >> SKIPPED: Dropdown is loading")
                    skipped_count += 1
                    continue
                
                # Try to select an option directly using the element
                try:
                    # Handle stale element - verify element is still valid
                    try:
                        _ = dropdown.is_displayed()
                    except:
                        # Try to re-find the element
                        print(f"    >> WARNING: Stale element, attempting to re-find...")
                        try:
                            # Re-find by scrolling and searching again
                            driver.execute_script("window.scrollTo(0, arguments[0]);", idx * 200)
                            time.sleep(0.5)
                            all_dropdowns_refresh = dropdown_handler.find_all_ant_dropdowns(include_all=True)
                            if idx <= len(all_dropdowns_refresh):
                                dropdown = all_dropdowns_refresh[idx - 1]
                                dropdown_info = dropdown_handler.identify_dropdown_type(dropdown)
                                dropdown_type = dropdown_info.get('type')
                                dropdown_label = dropdown_info.get('label') or dropdown_info.get('placeholder') or f"Dropdown #{idx}"
                                print(f"    >> Re-found dropdown: {dropdown_label[:30]}")
                            else:
                                print(f"    >> SKIPPED: Could not re-find element")
                                skipped_count += 1
                                continue
                        except:
                            print(f"    >> SKIPPED: Could not re-find stale element")
                            skipped_count += 1
                            continue
                    
                    # Scroll into view first
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", dropdown)
                    time.sleep(0.8)  # Longer wait for smooth scroll
                    
                    # For Dropdown menu components, select first option directly
                    if dropdown_type == 'dropdown':
                        # Use the handler's _select_from_dropdown_menu method directly
                        success = dropdown_handler._select_from_dropdown_menu(dropdown, "")
                        if success:
                            print(f"    >> SUCCESS: Selected option from dropdown menu")
                            success_count += 1
                        else:
                            print(f"    >> FAILED: Could not select option")
                            failed_count += 1
                    else:
                        # For Select components, try selecting first option
                        try:
                            # Try to open and select first option
                            from selenium.webdriver.support.ui import Select
                            if dropdown.tag_name.lower() == 'select':
                                select = Select(dropdown)
                                if len(select.options) > 0:
                                    # Skip empty options
                                    for opt_idx in range(len(select.options)):
                                        option = select.options[opt_idx]
                                        if option.text.strip():
                                            select.select_by_index(opt_idx)
                                            print(f"    >> SUCCESS: Selected first option: '{option.text.strip()}'")
                                            success_count += 1
                                            break
                                    else:
                                        print(f"    >> FAILED: No non-empty options available")
                                        failed_count += 1
                                else:
                                    print(f"    >> FAILED: No options available")
                                    failed_count += 1
                            else:
                                # Ant Design Select - try to get options and select first
                                try:
                                    # Open dropdown first
                                    dropdown_handler._open_dropdown(dropdown)
                                    time.sleep(1)
                                    # Get available options
                                    options = dropdown_handler._get_available_options_with_retry(dropdown, timeout=5)
                                    if options:
                                        # Select first option
                                        success = dropdown_handler._select_option(dropdown, options[0], clear_first=False)
                                        if success:
                                            print(f"    >> SUCCESS: Selected first option: '{options[0]}'")
                                            success_count += 1
                                        else:
                                            print(f"    >> FAILED: Could not select option")
                                            failed_count += 1
                                    else:
                                        print(f"    >> FAILED: No options available")
                                        failed_count += 1
                                except Exception as e:
                                    print(f"    >> FAILED: Error - {str(e)[:50]}")
                                    failed_count += 1
                        except Exception as e:
                            print(f"    >> FAILED: Error selecting option - {str(e)[:50]}")
                            failed_count += 1
                    
                    time.sleep(0.5)  # Small delay between interactions
                    
                except Exception as e:
                    print(f"    >> FAILED: {str(e)[:50]}")
                    failed_count += 1
                    
            except Exception as e:
                print(f"  Dropdown #{idx}: Error - {str(e)[:50]}")
                failed_count += 1
        
        print(f"\n" + "="*70)
        print(f"SUMMARY:")
        print(f"  Total dropdowns: {len(all_dropdowns)}")
        print(f"  Successfully interacted: {success_count}")
        print(f"  Skipped (disabled/loading): {skipped_count}")
        print(f"  Failed: {failed_count}")
        print("="*70)
        
        print("\n" + "="*70)
        print("EXAMPLES COMPLETE")
        print("="*70)
        print("\n>>> Keeping browser open for 10 seconds for inspection...")
        time.sleep(10)
        
    except Exception as e:
        print(f"\n>>> Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n>>> Closing browser...")
        driver.quit()
        print(">>> Done!")


if __name__ == "__main__":
    main()

