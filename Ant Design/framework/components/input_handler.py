"""
Generic Ant Design Input Handler
Handles input field interactions (filling, clearing, etc.)
Uses InputLocator for finding inputs and InputIdentifier for analyzing them
Uses ElementContext for context-driven interactions
"""
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from typing import Optional, Dict, List
from framework.base.base_page import BasePage
from framework.components.input_locator import InputLocator
from framework.components.input_identifier import InputIdentifier
from framework.components.button_handler import ButtonHandler
from framework.context.element_context import ElementContext, ElementInfo


class InputHandler(BasePage):
    """
    Generic handler for Ant Design input field interactions
    Single Responsibility: Handle input interactions (filling, clearing, etc.)
    Uses InputLocator to find inputs and InputIdentifier to analyze them
    """
    
    def __init__(self, driver: webdriver, context: Optional[ElementContext] = None):
        """
        Initialize Input Handler
        
        Args:
            driver: Selenium WebDriver instance
            context: Optional ElementContext for context-driven interactions
        """
        super().__init__(driver)
        self.locator = InputLocator(driver)
        self.identifier = InputIdentifier()
        self.context = context
        self.button_handler = ButtonHandler(driver, context=context)  # For clicking associated buttons
    
    def identify_and_store(self, identifier: str, identifier_type: str = 'data_attr_id',
                          timeout: int = 10, context_key: Optional[str] = None) -> bool:
        """
        Identify an input and store it in context
        
        Args:
            identifier: Value to identify the input (data-attr-id, label, or type)
            identifier_type: Type of identifier ('data_attr_id', 'label', 'type', 'position')
            timeout: Maximum wait time in seconds
            context_key: Optional key to use in context
            
        Returns:
            True if input was identified and stored, False otherwise
        """
        if not self.context:
            print("Context not available. Cannot store element.")
            return False
        
        element = None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_input_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'label':
                element = self.locator.find_input_by_label(identifier, exact_match=False, timeout=timeout, context=self.context)
            elif identifier_type == 'type':
                elements = self.locator.find_input_by_type(identifier, timeout, self.context)
                if elements:
                    element = elements[0]
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                element = self.locator.find_input_by_position(position, timeout=timeout, context=self.context)
            
            if element:
                if context_key and context_key != identifier:
                    element_info = self.context.get_element(identifier) or self.context.get_current()
                    if element_info:
                        self.context.store_element(context_key, element_info)
                print(f"Input identified and stored in context: {identifier}")
                return True
            else:
                print(f"Input not found with identifier: {identifier} (type: {identifier_type})")
                return False
                
        except Exception as e:
            print(f"Error identifying input: {str(e)}")
            return False
    
    def fill_from_context(self, value: str, context_key: Optional[str] = None, clear_first: bool = True) -> bool:
        """
        Fill an input using context (context-driven interaction)
        
        Args:
            value: Value to fill
            context_key: Optional key to retrieve element from context. If None, uses current element.
            clear_first: If True, clears the input before filling
            
        Returns:
            True if input was filled successfully, False otherwise
        """
        if not self.context:
            print("Context not available. Cannot fill from context.")
            return False
        
        # Get element from context
        element_info = self.context.get_element(context_key) if context_key else self.context.get_current()
        
        if not element_info:
            print(f"Element not found in context with key: {context_key or 'current'}")
            return False
        
        element = element_info.element
        input_info = element_info.metadata
        
        try:
            # Check if input is interactable
            if input_info.get('disabled', False):
                print(f"Input is disabled and cannot be filled")
                return False
            
            if input_info.get('readonly', False):
                print(f"Input is read-only and cannot be filled")
                return False
            
            # Scroll element into view
            try:
                self.execute_js("arguments[0].scrollIntoView({block: 'center'});", element)
            except:
                pass
            
            # Clear input if needed
            if clear_first:
                self._clear_input(element)
            
            # Fill the input
            fill_success = False
            try:
                element.clear()
                element.send_keys(value)
                print(f"Filled input with value: '{value}'")
                fill_success = True
            except ElementNotInteractableException:
                # Try JavaScript approach
                print("Normal fill failed, trying JavaScript...")
                self.execute_js(f"arguments[0].value = '{value}';", element)
                # Trigger input event
                self.execute_js("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", element)
                self.execute_js("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", element)
                print(f"Filled input with value using JavaScript: '{value}'")
                fill_success = True
            
            # Auto-click associated button if found
            if fill_success:
                button_clicked = self._click_associated_button(element)
                if button_clicked:
                    print(f"   >> Associated button was automatically clicked")
                else:
                    print(f"   >> No associated button found or button was disabled")
            
            return fill_success
            
        except Exception as e:
            print(f"Error filling input from context: {str(e)}")
            return False
    
    def fill_input(self, identifier: str, value: str, identifier_type: str = 'data_attr_id',
                   timeout: int = 10, clear_first: bool = True, use_context: bool = False) -> bool:
        """
        Fill an input field using various identification methods
        PRIORITY: data-attr-id is tried first when identifier_type is 'auto' or 'label'
        
        Args:
            identifier: Value to identify the input (data-attr-id, label, type, or position)
            value: Value to fill
            identifier_type: Type of identifier ('data_attr_id', 'label', 'type', 'position', 'auto')
            timeout: Maximum wait time in seconds
            clear_first: If True, clears the input before filling
            use_context: If True, tries to use context first
            
        Returns:
            True if input was filled successfully, False otherwise
        """
        # Try context first if enabled
        if use_context and self.context:
            element_info = self.context.get_element(identifier)
            if element_info:
                return self.fill_from_context(value, identifier, clear_first)
        
        element = None
        # Always use context if available (for storing elements)
        context_to_use = self.context if self.context else None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_input_by_data_attr(identifier, timeout, context_to_use)
            elif identifier_type == 'label':
                # For label type, try data-attr-id first (normalized), then semantic label
                element = self.locator.find_input_by_semantic_label(identifier, timeout, context_to_use)
            elif identifier_type == 'type':
                elements = self.locator.find_input_by_type(identifier, timeout, context_to_use)
                if elements:
                    element = elements[0]
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                element = self.locator.find_input_by_position(position, timeout=timeout, context=context_to_use)
            elif identifier_type == 'auto':
                # PRIORITY ORDER: pattern discovery -> data-attr-id -> label -> type
                # Use pattern discovery to automatically find matching data-attr-id
                try:
                    # Try to use shared PatternDiscovery from context if available
                    pattern_discovery = None
                    if self.context and hasattr(self.context, 'pattern_discovery'):
                        pattern_discovery = self.context.pattern_discovery
                    else:
                        from framework.utils.pattern_discovery import PatternDiscovery
                        pattern_discovery = PatternDiscovery(self.driver)
                    
                    # Normalize identifier for pattern matching
                    normalized_id = identifier.lower().replace(' ', '-').replace('_', '-')
                    
                    # Try to find matching data-attr-id using pattern discovery (fast - uses cache)
                    matching_attr_id = pattern_discovery.find_matching_data_attr_id(normalized_id, 'input')
                    if matching_attr_id:
                        element = self.locator.find_input_by_data_attr(matching_attr_id, timeout=1, context=context_to_use)
                        if element:
                            try:
                                from conftest import _current_step_name
                                step_name = _current_step_name or "Unknown Step"
                                print(f"   >> STEP: {step_name[:45]:<45} | data-attr-id: '{matching_attr_id}'")
                            except:
                                print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{matching_attr_id}'")
                    
                    # If not found, generate candidates based on discovered pattern (limit to 2 for speed)
                    if not element:
                        candidates = pattern_discovery.generate_candidates(normalized_id, 'input')
                        for candidate in candidates[:2]:  # Limit to first 2 candidates for speed
                            element = self.locator.find_input_by_data_attr(candidate, timeout=1, context=context_to_use)
                            if element:
                                try:
                                    from conftest import _current_step_name
                                    step_name = _current_step_name or "Unknown Step"
                                    print(f"   >> STEP: {step_name[:45]:<45} | data-attr-id: '{candidate}'")
                                except:
                                    print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{candidate}'")
                                break
                except Exception as e:
                    print(f"   >> Pattern discovery failed: {str(e)}")
                
                # Fallback to direct data-attr-id search (faster timeout)
                if not element:
                    element = self.locator.find_input_by_data_attr(identifier, timeout=1, context=context_to_use)
                
                # Fallback to label search (which also uses pattern discovery) - faster timeout
                if not element:
                    element = self.locator.find_input_by_semantic_label(identifier, timeout=1, context=context_to_use)
                
                # Fallback to type search (faster timeout)
                if not element:
                    elements = self.locator.find_input_by_type(identifier, timeout=1, context=context_to_use)
                    if elements:
                        element = elements[0]
            
            if not element:
                print(f"Input not found with identifier: {identifier} (type: {identifier_type})")
                return False
            
            # Store element in context if context is available and element not already stored
            if context_to_use:
                # Check if element is already in context
                context_key = None
                if identifier_type == 'data_attr_id':
                    context_key = identifier
                elif identifier_type == 'type':
                    context_key = identifier  # Use type as key (e.g., "search", "text")
                elif identifier_type == 'label':
                    context_key = identifier
                elif identifier_type == 'position':
                    # For position, use type + position as key
                    input_info_temp = self.identifier.identify_input_type(element)
                    input_type = input_info_temp.get('input_type', 'input')
                    context_key = f"{input_type}_{identifier}"
                
                # Only store if not already in context
                if context_key and not context_to_use.has_element(context_key):
                    # Manually store using locator's method
                    self.locator._store_element_in_context(element, context_key, context_to_use)
                    print(f"   >> Stored input in context with key: '{context_key}'")
            
            # Check if input is interactable
            input_info = self.identifier.identify_input_type(element)
            
            # Log detected field type (from data-attr-id priority)
            detected_type = input_info.get('input_type', 'unknown')
            data_attr_id = input_info.get('data_attr_id', 'N/A')
            print(f"   >> Detected field type: '{detected_type}' (data-attr-id: {data_attr_id})")
            
            if input_info['disabled']:
                print(f"Input is disabled and cannot be filled")
                return False
            
            if input_info['readonly']:
                print(f"Input is read-only and cannot be filled")
                return False
            
            # Scroll element into view
            try:
                self.execute_js("arguments[0].scrollIntoView({block: 'center'});", element)
            except:
                pass
            
            # Clear input if needed
            if clear_first:
                self._clear_input(element)
            
            # Fill the input
            fill_success = False
            try:
                element.clear()
                element.send_keys(value)
                print(f"Filled input '{identifier}' with value: '{value}'")
                fill_success = True
            except ElementNotInteractableException:
                # Try JavaScript approach
                print("Normal fill failed, trying JavaScript...")
                self.execute_js(f"arguments[0].value = '{value}';", element)
                self.execute_js("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", element)
                self.execute_js("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", element)
                print(f"Filled input using JavaScript: '{value}'")
                fill_success = True
            
            # Auto-click associated button if found
            if fill_success:
                button_clicked = self._click_associated_button(element)
                if button_clicked:
                    print(f"   >> Associated button was automatically clicked")
                else:
                    print(f"   >> No associated button found or button was disabled")
            
            return fill_success
            
        except Exception as e:
            print(f"Error filling input: {str(e)}")
            return False
    
    def _click_associated_button(self, element: WebElement) -> bool:
        """
        Automatically click an associated button (search, submit, etc.) for an input field
        This is called after filling an input to trigger the associated action
        
        Args:
            element: Input WebElement that was just filled
            
        Returns:
            True if button was found and clicked, False otherwise
        """
        try:
            # Find associated button using InputIdentifier
            associated_button = InputIdentifier._find_associated_button(element)
            
            if associated_button:
                # Check if button is disabled
                if associated_button.get_attribute('disabled') is not None:
                    print(f"   >> Associated button found but is disabled, skipping click")
                    return False
                
                # Get button info for logging
                try:
                    button_text = associated_button.text.strip() if associated_button.text else ''
                    button_class = associated_button.get_attribute('class') or ''
                    print(f"   >> Found associated button: '{button_text}' (class: {button_class[:50]})")
                except:
                    print(f"   >> Found associated button")
                
                # Scroll button into view
                try:
                    self.execute_js("arguments[0].scrollIntoView({block: 'center'});", associated_button)
                except:
                    pass
                
                # Click the button using ButtonHandler for consistency
                try:
                    # Try normal click first
                    associated_button.click()
                    print(f"   >> Successfully clicked associated button")
                    return True
                except ElementNotInteractableException:
                    # Try JavaScript click as fallback
                    try:
                        self.execute_js("arguments[0].click();", associated_button)
                        print(f"   >> Successfully clicked associated button using JavaScript")
                        return True
                    except Exception as e:
                        print(f"   >> Failed to click associated button: {str(e)}")
                        return False
            else:
                # No associated button found - this is normal for many inputs
                return False
                
        except Exception as e:
            # Silently fail - not all inputs have associated buttons
            return False
    
    def _clear_input(self, element: WebElement) -> None:
        """
        Clear an input field, handling Ant Design clear button if present
        
        Args:
            element: Input WebElement to clear
        """
        try:
            # Try to find and click clear button (Ant Design allowClear)
            try:
                parent = element.find_element(By.XPATH, "./ancestor::span[contains(@class, 'ant-input-affix-wrapper')]")
                clear_btn = parent.find_element(By.CSS_SELECTOR, '.ant-input-clear-icon, .anticon-close-circle')
                if clear_btn:
                    clear_btn.click()
                    return
            except:
                pass
            
            # Fallback to standard clear
            element.clear()
            # Also clear via JavaScript to ensure
            self.execute_js("arguments[0].value = '';", element)
            self.execute_js("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", element)
        except Exception as e:
            print(f"Error clearing input: {str(e)}")
    
    def get_input_info(self, identifier: str, identifier_type: str = 'data_attr_id') -> Optional[Dict]:
        """
        Get information about an input without filling it
        
        Args:
            identifier: Value to identify the input
            identifier_type: Type of identifier ('data_attr_id', 'label', 'type')
            
        Returns:
            Dictionary with input information or None if not found
        """
        element = None
        
        if identifier_type == 'data_attr_id':
            element = self.locator.find_input_by_data_attr(identifier)
        elif identifier_type == 'label':
            element = self.locator.find_input_by_label(identifier)
        elif identifier_type == 'type':
            elements = self.locator.find_input_by_type(identifier)
            if elements:
                element = elements[0]
        
        if element:
            return self.identifier.identify_input_type(element)
        
        return None
    
    def get_all_inputs_summary(self, include_all: bool = False) -> Dict[str, any]:
        """
        Get a summary of all detected inputs on the page
        
        Args:
            include_all: If True, includes ALL inputs (not just Ant Design)
        
        Returns:
            Dictionary with input counts and details by type
        """
        try:
            all_inputs = self.locator.find_all_ant_inputs(include_all=include_all)
            
            summary = {
                'total': len(all_inputs),
                'by_type': {},
                'details': []
            }
            
            for input_elem in all_inputs:
                input_info = self.identifier.identify_input_type(input_elem)
                input_type = input_info['input_type']
                
                # Count by type
                if input_type not in summary['by_type']:
                    summary['by_type'][input_type] = 0
                summary['by_type'][input_type] += 1
                
                # Store details
                summary['details'].append({
                    'type': input_type,
                    'size': input_info['size'],
                    'disabled': input_info['disabled'],
                    'readonly': input_info['readonly'],
                    'clearable': input_info['clearable'],
                    'placeholder': input_info['placeholder'],
                    'label': input_info['label'],
                    'data_attr_id': input_info['data_attr_id']
                })
            
            return summary
        except Exception as e:
            print(f"Error getting inputs summary: {str(e)}")
            return {'total': 0, 'by_type': {}, 'details': []}
    
    def print_inputs_summary(self, include_all: bool = False) -> None:
        """
        Print a readable summary of all detected inputs
        
        Args:
            include_all: If True, includes ALL inputs (not just Ant Design)
        """
        summary = self.get_all_inputs_summary(include_all=include_all)
        
        scope = "ALL INPUTS" if include_all else "ANT DESIGN INPUTS"
        print(f"\n{'='*70}")
        print(f"INPUT FIELDS SUMMARY ({scope})")
        print(f"{'='*70}")
        print(f"Total inputs detected: {summary['total']}")
        print(f"\nBy Type:")
        for input_type, count in summary['by_type'].items():
            print(f"  - {input_type}: {count}")
        
        if summary['details']:
            print(f"\nDetails:")
            for idx, detail in enumerate(summary['details'], 1):
                print(f"\n  Input #{idx}:")
                print(f"    Type: {detail['type']}")
                print(f"    Size: {detail['size']}")
                print(f"    Disabled: {detail['disabled']}")
                print(f"    Read-only: {detail['readonly']}")
                print(f"    Clearable: {detail['clearable']}")
                if detail['placeholder']:
                    print(f"    Placeholder: '{detail['placeholder']}'")
                if detail['label']:
                    print(f"    Label: '{detail['label']}'")
                if detail['data_attr_id']:
                    print(f"    Data-attr-id: '{detail['data_attr_id']}'")
        print(f"{'='*70}\n")
    
    def fill_all_inputs(self, use_random_values: bool = True, include_all: bool = True) -> Dict[str, any]:
        """
        Automatically fill all inputs on the page with random values
        
        Args:
            use_random_values: If True, uses random values. If False, uses generic values.
            include_all: If True, fills ALL inputs (not just Ant Design)
            
        Returns:
            Dictionary with fill results:
            {
                'total': int,
                'filled': int,
                'skipped': int,
                'failed': int,
                'details': list
            }
        """
        import random
        import string
        
        all_inputs = self.locator.find_all_ant_inputs(include_all=include_all)
        
        results = {
            'total': len(all_inputs),
            'filled': 0,
            'skipped': 0,
            'failed': 0,
            'details': []
        }
        
        print(f"\n{'='*70}")
        print(f"AUTOMATICALLY FILLING ALL INPUTS")
        print(f"{'='*70}")
        print(f"Total inputs found: {results['total']}\n")
        
        for idx, input_elem in enumerate(all_inputs, 1):
            try:
                # Get input information
                input_info = self.identifier.identify_input_type(input_elem)
                
                # Store element in context if context is available
                if self.context:
                    # Generate context key: prefer data-attr-id, then type + index
                    context_key = input_info.get('data_attr_id')
                    if not context_key:
                        context_key = f"{input_info['input_type']}_{idx}"
                    
                    # Only store if not already in context
                    if not self.context.has_element(context_key):
                        self.locator._store_element_in_context(input_elem, context_key, self.context)
                
                # Skip disabled or readonly inputs
                if input_info['disabled'] or input_info['readonly']:
                    print(f"  Input #{idx}: SKIPPED (disabled or readonly)")
                    results['skipped'] += 1
                    results['details'].append({
                        'index': idx,
                        'status': 'skipped',
                        'reason': 'disabled or readonly',
                        'type': input_info['input_type']
                    })
                    continue
                
                # Generate appropriate value based on input type
                if use_random_values:
                    value = self._generate_random_value(input_info['input_type'])
                else:
                    value = self._generate_generic_value(input_info['input_type'])
                
                # Try to fill the input
                try:
                    # Scroll into view
                    self.execute_js("arguments[0].scrollIntoView({block: 'center'});", input_elem)
                    
                    # Clear first
                    self._clear_input(input_elem)
                    
                    # Fill
                    input_elem.clear()
                    input_elem.send_keys(value)
                    
                    # Auto-click associated button if found
                    button_clicked = self._click_associated_button(input_elem)
                    if button_clicked:
                        print(f"  Input #{idx}: FILLED with '{value[:30]}...' (type: {input_info['input_type']}) + button clicked")
                    else:
                        print(f"  Input #{idx}: FILLED with '{value[:30]}...' (type: {input_info['input_type']})")
                    
                    results['filled'] += 1
                    results['details'].append({
                        'index': idx,
                        'status': 'filled',
                        'value': value,
                        'type': input_info['input_type'],
                        'button_clicked': button_clicked
                    })
                except Exception as e:
                    print(f"  Input #{idx}: FAILED - {str(e)}")
                    results['failed'] += 1
                    results['details'].append({
                        'index': idx,
                        'status': 'failed',
                        'error': str(e),
                        'type': input_info['input_type']
                    })
                    
            except Exception as e:
                print(f"  Input #{idx}: ERROR - {str(e)}")
                results['failed'] += 1
                results['details'].append({
                    'index': idx,
                    'status': 'error',
                    'error': str(e)
                })
        
        print(f"\n{'='*70}")
        print(f"FILL SUMMARY")
        print(f"{'='*70}")
        print(f"Total: {results['total']}")
        print(f"Filled: {results['filled']}")
        print(f"Skipped: {results['skipped']}")
        print(f"Failed: {results['failed']}")
        print(f"{'='*70}\n")
        
        return results
    
    def _generate_random_value(self, input_type: str) -> str:
        """
        Generate a random value based on input type
        
        Args:
            input_type: Type of input (text, email, password, number, etc.)
            
        Returns:
            Random value string
        """
        import random
        import string
        
        if input_type == 'email':
            domains = ['example.com', 'test.com', 'demo.org', 'sample.net']
            username = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 10)))
            return f"{username}@{random.choice(domains)}"
        
        elif input_type == 'password':
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            return ''.join(random.choices(chars, k=random.randint(8, 16)))
        
        elif input_type == 'number':
            return str(random.randint(1000, 999999))
        
        elif input_type == 'tel' or input_type == 'phone':
            return f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        elif input_type == 'url':
            domains = ['example.com', 'test.com', 'demo.org']
            paths = ['page', 'article', 'post', 'item']
            return f"https://{random.choice(domains)}/{random.choice(paths)}/{random.randint(1, 100)}"
        
        elif input_type == 'search':
            words = ['test', 'sample', 'demo', 'example', 'search', 'query']
            return f"{random.choice(words)} {random.choice(words)}"
        
        elif input_type == 'textarea':
            sentences = [
                "This is a sample text area content.",
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sample description text for testing purposes.",
                "Random text content for automation testing."
            ]
            return random.choice(sentences)
        
        else:  # text or default
            words = ['Test', 'Sample', 'Demo', 'Example', 'Random', 'Input', 'Field', 'Value']
            return f"{random.choice(words)} {random.choice(words)} {random.randint(1, 100)}"
    
    def _generate_generic_value(self, input_type: str) -> str:
        """
        Generate a generic value based on input type
        
        Args:
            input_type: Type of input
            
        Returns:
            Generic value string
        """
        values = {
            'email': 'test@example.com',
            'password': 'TestPassword123',
            'number': '12345',
            'tel': '123-456-7890',
            'url': 'https://example.com',
            'search': 'test search',
            'textarea': 'Sample text area content for testing.',
            'text': 'Sample Text Input'
        }
        return values.get(input_type, 'Sample Input Value')
    
    # Delegate methods for backward compatibility
    def find_input_by_data_attr(self, data_attr_id: str, timeout: int = 10) -> Optional[WebElement]:
        """Delegate to InputLocator"""
        return self.locator.find_input_by_data_attr(data_attr_id, timeout, self.context)
    
    def find_input_by_label(self, label_text: str, exact_match: bool = False, timeout: int = 10) -> Optional[WebElement]:
        """Delegate to InputLocator"""
        return self.locator.find_input_by_label(label_text, exact_match, timeout, self.context)
    
    def find_input_by_type(self, input_type: str, timeout: int = 10) -> List[WebElement]:
        """Delegate to InputLocator"""
        return self.locator.find_input_by_type(input_type, timeout, self.context)
    
    def find_all_ant_inputs(self, timeout: int = 10, include_all: bool = False) -> List[WebElement]:
        """Delegate to InputLocator"""
        return self.locator.find_all_ant_inputs(timeout, include_all=include_all)
    
    def identify_input_type(self, element: WebElement) -> Dict[str, any]:
        """Delegate to InputIdentifier"""
        return self.identifier.identify_input_type(element)

