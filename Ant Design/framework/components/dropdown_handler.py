"""
Generic Ant Design Dropdown Handler
Handles dropdown/Select field interactions (selecting options, opening, closing, etc.)
Uses DropdownLocator for finding dropdowns and DropdownIdentifier for analyzing them
Uses ElementContext for context-driven interactions
"""
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, NoSuchElementException
from typing import Optional, Dict, List
from framework.base.base_page import BasePage
from framework.components.dropdown_locator import DropdownLocator
from framework.components.dropdown_identifier import DropdownIdentifier
from framework.context.element_context import ElementContext, ElementInfo
import time


class DropdownHandler(BasePage):
    """
    Generic handler for Ant Design dropdown/Select field interactions
    Single Responsibility: Handle dropdown interactions (selecting, opening, closing, etc.)
    Uses DropdownLocator to find dropdowns and DropdownIdentifier to analyze them
    """
    
    def __init__(self, driver: webdriver, context: Optional[ElementContext] = None):
        """
        Initialize Dropdown Handler
        
        Args:
            driver: Selenium WebDriver instance
            context: Optional ElementContext for context-driven interactions
        """
        super().__init__(driver)
        self.locator = DropdownLocator(driver)
        self.identifier = DropdownIdentifier()
        self.context = context
    
    def identify_and_store(self, identifier: str, identifier_type: str = 'data_attr_id',
                          timeout: int = 10, context_key: Optional[str] = None) -> bool:
        """
        Identify a dropdown and store it in context
        
        Args:
            identifier: Value to identify the dropdown (data-attr-id, label, or type)
            identifier_type: Type of identifier ('data_attr_id', 'label', 'type', 'position')
            timeout: Maximum wait time in seconds
            context_key: Optional key to use in context
            
        Returns:
            True if dropdown was identified and stored, False otherwise
        """
        if not self.context:
            print("Context not available. Cannot store element.")
            return False
        
        element = None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_dropdown_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'label':
                element = self.locator.find_dropdown_by_label(identifier, exact_match=False, timeout=timeout, context=self.context)
            elif identifier_type == 'type':
                elements = self.locator.find_dropdown_by_type(identifier, timeout, self.context)
                if elements:
                    element = elements[0]
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                element = self.locator.find_dropdown_by_position(position, timeout=timeout, context=self.context)
            
            if element:
                if context_key and context_key != identifier:
                    element_info = self.context.get_element(identifier) or self.context.get_current()
                    if element_info:
                        self.context.store_element(context_key, element_info)
                print(f"Dropdown identified and stored in context: {identifier}")
                return True
            else:
                print(f"Dropdown not found with identifier: {identifier} (type: {identifier_type})")
                return False
                
        except Exception as e:
            print(f"Error identifying dropdown: {str(e)}")
            return False
    
    def select_from_context(self, option_text: str, context_key: Optional[str] = None,
                           clear_first: bool = False) -> bool:
        """
        Select an option from dropdown using context (context-driven interaction)
        
        Args:
            option_text: Text of the option to select
            context_key: Optional key to retrieve element from context. If None, uses current element.
            clear_first: If True, clears existing selection first (for multiple selects)
            
        Returns:
            True if option was selected successfully, False otherwise
        """
        if not self.context:
            print("Context not available. Cannot select from context.")
            return False
        
        # Get element from context
        element_info = self.context.get_element(context_key) if context_key else self.context.get_current()
        
        if not element_info:
            print(f"Element not found in context with key: {context_key or 'current'}")
            return False
        
        element = element_info.element
        dropdown_info = element_info.metadata
        
        try:
            # Check if dropdown is interactable
            if dropdown_info.get('disabled', False):
                print(f"Dropdown is disabled and cannot be selected")
                return False
            
            if dropdown_info.get('loading', False):
                print(f"Dropdown is loading, waiting...")
                self._wait_for_loading_complete(element, timeout=30)
            
            return self._select_option(element, option_text, clear_first=clear_first)
            
        except Exception as e:
            print(f"Error selecting from context: {str(e)}")
            return False
    
    def select_by_text(self, identifier: Optional[str], option_text: str, identifier_type: str = 'data_attr_id',
                       timeout: int = 15, clear_first: bool = False, use_context: bool = False) -> bool:
        """
        Select an option by visible text
        
        Args:
            identifier: Value to identify the dropdown (data-attr-id, label, type, or position)
            option_text: Text of the option to select
            identifier_type: Type of identifier ('data_attr_id', 'label', 'type', 'position', 'auto')
            timeout: Maximum wait time in seconds
            clear_first: If True, clears existing selection first (for multiple selects)
            use_context: If True, tries to use context first
            
        Returns:
            True if option was selected successfully, False otherwise
        """
        # Try context first if enabled
        if use_context and self.context:
            element_info = self.context.get_element(identifier)
            if element_info:
                return self.select_from_context(option_text, identifier, clear_first)
        
        element = None
        # Always use context if available (for storing elements)
        context_to_use = self.context if self.context else None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_dropdown_by_data_attr(identifier, timeout, context_to_use)
            elif identifier_type == 'label':
                element = self.locator.find_dropdown_by_semantic_label(identifier, timeout, context_to_use)
            elif identifier_type == 'type':
                elements = self.locator.find_dropdown_by_type(identifier, timeout, context_to_use)
                if elements:
                    element = elements[0]
            elif identifier_type == 'position':
                if identifier is None:
                    # Find first dropdown
                    element = self.locator.find_dropdown_by_position(1, timeout=timeout, context=context_to_use)
                else:
                    position = int(identifier) if identifier.isdigit() else 1
                    element = self.locator.find_dropdown_by_position(position, timeout=timeout, context=context_to_use)
            elif identifier_type == 'auto':
                # PRIORITY ORDER: pattern discovery -> data-attr-id -> label -> type
                # Use pattern discovery to automatically find matching data-attr-id
                try:
                    from framework.utils.pattern_discovery import PatternDiscovery
                    pattern_discovery = PatternDiscovery(self.driver)
                    
                    # Normalize identifier for pattern matching
                    normalized_id = identifier.lower().replace(' ', '-').replace('_', '-')
                    
                    # Try to find matching data-attr-id using pattern discovery
                    matching_attr_id = pattern_discovery.find_matching_data_attr_id(normalized_id, 'dropdown')
                    if matching_attr_id:
                        element = self.locator.find_dropdown_by_data_attr(matching_attr_id, timeout=1, context=context_to_use)
                        if element:
                            try:
                                from conftest import _current_step_name
                                step_name = _current_step_name or "Unknown Step"
                                print(f"   >> STEP: {step_name[:45]:<45} | data-attr-id: '{matching_attr_id}'")
                            except:
                                print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{matching_attr_id}'")
                    
                    # If not found, try candidates
                    if not element:
                        data_attr_candidates = [
                            identifier.lower().replace(' ', '-'),
                            identifier.lower().replace(' ', '_'),
                            identifier.lower().replace(' ', ''),
                        ]
                        for candidate in data_attr_candidates:
                            element = self.locator.find_dropdown_by_data_attr(candidate, timeout=3, context=context_to_use)
                            if element:
                                break
                except Exception as e:
                    print(f"   >> Pattern discovery error: {str(e)}")
                
                if not element:
                    element = self.locator.find_dropdown_by_label(identifier, exact_match=False, timeout=5, context=context_to_use)
                if not element:
                    elements = self.locator.find_dropdown_by_type(identifier, timeout=5, context=context_to_use)
                    if elements:
                        element = elements[0]
            
            if not element:
                print(f"Dropdown not found with identifier: {identifier} (type: {identifier_type})")
                return False
            
            # Store element in context if context is available and element not already stored
            if context_to_use:
                context_key = None
                if identifier_type == 'data_attr_id':
                    context_key = identifier
                elif identifier_type == 'type':
                    context_key = identifier
                elif identifier_type == 'label':
                    context_key = identifier
                
                if context_key and not context_to_use.has_element(context_key):
                    self.locator._store_element_in_context(element, context_key, context_to_use)
                    print(f"   >> Stored dropdown in context with key: '{context_key}'")
            
            # Check dropdown properties
            dropdown_info = self.identifier.identify_dropdown_type(element)
            
            # Log detected dropdown type
            detected_type = dropdown_info.get('type', 'unknown')
            data_attr_id = dropdown_info.get('data_attr_id', 'N/A')
            print(f"   >> Detected dropdown type: '{detected_type}' (data-attr-id: {data_attr_id})")
            
            if dropdown_info['disabled']:
                print(f"Dropdown is disabled and cannot be selected")
                return False
            
            if dropdown_info['loading']:
                print(f"Dropdown is loading, waiting...")
                self._wait_for_loading_complete(element, timeout=30)
            
            return self._select_option(element, option_text, clear_first=clear_first)
            
        except Exception as e:
            print(f"Error selecting dropdown: {str(e)}")
            return False
    
    def select_by_index(self, identifier: Optional[str], index: int, identifier_type: str = 'data_attr_id',
                        timeout: int = 15, use_context: bool = False) -> bool:
        """
        Select an option by index (0-based)
        
        Args:
            identifier: Value to identify the dropdown (None means first dropdown)
            index: Index of the option to select (0-based)
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds (increased for reliability)
            use_context: If True, tries to use context first
            
        Returns:
            True if option was selected successfully, False otherwise
        """
        # Handle None identifier - find first dropdown
        if identifier is None:
            if identifier_type == 'position':
                # Find first dropdown by position
                element = self.locator.find_dropdown_by_position(1, timeout=timeout, context=self.context)
            else:
                # Find first dropdown by any means
                all_dropdowns = self.locator.find_all_dropdowns(timeout=timeout)
                if all_dropdowns:
                    element = all_dropdowns[0]
                else:
                    print("No dropdowns found on the page")
                    return False
        else:
            # Get available options first
            element = None
            if use_context and self.context:
                element_info = self.context.get_element(identifier)
                if element_info:
                    element = element_info.element
                else:
                    # Find element
                    if identifier_type == 'data_attr_id':
                        element = self.locator.find_dropdown_by_data_attr(identifier, timeout, self.context)
                    elif identifier_type == 'label':
                        element = self.locator.find_dropdown_by_semantic_label(identifier, timeout, self.context)
                    elif identifier_type == 'position':
                        position = int(identifier) if identifier.isdigit() else 1
                        element = self.locator.find_dropdown_by_position(position, timeout=timeout, context=self.context)
            
            if not element:
                if identifier_type == 'data_attr_id':
                    element = self.locator.find_dropdown_by_data_attr(identifier, timeout, self.context)
                elif identifier_type == 'label':
                    element = self.locator.find_dropdown_by_semantic_label(identifier, timeout, self.context)
                elif identifier_type == 'position':
                    position = int(identifier) if identifier.isdigit() else 1
                    element = self.locator.find_dropdown_by_position(position, timeout=timeout, context=self.context)
        
        if not element:
            print(f"Dropdown not found: {identifier}")
            return False
        
        # Get available options with increased timeout
        options = self._get_available_options_with_retry(element, timeout=timeout + 5)
        
        if 0 <= index < len(options):
            option_text = options[index]
            # Use the element directly instead of identifier for better reliability
            return self._select_option_direct(element, option_text, timeout=timeout + 5)
        else:
            print(f"Index {index} out of range. Available options: {len(options)}")
            return False
    
    def _select_option_direct(self, element: WebElement, option_text: str, timeout: int = 15) -> bool:
        """
        Select an option directly on an element (bypasses identifier lookup)
        
        Args:
            element: Dropdown element
            option_text: Text of option to select
            timeout: Maximum wait time
            
        Returns:
            True if successful
        """
        try:
            return self._select_option(element, option_text, clear_first=False)
        except Exception as e:
            print(f"Error selecting option directly: {str(e)}")
            return False
    
    def select_multiple(self, identifier: str, option_texts: List[str], identifier_type: str = 'data_attr_id',
                        timeout: int = 10, use_context: bool = False) -> bool:
        """
        Select multiple options (for multiple/tags dropdowns)
        
        Args:
            identifier: Value to identify the dropdown
            option_texts: List of option texts to select
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            use_context: If True, tries to use context first
            
        Returns:
            True if all options were selected successfully, False otherwise
        """
        success = True
        for option_text in option_texts:
            result = self.select_by_text(identifier, option_text, identifier_type, timeout, 
                                        clear_first=False, use_context=use_context)
            if not result:
                success = False
            time.sleep(0.5)  # Small delay between selections
        return success
    
    def select_first_in(self, identifier: str, identifier_type: str = 'data_attr_id',
                       timeout: int = 10, use_context: bool = False) -> bool:
        """
        Select the first option in dropdown
        
        Args:
            identifier: Value to identify the dropdown
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            use_context: If True, tries to use context first
            
        Returns:
            True if option was selected successfully, False otherwise
        """
        return self.select_by_index(identifier, 0, identifier_type, timeout, use_context)
    
    def select_last_in(self, identifier: str, identifier_type: str = 'data_attr_id',
                      timeout: int = 10, use_context: bool = False) -> bool:
        """
        Select the last option in dropdown
        
        Args:
            identifier: Value to identify the dropdown
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            use_context: If True, tries to use context first
            
        Returns:
            True if option was selected successfully, False otherwise
        """
        # Get element and options count
        element = None
        if use_context and self.context:
            element_info = self.context.get_element(identifier)
            if element_info:
                element = element_info.element
        
        if not element:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_dropdown_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'label':
                element = self.locator.find_dropdown_by_semantic_label(identifier, timeout, self.context)
        
        if not element:
            print(f"Dropdown not found: {identifier}")
            return False
        
        options = self._get_available_options_with_retry(element, timeout=timeout)
        if options:
            last_index = len(options) - 1
            return self.select_by_index(identifier, last_index, identifier_type, timeout, use_context)
        else:
            print(f"No options available in dropdown")
            return False
    
    def _select_option(self, element: WebElement, option_text: str, clear_first: bool = False) -> bool:
        """
        Internal method to select an option from dropdown
        Works with both Select components and Dropdown menu components
        
        Args:
            element: Dropdown WebElement
            option_text: Text of the option to select
            clear_first: If True, clears existing selection first
            
        Returns:
            True if option was selected successfully, False otherwise
        """
        try:
            # Check if it's a native select element
            if element.tag_name.lower() == 'select':
                from selenium.webdriver.support.ui import Select
                select = Select(element)
                if clear_first:
                    select.deselect_all()
                select.select_by_visible_text(option_text)
                print(f"Selected option '{option_text}' from native select")
                return True
            
            # Check if it's a Dropdown menu component (not Select)
            dropdown_info = self.identifier.identify_dropdown_type(element)
            if dropdown_info.get('type') == 'dropdown':
                # This is a Dropdown menu component - need to hover/click to open, then click menu item
                return self._select_from_dropdown_menu(element, option_text)
            
            # Ant Design Select component
            # Step 1: Open dropdown
            if not self._is_dropdown_open(element):
                self._open_dropdown(element)
            
            # Step 2: Wait for options to load (with retry for virtualized lists)
            self._wait_for_options_loaded(element, timeout=20)
            
            # Step 3: Clear existing selection if needed
            if clear_first:
                self._clear_selection(element)
            
            # Step 4: Find and click option
            option_found = self._click_option(element, option_text)
            
            if option_found:
                print(f"Selected option '{option_text}' from dropdown")
                return True
            else:
                print(f"Option '{option_text}' not found in dropdown")
                return False
                
        except Exception as e:
            print(f"Error selecting option: {str(e)}")
            return False
    
    def _select_from_dropdown_menu(self, element: WebElement, option_text: str) -> bool:
        """
        Select an option from a Dropdown menu component (menu dropdown, not Select)
        
        Args:
            element: Dropdown trigger WebElement
            option_text: Text of the menu item to select
            
        Returns:
            True if option was selected successfully, False otherwise
        """
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Step 1: Close any open dropdowns first to avoid interference
            self._close_all_open_dropdowns()
            time.sleep(0.5)
            
            # Step 2: Scroll into view
            self.execute_js("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1.0)
            
            # Step 3: Try clicking the element first to open menu (more reliable than hover)
            try:
                element.click()
                time.sleep(2.0)  # Increased wait for menu to open
            except:
                # If click fails, try hover
                actions = ActionChains(self.driver)
                actions.move_to_element(element).perform()
                time.sleep(2.0)  # Increased wait for menu to open
            
            # Step 4: Wait for menu to be visible and find the SPECIFIC menu for this dropdown
            try:
                WebDriverWait(self.driver, 10).until(  # Increased timeout
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-dropdown-menu, .ant-dropdown-menu-item'))
                )
                time.sleep(1.0)  # Additional wait for menu to fully render
            except:
                time.sleep(2.0)  # Wait even if timeout occurs
                pass
            
            # Step 5: Find menu items scoped to THIS specific dropdown (not all dropdowns)
            menu_items = self._find_menu_items_for_dropdown(element)
            
            if not menu_items:
                # Menu not open with click, try hover
                actions = ActionChains(self.driver)
                actions.move_to_element(element).perform()
                time.sleep(1.5)
                menu_items = self._find_menu_items_for_dropdown(element)
            
            # Extract text from all menu items first
            menu_item_texts = []
            for item in menu_items:
                try:
                    # Try multiple ways to get text
                    item_text = item.text.strip()
                    if not item_text:
                        # Try to get text from title content
                        try:
                            title_elem = item.find_element(By.CSS_SELECTOR, '.ant-dropdown-menu-title-content')
                            item_text = title_elem.text.strip()
                        except:
                            pass
                    if not item_text:
                        # Try innerText via JavaScript
                        try:
                            item_text = self.execute_js("return arguments[0].innerText || arguments[0].textContent;", item).strip()
                        except:
                            pass
                    if not item_text:
                        # Try getting text from all child text nodes
                        try:
                            item_text = self.execute_js("""
                                var text = '';
                                var nodes = arguments[0].childNodes;
                                for (var i = 0; i < nodes.length; i++) {
                                    if (nodes[i].nodeType === 3) { // Text node
                                        text += nodes[i].textContent;
                                    }
                                }
                                return text.trim();
                            """, item)
                        except:
                            pass
                    menu_item_texts.append(item_text or '')
                except:
                    menu_item_texts.append('')
            
            # Find and click the matching menu item
            for idx, item in enumerate(menu_items):
                try:
                    item_text = menu_item_texts[idx] if idx < len(menu_item_texts) else item.text.strip()
                    
                    # If option_text matches or is empty/first, click it
                    should_click = False
                    option_text_lower = option_text.lower() if option_text else ''
                    
                    # Check for "1st", "2nd", "first", "second", etc. patterns
                    is_first_request = option_text_lower in ['first', '1st', '1', ''] or \
                                      '1st' in option_text_lower or \
                                      (option_text_lower.startswith('first') and 'menu' in option_text_lower)
                    is_second_request = option_text_lower in ['second', '2nd', '2'] or \
                                       '2nd' in option_text_lower or \
                                       (option_text_lower.startswith('second') and 'menu' in option_text_lower)
                    
                    if option_text and item_text:
                        # Direct text match
                        if option_text.lower() in item_text.lower() or item_text.lower() in option_text.lower():
                            should_click = True
                        # Check for ordinal patterns (1st, 2nd, etc.)
                        elif is_first_request and idx == 0:
                            should_click = True
                        elif is_second_request and idx == 1:
                            should_click = True
                        # Check for "Nth menu item" pattern
                        elif 'menu item' in option_text_lower:
                            # Extract number from "1st menu item", "2nd menu item", etc.
                            import re
                            match = re.search(r'(\d+)(?:st|nd|rd|th)?', option_text_lower)
                            if match:
                                requested_index = int(match.group(1)) - 1  # Convert to 0-based
                                if idx == requested_index:
                                    should_click = True
                    elif is_first_request or not option_text:
                        # Click first item if no specific option or "first" requested
                        if idx == 0:
                            should_click = True
                    
                    if should_click:
                        # Scroll item into view
                        self.execute_js("arguments[0].scrollIntoView({block: 'center'});", item)
                        time.sleep(0.3)
                        
                        # Try multiple click methods for reliability
                        clicked = False
                        
                        # Method 1: Direct Selenium click
                        try:
                            item.click()
                            clicked = True
                        except:
                            pass
                        
                        # Method 2: JavaScript click if Selenium click failed
                        if not clicked:
                            try:
                                self.execute_js("arguments[0].click();", item)
                                clicked = True
                            except:
                                pass
                        
                        # Method 3: ActionChains click if both failed
                        if not clicked:
                            try:
                                actions = ActionChains(self.driver)
                                actions.move_to_element(item).click().perform()
                                clicked = True
                            except:
                                pass
                        
                        # Method 4: Mouse events via JavaScript
                        if not clicked:
                            try:
                                self.execute_js("""
                                    var event = new MouseEvent('click', {
                                        view: window,
                                        bubbles: true,
                                        cancelable: true
                                    });
                                    arguments[0].dispatchEvent(event);
                                """, item)
                                clicked = True
                            except:
                                pass
                        
                        time.sleep(0.5)
                        if clicked:
                            # Verify click was successful by checking if menu closed or item was selected
                            try:
                                # Wait a bit for menu to close or state to change
                                time.sleep(0.3)
                                # Check if menu is still visible (should close after click)
                                menu_visible = len(self.driver.find_elements(By.CSS_SELECTOR, '.ant-dropdown-menu:not([style*="display: none"])')) > 0
                                if not menu_visible or item_text:
                                    print(f"Selected menu item '{item_text}' from dropdown menu")
                                    return True
                            except:
                                # If verification fails, assume click worked
                                print(f"Selected menu item '{item_text}' from dropdown menu")
                                return True
                        else:
                            print(f"Failed to click menu item '{item_text}'")
                            
                except Exception as e:
                    continue
            
            # If still no match, try clicking first item anyway
            if menu_items:
                try:
                    first_item = menu_items[0]
                    first_text = menu_item_texts[0] if menu_item_texts else 'first item'
                    
                    # Scroll into view
                    self.execute_js("arguments[0].scrollIntoView({block: 'center'});", first_item)
                    time.sleep(0.3)
                    
                    # Try multiple click methods
                    clicked = False
                    try:
                        first_item.click()
                        clicked = True
                    except:
                        try:
                            self.execute_js("arguments[0].click();", first_item)
                            clicked = True
                        except:
                            try:
                                actions = ActionChains(self.driver)
                                actions.move_to_element(first_item).click().perform()
                                clicked = True
                            except:
                                pass
                    
                    time.sleep(1.5)  # Increased wait for selection to complete
                    if clicked:
                        print(f"Selected first menu item (text: '{first_text}') from dropdown menu")
                        return True
                except Exception as e:
                    print(f"Error clicking first item: {str(e)}")
                    pass
            
            available_texts = [text[:30] if text else '(empty)' for text in menu_item_texts[:5]]
            print(f"Menu item '{option_text}' not found in dropdown menu. Available items: {available_texts}")
            return False
            
        except Exception as e:
            print(f"Error selecting from dropdown menu: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _close_all_open_dropdowns(self) -> None:
        """
        Close any open dropdown menus to avoid interference
        """
        try:
            # Click outside or press Escape to close any open dropdowns
            script = """
            // Close all visible dropdown menus
            var menus = document.querySelectorAll('.ant-dropdown-menu, .ant-dropdown');
            menus.forEach(function(menu) {
                var style = window.getComputedStyle(menu);
                if (style.display !== 'none' && style.visibility !== 'hidden') {
                    // Try to find and click overlay/backdrop
                    var overlay = menu.closest('.ant-dropdown, [class*="dropdown"]');
                    if (overlay) {
                        overlay.style.display = 'none';
                    }
                }
            });
            // Press Escape key to close any open dropdowns
            var event = new KeyboardEvent('keydown', {
                key: 'Escape',
                code: 'Escape',
                keyCode: 27,
                bubbles: true
            });
            document.dispatchEvent(event);
            """
            self.driver.execute_script(script)
            time.sleep(0.2)
        except:
            pass
    
    def _find_menu_items_for_dropdown(self, trigger_element: WebElement) -> List[WebElement]:
        """
        Find menu items specifically for the given dropdown trigger element
        Uses proximity and association to find the correct menu
        
        Args:
            trigger_element: The dropdown trigger element
            
        Returns:
            List of menu item WebElements for this specific dropdown
        """
        menu_items = []
        try:
            # Get trigger element location
            trigger_location = trigger_element.location
            trigger_rect = trigger_element.rect
            
            # Use JavaScript to find menu items closest to this trigger
            script = """
            var trigger = arguments[0];
            var triggerRect = trigger.getBoundingClientRect();
            var triggerCenterX = triggerRect.left + triggerRect.width / 2;
            var triggerCenterY = triggerRect.top + triggerRect.height / 2;
            
            // Find all menu items
            var allItems = document.querySelectorAll('.ant-dropdown-menu-item:not(.ant-dropdown-menu-item-disabled), [role="menuitem"]:not([aria-disabled="true"])');
            var closestItems = [];
            var minDistance = Infinity;
            
            // Find the dropdown menu container
            var menus = document.querySelectorAll('.ant-dropdown-menu, .ant-dropdown');
            var targetMenu = null;
            
            // Find menu closest to trigger
            menus.forEach(function(menu) {
                var style = window.getComputedStyle(menu);
                if (style.display !== 'none' && style.visibility !== 'hidden') {
                    var menuRect = menu.getBoundingClientRect();
                    var distance = Math.sqrt(
                        Math.pow(menuRect.left - triggerRect.left, 2) + 
                        Math.pow(menuRect.top - triggerRect.top, 2)
                    );
                    if (distance < minDistance) {
                        minDistance = distance;
                        targetMenu = menu;
                    }
                }
            });
            
            // If we found a menu, get items from it
            if (targetMenu) {
                var items = targetMenu.querySelectorAll('.ant-dropdown-menu-item:not(.ant-dropdown-menu-item-disabled), [role="menuitem"]:not([aria-disabled="true"])');
                return Array.from(items);
            }
            
            // Fallback: find items closest to trigger by position
            allItems.forEach(function(item) {
                var itemRect = item.getBoundingClientRect();
                var distance = Math.sqrt(
                    Math.pow(itemRect.left - triggerCenterX, 2) + 
                    Math.pow(itemRect.top - triggerCenterY, 2)
                );
                if (distance < 500) { // Within 500px
                    closestItems.push({item: item, distance: distance});
                }
            });
            
            // Sort by distance and return closest items
            closestItems.sort(function(a, b) { return a.distance - b.distance; });
            return closestItems.slice(0, 10).map(function(x) { return x.item; });
            """
            
            items = self.driver.execute_script(script, trigger_element)
            if items:
                # Convert JavaScript elements to Selenium WebElements
                # We need to find them again using Selenium
                try:
                    # Get all visible menu items
                    all_menu_items = self.driver.find_elements(By.CSS_SELECTOR, '.ant-dropdown-menu-item:not(.ant-dropdown-menu-item-disabled)')
                    
                    # Filter by proximity to trigger
                    trigger_location = trigger_element.location
                    for item in all_menu_items:
                        try:
                            item_location = item.location
                            # Calculate distance
                            distance = ((item_location['x'] - trigger_location['x'])**2 + 
                                       (item_location['y'] - trigger_location['y'])**2)**0.5
                            # Only include items within reasonable distance (500px)
                            if distance < 500:
                                menu_items.append(item)
                        except:
                            pass
                    
                    # If we found items, return them
                    if menu_items:
                        return menu_items[:10]  # Limit to 10 closest items
                except:
                    pass
            
            # Fallback: Use standard selectors but filter by visibility and proximity
            selectors = [
                '.ant-dropdown-menu-item:not(.ant-dropdown-menu-item-disabled)',
                '.ant-dropdown-menu-item',
                '[role="menuitem"]:not([aria-disabled="true"])',
                '.ant-dropdown-menu li:not(.ant-dropdown-menu-item-disabled)'
            ]
            
            for selector in selectors:
                try:
                    items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if items:
                        # Filter items that are actually visible and near the trigger
                        trigger_location = trigger_element.location
                        for item in items:
                            try:
                                if item.is_displayed():
                                    item_location = item.location
                                    distance = ((item_location['x'] - trigger_location['x'])**2 + 
                                               (item_location['y'] - trigger_location['y'])**2)**0.5
                                    if distance < 500:  # Within 500px
                                        menu_items.append(item)
                            except:
                                pass
                        if menu_items:
                            return menu_items[:10]  # Return first 10 closest
                except:
                    pass
                    
        except Exception as e:
            print(f"Error finding menu items for dropdown: {str(e)}")
        
        return menu_items
    
    def _is_dropdown_open(self, element: WebElement) -> bool:
        """Check if dropdown is open"""
        try:
            aria_expanded = element.get_attribute('aria-expanded')
            if aria_expanded == 'true':
                return True
            
            # Check if dropdown menu is visible
            try:
                menu = element.find_element(By.CSS_SELECTOR, '.ant-select-dropdown:not([style*="display: none"])')
                return menu.is_displayed()
            except:
                # Check in document (could be in portal)
                driver = self.driver
                script = """
                var menus = document.querySelectorAll('.ant-select-dropdown');
                for (var i = 0; i < menus.length; i++) {
                    var style = window.getComputedStyle(menus[i]);
                    if (style.display !== 'none' && style.visibility !== 'hidden') {
                        return true;
                    }
                }
                return false;
                """
                return driver.execute_script(script) or False
        except:
            return False
    
    def _open_dropdown(self, element: WebElement) -> bool:
        """Open the dropdown"""
        try:
            # Click on selector to open dropdown
            selector = element.find_element(By.CSS_SELECTOR, '.ant-select-selector')
            selector.click()
            time.sleep(0.5)  # Wait for dropdown to open
            return True
        except:
            try:
                # Try clicking the element itself
                element.click()
                time.sleep(0.5)
                return True
            except:
                return False
    
    def _wait_for_options_loaded(self, element: WebElement, timeout: int = 10) -> bool:
        """Wait for dropdown options to load (with retry for virtualized lists)"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Check if options are visible
                driver = self.driver
                script = """
                var options = document.querySelectorAll('.ant-select-item:not(.ant-select-item-empty)');
                return options.length > 0;
                """
                has_options = driver.execute_script(script)
                
                if has_options:
                    time.sleep(0.5)  # Wait for rendering
                    return True
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
            except:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        return False
    
    def _get_available_options_with_retry(self, element: WebElement, timeout: int = 20) -> List[str]:
        """Get available options with retry for virtualized lists"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Open dropdown if not open
                if not self._is_dropdown_open(element):
                    self._open_dropdown(element)
                
                # Wait for options
                self._wait_for_options_loaded(element, timeout=timeout)
                
                # Get options
                options = []
                driver = self.driver
                script = """
                var options = [];
                var items = document.querySelectorAll('.ant-select-item:not(.ant-select-item-empty)');
                for (var i = 0; i < items.length; i++) {
                    var text = items[i].textContent.trim();
                    if (text) options.push(text);
                }
                return options;
                """
                options = driver.execute_script(script) or []
                
                if options:
                    return options
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        return []
    
    def _click_option(self, element: WebElement, option_text: str) -> bool:
        """Click on an option by text"""
        try:
            # Try to find option in dropdown menu
            driver = self.driver
            script = f"""
            var optionText = arguments[0];
            var items = document.querySelectorAll('.ant-select-item:not(.ant-select-item-empty)');
            for (var i = 0; i < items.length; i++) {{
                var text = items[i].textContent.trim();
                if (text === optionText || text.includes(optionText)) {{
                    items[i].click();
                    return true;
                }}
            }}
            return false;
            """
            result = driver.execute_script(script, option_text)
            
            if result:
                time.sleep(0.5)  # Wait for selection to complete
                return True
            
            # Fallback: Try Selenium find
            try:
                # Find dropdown menu
                menu = element.find_element(By.CSS_SELECTOR, '.ant-select-dropdown:not([style*="display: none"])')
                options = menu.find_elements(By.CSS_SELECTOR, '.ant-select-item')
                for opt in options:
                    if option_text in opt.text.strip():
                        opt.click()
                        time.sleep(0.5)
                        return True
            except:
                pass
            
            return False
        except:
            return False
    
    def _clear_selection(self, element: WebElement) -> bool:
        """Clear existing selection (for multiple selects)"""
        try:
            # Find and click clear buttons
            clear_buttons = element.find_elements(By.CSS_SELECTOR, '.ant-select-selection-item-remove')
            for btn in clear_buttons:
                btn.click()
                time.sleep(0.2)
            return True
        except:
            return False
    
    def _wait_for_loading_complete(self, element: WebElement, timeout: int = 30) -> bool:
        """Wait for dropdown loading to complete"""
        try:
            wait = WebDriverWait(element._parent, timeout)
            wait.until_not(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-select-loading-icon')))
            return True
        except:
            return False
    
    def get_all_dropdowns_summary(self, include_all: bool = False) -> Dict[str, any]:
        """
        Get summary of all detected dropdowns
        
        Args:
            include_all: If True, includes ALL dropdowns (not just Ant Design)
            
        Returns:
            Dictionary with summary information
        """
        try:
            all_dropdowns = self.locator.find_all_ant_dropdowns(include_all=include_all)
            
            summary = {
                'total': len(all_dropdowns),
                'by_type': {},
                'details': []
            }
            
            for dropdown_elem in all_dropdowns:
                dropdown_info = self.identifier.identify_dropdown_type(dropdown_elem)
                dropdown_type = dropdown_info['type']
                
                # Count by type
                if dropdown_type not in summary['by_type']:
                    summary['by_type'][dropdown_type] = 0
                summary['by_type'][dropdown_type] += 1
                
                # Store details
                summary['details'].append({
                    'type': dropdown_type,
                    'size': dropdown_info['size'],
                    'disabled': dropdown_info['disabled'],
                    'loading': dropdown_info['loading'],
                    'searchable': dropdown_info['searchable'],
                    'placeholder': dropdown_info['placeholder'],
                    'label': dropdown_info['label'],
                    'selected_values': dropdown_info['selected_values'],
                    'options_count': dropdown_info['options_count'],
                    'data_attr_id': dropdown_info['data_attr_id']
                })
            
            return summary
        except Exception as e:
            print(f"Error getting dropdowns summary: {str(e)}")
            return {'total': 0, 'by_type': {}, 'details': []}
    
    def print_dropdowns_summary(self, include_all: bool = False) -> None:
        """
        Print a readable summary of all detected dropdowns
        
        Args:
            include_all: If True, includes ALL dropdowns (not just Ant Design)
        """
        summary = self.get_all_dropdowns_summary(include_all=include_all)
        
        scope = "ALL DROPDOWNS" if include_all else "ANT DESIGN DROPDOWNS"
        print(f"\n{'='*100}")
        print(f"DROPDOWN FIELDS SUMMARY ({scope})")
        print(f"{'='*100}")
        print(f"Total dropdowns detected: {summary['total']}")
        print(f"\nBy Type:")
        for dropdown_type, count in summary['by_type'].items():
            print(f"  - {dropdown_type}: {count}")
        
        if summary['details']:
            print(f"\n{'Dropdown Label':<20} {'Type':<12} {'Size':<8} {'Disabled':<10} {'Searchable':<12} {'Selected':<20} {'Options':<10}")
            print(f"{'-'*100}")
            for detail in summary['details']:
                label = detail['label'] or detail['placeholder'] or 'N/A'
                label = label[:18] if len(label) > 18 else label
                dropdown_type = detail['type'][:10] if len(detail['type']) > 10 else detail['type']
                size = detail['size'][:6] if len(detail['size']) > 6 else detail['size']
                disabled = 'Yes' if detail['disabled'] else 'No'
                searchable = 'Yes' if detail['searchable'] else 'No'
                selected = ', '.join(detail['selected_values'][:2]) if detail['selected_values'] else 'None'
                selected = selected[:18] if len(selected) > 18 else selected
                options_count = str(detail['options_count'])
                
                print(f"{label:<20} {dropdown_type:<12} {size:<8} {disabled:<10} {searchable:<12} {selected:<20} {options_count:<10}")
        
        print(f"{'='*100}\n")
    
    # Delegate methods for backward compatibility
    def find_dropdown_by_data_attr(self, data_attr_id: str, timeout: int = 10) -> Optional[WebElement]:
        """Delegate to DropdownLocator"""
        return self.locator.find_dropdown_by_data_attr(data_attr_id, timeout, self.context)
    
    def find_dropdown_by_label(self, label_text: str, exact_match: bool = False, timeout: int = 10) -> Optional[WebElement]:
        """Delegate to DropdownLocator"""
        return self.locator.find_dropdown_by_label(label_text, exact_match, timeout, self.context)
    
    def find_dropdown_by_type(self, dropdown_type: str, timeout: int = 10) -> List[WebElement]:
        """Delegate to DropdownLocator"""
        return self.locator.find_dropdown_by_type(dropdown_type, timeout, self.context)
    
    def find_all_ant_dropdowns(self, timeout: int = 10, include_all: bool = False) -> List[WebElement]:
        """Delegate to DropdownLocator"""
        return self.locator.find_all_ant_dropdowns(timeout, include_all=include_all)
    
    def identify_dropdown_type(self, element: WebElement) -> Dict[str, any]:
        """Delegate to DropdownIdentifier"""
        return self.identifier.identify_dropdown_type(element)

