"""
Production-Ready TreeSelect Automation Script
STRICTLY follows critical TreeSelect interaction rules
"""
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from framework.components.treeselect_handler import TreeSelectHandler
from framework.context.element_context import ElementContext
from framework.utils.driver_setup import DriverSetup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# Ant Design TreeSelect page URL
TREESELECT_PAGE_URL = "https://ant.design/components/tree-select"


def close_all_dropdowns(driver):
    """Close all open TreeSelect dropdowns"""
    try:
        open_dropdowns = driver.find_elements(By.CSS_SELECTOR, 
            '.ant-select-dropdown:not([style*="display: none"])')
        for dd in open_dropdowns:
            try:
                driver.execute_script("arguments[0].style.display = 'none';", dd)
            except:
                pass
        driver.find_element(By.TAG_NAME, 'body').click()
        time.sleep(0.5)
        return True
    except:
        return False


def _click_tree_node_comprehensive(driver, tree_node, wrapper):
    """Helper: Click tree node with comprehensive event sequence"""
    driver.execute_script("""
        var node = arguments[0];
        var wrapper = arguments[1];
        node.scrollIntoView({block: 'center', behavior: 'auto'});
        wrapper.scrollIntoView({block: 'center', behavior: 'auto'});
        var rect = node.getBoundingClientRect();
        var x = rect.left + rect.width / 2;
        var y = rect.top + rect.height / 2;
        var mouseDown = new MouseEvent('mousedown', {
            bubbles: true, cancelable: true, view: window, button: 0,
            clientX: x, clientY: y
        });
        var mouseUp = new MouseEvent('mouseup', {
            bubbles: true, cancelable: true, view: window, button: 0,
            clientX: x, clientY: y
        });
        var clickEvent = new MouseEvent('click', {
            bubbles: true, cancelable: true, view: window, button: 0,
            clientX: x, clientY: y
        });
        node.dispatchEvent(mouseDown);
        node.dispatchEvent(mouseUp);
        node.dispatchEvent(clickEvent);
        wrapper.dispatchEvent(mouseDown);
        wrapper.dispatchEvent(mouseUp);
        wrapper.dispatchEvent(clickEvent);
        if (typeof node.click === 'function') node.click();
        if (typeof wrapper.click === 'function') wrapper.click();
    """, tree_node, wrapper)
    try:
        tree_node.click()
    except:
        pass
    try:
        wrapper.click()
    except:
        pass


def _check_selection_items(treeselect, node_text):
    """Helper: Check if selection items contain node text"""
    try:
        selection_items = treeselect.find_elements(By.CSS_SELECTOR, 
            '.ant-select-selection-item, [class*="selection-item"]')
        for item in selection_items:
            item_text = item.text or item.get_attribute('title') or ''
            if item_text and (node_text.lower() in item_text.lower() or 
                            any(word in item_text.lower() for word in node_text.lower().split())):
                return True, item_text
        return False, None
    except:
        return False, None


def _check_dropdown_closed(driver):
    """Helper: Check if dropdown is closed"""
    try:
        driver.find_element(By.CSS_SELECTOR, 
            '.ant-select-dropdown:not([style*="display: none"])')
        return False
    except:
        return True


def verify_dropdown_ownership(driver, treeselect, dropdown):
    """
    Verify that the dropdown belongs to the clicked TreeSelect
    Uses multiple validation methods as per critical rules
    """
    try:
        # Method 1: Check aria-controls relationship
        treeselect_id = treeselect.get_attribute('id')
        if treeselect_id:
            dropdown_aria_controls = dropdown.get_attribute('aria-controls')
            if dropdown_aria_controls and treeselect_id in dropdown_aria_controls:
                return True
        
        # Method 2: Check DOM proximity (dropdown should be near TreeSelect)
        treeselect_loc = treeselect.location
        dropdown_loc = dropdown.location
        
        # Dropdown should be near TreeSelect (within reasonable distance)
        x_diff = abs(dropdown_loc['x'] - treeselect_loc['x'])
        y_diff = abs(dropdown_loc['y'] - treeselect_loc['y'])
        
        # Dropdown typically appears below or near the TreeSelect
        if x_diff < 300 and y_diff < 500:
            return True
        
        # Method 3: Check if TreeSelect has focus/active state
        try:
            is_focused = driver.execute_script("""
                var elem = arguments[0];
                return document.activeElement === elem || elem === document.activeElement.closest('.ant-select');
            """, treeselect)
            if is_focused:
                return True
        except:
            pass
        
        # Method 4: Check timing - dropdown appeared right after click
        # (This is handled by the fact we just clicked it)
        
        # If we can't verify, be conservative - assume it might not belong
        # But allow it if it's the only dropdown and close to TreeSelect
        all_dropdowns = driver.find_elements(By.CSS_SELECTOR, 
            '.ant-select-dropdown:not([style*="display: none"])')
        if len(all_dropdowns) == 1 and x_diff < 500:
            return True
        
        return False
    except:
        return False


def find_treeselects_in_examples_section(driver, treeselect_handler):
    """Find TreeSelect components ONLY in the Examples section - STRICT MODE"""
    all_treeselects = []
    seen_keys = set()
    
    def get_unique_key(element):
        """Generate a unique key for an element"""
        try:
            elem_id = element.get_attribute('id')
            if elem_id:
                return f"id_{elem_id}"
            data_attr = element.get_attribute('data-attr-id') or element.get_attribute('data-atr-id')
            if data_attr:
                return f"data_{data_attr}"
            loc = element.location
            size = element.size
            tag = element.tag_name
            x_rounded = round(loc['x'] / 10) * 10
            y_rounded = round(loc['y'] / 10) * 10
            return f"loc_{x_rounded}_{y_rounded}_{size['width']}_{size['height']}_{tag}"
        except:
            try:
                return f"obj_{id(element)}"
            except:
                return None
    
    # STRICT: Find Examples section by heading and get only that section
    examples_section = None
    try:
        print(">>> Searching for Examples section heading...")
        
        # Strategy 1: Find "Examples" heading (h2 or h3)
        try:
            examples_heading = driver.find_element(By.XPATH, 
                "//h2[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'example')] | " +
                "//h3[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'example')]")
            
            # Get the parent section/article that contains examples
            examples_section = examples_heading.find_element(By.XPATH, 
                "./following-sibling::*[1] | " +
                "./ancestor::article[1] | " +
                "./ancestor::section[1] | " +
                "./ancestor::div[contains(@class, 'markdown')][1]")
            
            print(">>> Found Examples section via heading")
        except:
            pass
        
        # Strategy 2: Find main content area and look for code-box-demo within it
        if not examples_section:
            try:
                # Find main content
                main_content = driver.find_element(By.CSS_SELECTOR, 
                    'main, article, [class*="main-content"], [class*="site-layout-content"]')
                
                # Within main content, find code-box-demo containers
                code_box_demos = main_content.find_elements(By.CSS_SELECTOR, 
                    '[class*="code-box-demo"]')
                
                if code_box_demos:
                    # Use the first code-box-demo's parent as the examples section
                    examples_section = code_box_demos[0].find_element(By.XPATH, 
                        "./ancestor::*[contains(@class, 'markdown') or contains(@class, 'article') or self::article or self::section][1]")
                    print(">>> Found Examples section via code-box-demo")
            except:
                pass
        
        # Strategy 3: Directly find code-box-demo containers (strict - only these)
        if not examples_section:
            try:
                code_box_demos = driver.find_elements(By.CSS_SELECTOR, 
                    '[class*="code-box-demo"]')
                
                if code_box_demos:
                    # Get the common parent of all code-box-demos
                    # This should be the Examples section
                    examples_section = code_box_demos[0].find_element(By.XPATH, 
                        "./ancestor::*[contains(@class, 'markdown') or contains(@class, 'article') or self::article or self::section][1]")
                    print(">>> Found Examples section via code-box-demo containers")
            except:
                pass
        
        if not examples_section:
            print(">>> WARNING: Could not find Examples section, will search only in code-box-demo containers")
        
    except Exception as e:
        print(f">>> Error finding Examples section: {str(e)[:100]}")
    
    # STRICT: Only search within code-box-demo containers (these are the actual examples)
    try:
        print(">>> Searching ONLY in code-box-demo containers (STRICT MODE - NO PAGE SCAN)...")
        
        # Find ALL code-box-demo containers on the page
        code_box_demos = driver.find_elements(By.CSS_SELECTOR, 
            '[class*="code-box-demo"]')
        
        print(f">>> Found {len(code_box_demos)} code-box-demo containers")
        
        for code_box_demo in code_box_demos:
            try:
                # Find all ant-select elements ONLY in this code-box-demo
                selects = code_box_demo.find_elements(By.CSS_SELECTOR, 
                    '.ant-select, [class*="ant-select"]')
                
                for select in selects:
                    try:
                        if not select.is_displayed():
                            continue
                        
                        # STRICT: Skip contributors, navigation, header elements
                        ts_id = (select.get_attribute('id') or '').lower()
                        if 'contributors' in ts_id or 'nav' in ts_id or 'header' in ts_id:
                            continue
                        
                        # STRICT: Verify it's actually in a code-box-demo (double check)
                        try:
                            demo_parent = select.find_element(By.XPATH, 
                                "./ancestor::*[contains(@class, 'code-box-demo')][1]")
                            # Verify it's the same container we're iterating over
                            if demo_parent != code_box_demo:
                                continue  # Not in the expected container
                        except:
                            continue  # Not in code-box-demo at all
                        
                        # Verify it's a TreeSelect
                        if not treeselect_handler.locator._is_treeselect(select):
                            continue
                        
                        unique_key = get_unique_key(select)
                        if unique_key and unique_key not in seen_keys:
                            seen_keys.add(unique_key)
                            all_treeselects.append(select)
                    except:
                        continue
            except:
                continue
                
    except Exception as e:
        print(f">>> Error searching in Examples section: {str(e)[:100]}")
    
    # Sort by Y position (top to bottom)
    try:
        all_treeselects.sort(key=lambda x: (x.location['y'], x.location['x']))
    except:
        pass
    
    print(f">>> Total TreeSelects found in Examples section ONLY: {len(all_treeselects)}")
    return all_treeselects


def select_node_from_dropdown(driver, treeselect, dropdown, treeselect_handler):
    """Attempt to select a node from the verified dropdown"""
    try:
        time.sleep(1.5)  # Wait for tree to render
        
        # Check if dropdown is empty
        try:
            empty_indicator = dropdown.find_elements(By.CSS_SELECTOR, 
                '.ant-select-empty, .ant-empty, [class*="empty"]')
            if empty_indicator:
                tree_nodes = dropdown.find_elements(By.CSS_SELECTOR, 'li.ant-tree-node')
                if not tree_nodes:
                    return False, "Empty dropdown (no tree nodes)", True
        except:
            pass
        
        # Find tree nodes
        tree_nodes = []
        try:
            nodes = dropdown.find_elements(By.CSS_SELECTOR, 
                'li.ant-tree-node, [role="treeitem"], .ant-tree-treenode')
            for node in nodes:
                try:
                    wrapper = None
                    for wrapper_sel in ['.ant-tree-node-content-wrapper', 
                                       '[class*="content-wrapper"]',
                                       '.ant-tree-title',
                                       'span']:
                        try:
                            wrapper = node.find_element(By.CSS_SELECTOR, wrapper_sel)
                            if wrapper.is_displayed():
                                break
                        except:
                            continue
                    
                    if not wrapper:
                        continue
                    
                    node_text = driver.execute_script("""
                        var node = arguments[0];
                        var title = node.querySelector('.ant-tree-title, [class*="title"]');
                        if (title) return title.textContent.trim();
                        var wrapper = node.querySelector('.ant-tree-node-content-wrapper');
                        if (wrapper) return wrapper.textContent.trim();
                        return node.textContent.trim();
                    """, node)
                    
                    if node_text and len(node_text) > 0:
                        skip_texts = ['contributors', 'aojunhao123', 'thinkasany']
                        if node_text.lower() not in skip_texts:
                            tree_nodes.append({
                                'node': node,
                                'wrapper': wrapper,
                                'text': node_text
                            })
                except:
                    continue
        except:
            pass
        
        if not tree_nodes:
            # Check if dropdown is truly empty (no nodes at all)
            # This is a valid skip condition
            return False, "No selectable tree nodes found (empty dropdown)", True
        
        # MANDATORY SELECTION: Must select at least one node
        # Try ALL available nodes if needed (not just first 5)
        max_attempts = min(len(tree_nodes), 10)  # Try up to 10 nodes
        for node_info in tree_nodes[:max_attempts]:
            try:
                wrapper = node_info['wrapper']
                node_text = node_info['text']
                
                print(f">>> Attempting to select: '{node_text[:50]}'")
                
                # Scroll wrapper into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'auto'});", wrapper)
                time.sleep(0.3)
                
                # CRITICAL: Store initial state to verify change
                initial_value = ""
                try:
                    value_elem = treeselect.find_element(By.CSS_SELECTOR, 
                        'input, .ant-select-selection-item')
                    initial_value = value_elem.get_attribute('value') or value_elem.text or ''
                except:
                    pass
                try:
                    initial_selection_count = len(treeselect.find_elements(By.CSS_SELECTOR, 
                        '.ant-select-selection-item'))
                except:
                    initial_selection_count = 0
                
                # CRITICAL: Click on the actual tree node (li element), not just wrapper
                tree_node = node_info['node']
                
                # Click tree node with comprehensive events
                _click_tree_node_comprehensive(driver, tree_node, wrapper)
                
                # Also try clicking title element
                try:
                    title_elem = wrapper.find_element(By.CSS_SELECTOR, 
                        '.ant-tree-title, [class*="title"]')
                    driver.execute_script("""
                        var title = arguments[0];
                        title.scrollIntoView({block: 'center', behavior: 'auto'});
                        var clickEvent = new MouseEvent('click', {
                            bubbles: true, cancelable: true, view: window, button: 0
                        });
                        title.dispatchEvent(clickEvent);
                        title.click();
                    """, title_elem)
                except:
                    pass
                
                time.sleep(2.5)  # Wait for selection to register
                
                # CRITICAL VERIFICATION: Check success with multiple methods
                # Method 1: Check if dropdown closed (single-select mode) - STRONGEST INDICATOR
                if _check_dropdown_closed(driver):
                    print(f">>> SUCCESS: Dropdown closed - selection confirmed (single-select mode)")
                    return True, f"Selected: {node_text}", False
                
                # Method 2: Check if value CHANGED in input (for single-select)
                try:
                    value_elem = treeselect.find_element(By.CSS_SELECTOR, 
                        'input.ant-select-selection-search-input, input')
                    new_value = value_elem.get_attribute('value') or ''
                    if new_value and new_value != initial_value:
                        if node_text.lower() in new_value.lower() or any(word in new_value.lower() for word in node_text.lower().split()):
                            print(f">>> SUCCESS: Value changed in input: '{new_value[:50]}'")
                            return True, f"Selected: {node_text}", False
                except:
                    pass
                
                # Method 3: Check if selection items COUNT INCREASED or contain our text
                try:
                    current_selection_items = treeselect.find_elements(By.CSS_SELECTOR, 
                        '.ant-select-selection-item, [class*="selection-item"]')
                    current_count = len(current_selection_items)
                    
                    if current_count > initial_selection_count:
                        # Check if new item contains our text
                        found, item_text = _check_selection_items(treeselect, node_text)
                        if found:
                            print(f">>> SUCCESS: New selection item appeared: '{item_text[:50]}'")
                            return True, f"Selected: {node_text}", False
                        # Count increased = selection happened
                        print(f">>> SUCCESS: Selection count increased from {initial_selection_count} to {current_count}")
                        return True, f"Selected: {node_text} (count increased)", False
                    
                    # Check if any existing item contains our text
                    found, item_text = _check_selection_items(treeselect, node_text)
                    if found:
                        print(f">>> SUCCESS: Selection item found: '{item_text[:50]}'")
                        return True, f"Selected: {node_text}", False
                except:
                    pass
                
                # Method 3: Check if node is marked as selected (for multiple/checkable mode)
                try:
                    # Check wrapper classes
                    wrapper_classes = driver.execute_script("""
                        var wrapper = arguments[0];
                        return wrapper.className || '';
                    """, wrapper)
                    
                    # Check parent node classes
                    parent_classes = driver.execute_script("""
                        var wrapper = arguments[0];
                        var parent = wrapper.closest('li.ant-tree-node');
                        return parent ? (parent.className || '') : '';
                    """, wrapper)
                    
                    # Check for selected indicators
                    if ('ant-tree-node-selected' in wrapper_classes or 
                        'ant-tree-node-selected' in parent_classes or
                        'selected' in wrapper_classes.lower() or
                        'ant-tree-node-selected' in str(node_info['node'].get_attribute('class') or '')):
                        print(f">>> SUCCESS: Node marked as selected")
                        return True, f"Selected: {node_text} (multiple/checkable mode)", False
                except:
                    pass
                
                # Method 4: Check if checkbox is checked (for checkable mode)
                try:
                    checkbox = node_info['node'].find_element(By.CSS_SELECTOR, 
                        '.ant-tree-checkbox, [class*="checkbox"]')
                    is_checked = driver.execute_script("""
                        var checkbox = arguments[0];
                        return checkbox.classList.contains('ant-tree-checkbox-checked') || 
                               checkbox.getAttribute('aria-checked') === 'true' ||
                               checkbox.classList.contains('checked');
                    """, checkbox)
                    if is_checked:
                        print(f">>> SUCCESS: Checkbox checked - selection confirmed")
                        return True, f"Selected: {node_text} (checkable mode)", False
                except:
                    pass
                
                # Method 5: For multiple mode, if dropdown still open, try additional click
                if not _check_dropdown_closed(driver):
                    print(f">>> Dropdown still open, trying additional click on node...")
                    try:
                        before_click_count = len(treeselect.find_elements(By.CSS_SELECTOR, 
                            '.ant-select-selection-item'))
                        
                        # Click again with comprehensive events
                        _click_tree_node_comprehensive(driver, tree_node, wrapper)
                        time.sleep(2.5)
                        
                        # Check if dropdown closed
                        if _check_dropdown_closed(driver):
                            print(f">>> SUCCESS: Dropdown closed after additional click")
                            return True, f"Selected: {node_text}", False
                        
                        # Check if selection count increased
                        try:
                            after_click_count = len(treeselect.find_elements(By.CSS_SELECTOR, 
                                '.ant-select-selection-item'))
                            if after_click_count > before_click_count:
                                print(f">>> SUCCESS: Selection count increased from {before_click_count} to {after_click_count}")
                                return True, f"Selected: {node_text} (count increased)", False
                            
                            # Check if item contains our text
                            found, item_text = _check_selection_items(treeselect, node_text)
                            if found:
                                print(f">>> SUCCESS: Selection item found: '{item_text[:50]}'")
                                return True, f"Selected: {node_text}", False
                        except:
                            pass
                        
                        # Check if node is marked as selected
                        try:
                            node_classes = driver.execute_script("return arguments[0].className || '';", tree_node)
                            if 'ant-tree-node-selected' in node_classes:
                                print(f">>> SUCCESS: Node marked as selected after additional click")
                                return True, f"Selected: {node_text} (node marked selected)", False
                        except:
                            pass
                        
                        # Check checkbox state
                        try:
                            checkbox = tree_node.find_element(By.CSS_SELECTOR, 
                                '.ant-tree-checkbox, [class*="checkbox"]')
                            is_checked = driver.execute_script("""
                                var cb = arguments[0];
                                return cb.classList.contains('ant-tree-checkbox-checked') || 
                                       cb.getAttribute('aria-checked') === 'true';
                            """, checkbox)
                            if is_checked:
                                print(f">>> SUCCESS: Checkbox checked after additional click")
                                return True, f"Selected: {node_text} (checkbox checked)", False
                        except:
                            pass
                        
                        # Check for selected nodes in dropdown
                        try:
                            selected_nodes = dropdown.find_elements(By.CSS_SELECTOR, 
                                'li.ant-tree-node-selected, [class*="selected"]')
                            if selected_nodes:
                                print(f">>> SUCCESS: Found {len(selected_nodes)} selected node(s) in dropdown")
                                return True, f"Selected: {node_text} (multiple/checkable mode)", False
                        except:
                            pass
                        
                        print(f">>> WARNING: Could not verify selection after additional click")
                    except Exception as e:
                        print(f">>> Error in additional click: {str(e)[:50]}")
                        # Continue to next node
                
            except Exception as e:
                print(f">>> Error selecting node '{node_info.get('text', 'unknown')[:50]}': {str(e)[:50]}")
                continue
        
        # MANDATORY SELECTION FAILURE: Tried all available nodes but none could be selected
        # This is a critical failure - dropdown opened but no selection was made
        return False, f"Tried {len(tree_nodes)} node(s) but could not confirm any selection", False
        
    except Exception as e:
        # Exception during selection attempt - this is also a failure
        return False, f"Exception during selection: {str(e)[:100]}", False


def main():
    print("="*70)
    print("PRODUCTION-READY TreeSelect Automation - Complete Report")
    print("STRICTLY Following Critical Interaction Rules")
    print("="*70)

    driver = DriverSetup.get_chrome_driver(headless=False, maximize=True)

    stats = {
        'total_found': 0,
        'total_processed': 0,
        'successfully_opened': 0,
        'successfully_selected': 0,
        'empty_dropdowns': 0,
        'skipped_disabled': 0,
        'skipped_no_dropdown': 0,
        'failed': 0,
        'details': []
    }

    try:
        context = ElementContext()
        treeselect_handler = TreeSelectHandler(driver, context=context)

        print(f"\nNavigating to: {TREESELECT_PAGE_URL}")
        try:
            driver.get(TREESELECT_PAGE_URL)
            print(">>> Waiting for page to load...")
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(4)
        except Exception as e:
            print(f">>> Warning: Page load issue: {str(e)[:100]}")
            time.sleep(5)  # Wait anyway
        
        print(">>> Scrolling to load all TreeSelect components...")
        try:
            # Scroll gradually to load all content - multiple passes
            for scroll_pass in range(2):  # Do 2 passes to ensure everything loads
                try:
                    max_scroll = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);")
                    scroll_step = 400
                    for scroll_position in range(0, max_scroll + scroll_step, scroll_step):
                        try:
                            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                            time.sleep(0.6)
                        except:
                            break
                    # Scroll back to top
                    try:
                        driver.execute_script("window.scrollTo(0, 0);")
                        time.sleep(1.5)
                    except:
                        break
                except:
                    break
            
            # Final scroll to ensure all lazy-loaded content appears
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(2)
            except:
                pass
        except Exception as e:
            print(f">>> Warning: Scrolling issue: {str(e)[:100]}")
            time.sleep(2)

        print("\n" + "="*70)
        print("FINDING ALL ANT DESIGN TREESELECT COMPONENTS")
        print("="*70)
        
        all_treeselects = find_treeselects_in_examples_section(driver, treeselect_handler)
        stats['total_found'] = len(all_treeselects)
        print(f"\nTotal TreeSelects found: {stats['total_found']}")

        if not all_treeselects:
            print(">>> No TreeSelects found. Exiting.")
            return

        print("\n" + "="*70)
        print("AUTOMATING ALL TREESELECT COMPONENTS")
        print("="*70)
        
        processed_keys = set()
        
        def get_element_key(element):
            """Get unique key for element"""
            try:
                elem_id = element.get_attribute('id')
                if elem_id:
                    return f"id_{elem_id}"
                loc = element.location
                size = element.size
                return f"loc_{loc['x']}_{loc['y']}_{size['width']}_{size['height']}"
            except:
                return f"obj_{id(element)}"
        
        for idx in range(1, len(all_treeselects) + 1):
            try:
                print(f"\n--- TreeSelect #{idx}/{len(all_treeselects)} ---")
                
                # Get TreeSelect
                try:
                    treeselect = all_treeselects[idx - 1]
                    element_key = get_element_key(treeselect)
                    if element_key in processed_keys:
                        continue
                except (StaleElementReferenceException, IndexError):
                    # Re-find all
                    all_treeselects = find_treeselects_in_examples_section(driver, treeselect_handler)
                    if idx > len(all_treeselects):
                        break
                    treeselect = all_treeselects[idx - 1]
                    element_key = get_element_key(treeselect)
                    if element_key in processed_keys:
                        continue
                
                stats['total_processed'] += 1
                
                # CRITICAL RULE: Close all existing dropdowns before interacting
                print(">>> Closing any existing dropdowns...")
                close_all_dropdowns(driver)
                
                # Scroll into view
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", treeselect)
                    time.sleep(0.8)
                except:
                    continue
                
                # Get TreeSelect info
                try:
                    info = treeselect_handler.identifier.identify_treeselect_type(treeselect)
                    treeselect_type = info.get('type', 'Unknown')
                    is_disabled = info.get('disabled', False)
                    placeholder = info.get('placeholder', 'N/A')
                    
                    print(f">>> Type: {treeselect_type}, Placeholder: {placeholder}")
                    
                    if is_disabled:
                        print(f">>> SKIPPED: TreeSelect is disabled")
                        stats['skipped_disabled'] += 1
                        stats['details'].append({
                            'index': idx,
                            'status': 'skipped',
                            'reason': 'disabled',
                            'type': treeselect_type
                        })
                        processed_keys.add(element_key)
                        continue
                except:
                    treeselect_type = 'Unknown'
                
                # Store location for verification
                try:
                    treeselect_location = treeselect.location
                    print(f">>> Location: x={treeselect_location['x']}, y={treeselect_location['y']}")
                except:
                    treeselect_location = None
                
                # CRITICAL RULE: Click THIS specific TreeSelect to open its dropdown
                print(">>> Clicking TreeSelect to open dropdown...")
                try:
                    # Find the best clickable element - prioritize input/selector
                    clickable = None
                    clickable_selectors = [
                        'input.ant-select-selection-search-input',
                        'input',
                        '.ant-select-selector',
                        '.ant-select-selection',
                        '.ant-select-selection-search',
                        '.ant-select-selection-item'
                    ]
                    
                    for selector in clickable_selectors:
                        try:
                            clickable = treeselect.find_element(By.CSS_SELECTOR, selector)
                            if clickable.is_displayed() and clickable.is_enabled():
                                print(f">>> Found clickable element: {selector}")
                                break
                        except:
                            continue
                    
                    if not clickable:
                        clickable = treeselect
                        print(">>> Using TreeSelect element itself")
                    
                    # Scroll into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'auto'});", clickable)
                    time.sleep(0.5)
                    
                    # IMPROVED: Multiple click strategies to ensure dropdown opens
                    # Strategy 1: JavaScript click with all events and coordinates
                    driver.execute_script("""
                        var elem = arguments[0];
                        elem.scrollIntoView({block: 'center', behavior: 'auto'});
                        
                        // Focus first
                        elem.focus();
                        
                        // Get coordinates for accurate click
                        var rect = elem.getBoundingClientRect();
                        var x = rect.left + rect.width / 2;
                        var y = rect.top + rect.height / 2;
                        
                        // Mouse events in sequence
                        var mouseDown = new MouseEvent('mousedown', {
                            bubbles: true,
                            cancelable: true,
                            view: window,
                            button: 0,
                            clientX: x,
                            clientY: y
                        });
                        elem.dispatchEvent(mouseDown);
                        
                        var mouseUp = new MouseEvent('mouseup', {
                            bubbles: true,
                            cancelable: true,
                            view: window,
                            button: 0,
                            clientX: x,
                            clientY: y
                        });
                        elem.dispatchEvent(mouseUp);
                        
                        var clickEvent = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window,
                            button: 0,
                            clientX: x,
                            clientY: y
                        });
                        elem.dispatchEvent(clickEvent);
                        
                        // Native click
                        if (typeof elem.click === 'function') {
                            elem.click();
                        }
                    """, clickable)
                    
                    # Strategy 2: Direct Selenium click
                    try:
                        clickable.click()
                    except:
                        pass
                    
                    # Strategy 3: Try clicking parent if child didn't work
                    try:
                        parent = clickable.find_element(By.XPATH, "./ancestor::*[contains(@class, 'ant-select')][1]")
                        driver.execute_script("arguments[0].click();", parent)
                    except:
                        pass
                    
                    print(">>> Click executed, waiting for dropdown...")
                    time.sleep(3.0)  # Wait longer for dropdown animation
                    
                except Exception as e:
                    print(f">>> FAILED: Could not click TreeSelect: {str(e)[:50]}")
                    stats['failed'] += 1
                    stats['details'].append({
                        'index': idx,
                        'status': 'failed',
                        'reason': f'Could not click TreeSelect: {str(e)[:50]}',
                        'type': treeselect_type
                    })
                    processed_keys.add(element_key)
                    continue
                
                # CRITICAL RULE: Verify dropdown belongs to THIS TreeSelect
                print(">>> Verifying dropdown ownership...")
                try:
                    # Wait for dropdown with explicit wait - try multiple times
                    all_dropdowns = []
                    for attempt in range(3):
                        try:
                            wait = WebDriverWait(driver, 5)
                            all_dropdowns = wait.until(
                                EC.presence_of_all_elements_located(
                                    (By.CSS_SELECTOR, '.ant-select-dropdown:not([style*="display: none"])')
                                )
                            )
                            if all_dropdowns:
                                break
                        except TimeoutException:
                            # Try alternative selectors
                            try:
                                all_dropdowns = driver.find_elements(By.CSS_SELECTOR, 
                                    '.ant-select-dropdown, [class*="ant-select-dropdown"]')
                                # Filter out hidden ones
                                all_dropdowns = [dd for dd in all_dropdowns if dd.is_displayed()]
                                if all_dropdowns:
                                    break
                            except:
                                pass
                            time.sleep(1.0)
                        except:
                            time.sleep(1.0)
                    
                    if not all_dropdowns:
                        print(f">>> SKIPPED: Dropdown did not open for this TreeSelect")
                        stats['skipped_no_dropdown'] += 1
                        stats['details'].append({
                            'index': idx,
                            'status': 'skipped',
                            'reason': 'dropdown not opened for this component',
                            'type': treeselect_type
                        })
                        processed_keys.add(element_key)
                        continue
                    
                    print(f">>> Found {len(all_dropdowns)} dropdown(s)")
                    
                    # Find the dropdown that belongs to this TreeSelect
                    valid_dropdown = None
                    for dropdown in all_dropdowns:
                        if verify_dropdown_ownership(driver, treeselect, dropdown):
                            valid_dropdown = dropdown
                            break
                    
                    if not valid_dropdown:
                        # If we can't verify, use closest one but log warning
                        print(">>> WARNING: Could not verify dropdown ownership, using closest dropdown")
                        if treeselect_location:
                            min_distance = float('inf')
                            for dd in all_dropdowns:
                                try:
                                    dd_loc = dd.location
                                    distance = abs(dd_loc['x'] - treeselect_location['x']) + abs(dd_loc['y'] - treeselect_location['y'])
                                    if distance < min_distance:
                                        min_distance = distance
                                        valid_dropdown = dd
                                except:
                                    continue
                        else:
                            valid_dropdown = all_dropdowns[0]
                    
                    if not valid_dropdown:
                        print(f">>> SKIPPED: Could not find valid dropdown for this TreeSelect")
                        stats['skipped_no_dropdown'] += 1
                        stats['details'].append({
                            'index': idx,
                            'status': 'skipped',
                            'reason': 'dropdown not opened for this component',
                            'type': treeselect_type
                        })
                        processed_keys.add(element_key)
                        continue
                    
                    print(">>> Dropdown verified and opened")
                    stats['successfully_opened'] += 1
                    
                except TimeoutException:
                    print(f">>> SKIPPED: Dropdown did not appear for this TreeSelect")
                    stats['skipped_no_dropdown'] += 1
                    stats['details'].append({
                        'index': idx,
                        'status': 'skipped',
                        'reason': 'dropdown not opened for this component',
                        'type': treeselect_type
                    })
                    processed_keys.add(element_key)
                    continue
                except Exception as e:
                    print(f">>> FAILED: Error verifying dropdown: {str(e)[:50]}")
                    stats['failed'] += 1
                    stats['details'].append({
                        'index': idx,
                        'status': 'failed',
                        'reason': f'Error verifying dropdown: {str(e)[:50]}',
                        'type': treeselect_type
                    })
                    processed_keys.add(element_key)
                    continue
                
                # CRITICAL RULE: MANDATORY SELECTION - Must select at least one value
                # Opening a dropdown is NOT considered successful - MUST select a value
                print(">>> Attempting to select a node...")
                success, message, is_empty = select_node_from_dropdown(
                    driver, treeselect, valid_dropdown, treeselect_handler)
                
                if is_empty:
                    # VALID SKIP: Tree contains zero selectable nodes
                    print(f">>> SKIPPED (VALID): Empty dropdown - {message}")
                    stats['empty_dropdowns'] += 1
                    stats['details'].append({
                        'index': idx,
                        'status': 'skipped',
                        'reason': f'Empty dropdown (zero selectable nodes): {message}',
                        'type': treeselect_type
                    })
                elif success:
                    # SUCCESS: Value was selected
                    print(f">>> SUCCESS: {message}")
                    stats['successfully_selected'] += 1
                    stats['details'].append({
                        'index': idx,
                        'status': 'success',
                        'message': message,
                        'type': treeselect_type
                    })
                else:
                    # CRITICAL FAILURE: Dropdown opened but no value was selected
                    # This violates the mandatory selection rule
                    error_msg = "TreeSelect dropdown opened but no option was selected"
                    print(f">>> FAILED: {error_msg}")
                    print(f">>> Details: {message}")
                    stats['failed'] += 1
                    stats['details'].append({
                        'index': idx,
                        'status': 'failed',
                        'reason': error_msg,
                        'details': message,
                        'type': treeselect_type
                    })
                    # DO NOT continue to next TreeSelect - this is a critical failure
                    # The script will continue but this TreeSelect is marked as failed
                
                # CRITICAL RULE: Close dropdown before moving to next TreeSelect
                print(">>> Closing dropdown before next TreeSelect...")
                close_all_dropdowns(driver)
                
                processed_keys.add(element_key)
                time.sleep(0.5)
                
            except Exception as e:
                print(f">>> FAILED: Error processing TreeSelect #{idx}: {str(e)[:100]}")
                stats['failed'] += 1
                stats['details'].append({
                    'index': idx,
                    'status': 'failed',
                    'reason': f'Exception: {str(e)[:100]}',
                    'type': 'Unknown'
                })
                try:
                    processed_keys.add(get_element_key(treeselect))
                except:
                    pass
                # Close any open dropdowns
                close_all_dropdowns(driver)
                continue
        
        # Print comprehensive report
        print("\n" + "="*70)
        print("COMPLETE AUTOMATION REPORT")
        print("="*70)
        print(f"Total TreeSelects Found: {stats['total_found']}")
        print(f"Total TreeSelects Processed: {stats['total_processed']}")
        print(f"Successfully Opened: {stats['successfully_opened']}")
        print(f"Successfully Selected: {stats['successfully_selected']}")
        print(f"Empty Dropdowns (clicked and reported): {stats['empty_dropdowns']}")
        print(f"Skipped (Disabled): {stats['skipped_disabled']}")
        print(f"Skipped (No Dropdown): {stats['skipped_no_dropdown']}")
        print(f"Failed: {stats['failed']}")
        print(f"\nSuccess Rate: {(stats['successfully_selected'] / max(stats['total_processed'], 1) * 100):.1f}%")
        print(f"Coverage: {(stats['total_processed'] / max(stats['total_found'], 1) * 100):.1f}% of found TreeSelects")
        print("="*70)
        
        # Detailed breakdown
        if stats['details']:
            print("\nDETAILED BREAKDOWN:")
            print("-"*70)
            for detail in stats['details']:
                status_icon = "✓" if detail['status'] == 'success' else "⊘" if detail['status'] == 'empty' else "⊘" if detail['status'] == 'skipped' else "✗"
                print(f"{status_icon} TreeSelect #{detail['index']} ({detail.get('type', 'Unknown')}): {detail['status'].upper()}")
                if detail['status'] == 'success':
                    print(f"   → {detail.get('message', 'N/A')}")
                elif detail['status'] in ['empty', 'skipped', 'failed']:
                    print(f"   → {detail.get('reason', 'N/A')}")
        
        print("\n>>> Keeping browser open for 15 seconds for inspection...")
        time.sleep(15)

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
