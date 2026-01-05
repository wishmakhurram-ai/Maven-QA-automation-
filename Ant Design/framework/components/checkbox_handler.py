"""
Generic Ant Design Checkbox Handler
Handles checkbox interactions (checking, unchecking, reading state, validating, etc.)
Uses CheckboxLocator for finding checkboxes and CheckboxIdentifier for analyzing them
Uses ElementContext for context-driven interactions
"""
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from typing import Optional, Dict, List
from framework.base.base_page import BasePage
from framework.components.checkbox_locator import CheckboxLocator
from framework.components.checkbox_identifier import CheckboxIdentifier
from framework.context.element_context import ElementContext, ElementInfo
import time


class CheckboxHandler(BasePage):
    """
    Generic handler for Ant Design Checkbox component interactions
    Single Responsibility: Handle checkbox interactions (checking, unchecking, validating, etc.)
    Uses CheckboxLocator to find checkboxes and CheckboxIdentifier to analyze them
    """
    
    def __init__(self, driver: webdriver, context: Optional[ElementContext] = None):
        """
        Initialize Checkbox Handler
        
        Args:
            driver: Selenium WebDriver instance
            context: Optional ElementContext for context-driven interactions
        """
        super().__init__(driver)
        self.locator = CheckboxLocator(driver)
        self.identifier = CheckboxIdentifier()
        self.context = context
    
    def identify_and_store(self, identifier: str, identifier_type: str = 'auto',
                          timeout: int = 10, context_key: Optional[str] = None) -> bool:
        """
        Identify a checkbox and store it in context
        
        Args:
            identifier: Value to identify the checkbox (data-attr-id, label, or position)
            identifier_type: Type of identifier ('data_attr_id', 'label', 'position', 'auto')
            timeout: Maximum wait time in seconds
            context_key: Optional key to use in context
            
        Returns:
            True if checkbox was identified and stored, False otherwise
        """
        if not self.context:
            print("Context not available. Cannot store element.")
            return False
        
        element = None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_checkbox_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'label' or identifier_type == 'semantic':
                element = self.locator.find_checkbox_by_semantic_label(identifier, timeout=timeout, context=self.context)
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                element = self.locator.find_checkbox_by_position(position, timeout=timeout, context=self.context)
            elif identifier_type == 'auto':
                # PRIORITY ORDER: pattern discovery -> data-attr-id -> semantic label -> position
                try:
                    from framework.utils.pattern_discovery import PatternDiscovery
                    pattern_discovery = PatternDiscovery(self.driver)
                    
                    # Normalize identifier for pattern matching
                    normalized_id = identifier.lower().replace(' ', '-').replace('_', '-')
                    
                    # Try to find matching data-attr-id using pattern discovery
                    matching_attr_id = pattern_discovery.find_matching_data_attr_id(normalized_id, 'checkbox')
                    if matching_attr_id:
                        element = self.locator.find_checkbox_by_data_attr(matching_attr_id, timeout=3, context=self.context)
                        if element:
                            print(f"   >> Found using pattern discovery: {matching_attr_id}")
                    
                    # If not found, generate candidates based on discovered pattern
                    if not element:
                        candidates = pattern_discovery.generate_candidates(normalized_id, 'checkbox')
                        for candidate in candidates:
                            element = self.locator.find_checkbox_by_data_attr(candidate, timeout=2, context=self.context)
                            if element:
                                print(f"   >> Found using pattern candidate: {candidate}")
                                break
                except Exception as e:
                    print(f"   >> Pattern discovery failed: {str(e)}")
                
                # Fallback to direct data-attr-id search
                if not element:
                    element = self.locator.find_checkbox_by_data_attr(identifier, timeout=3, context=self.context)
                
                # Fallback to semantic label search
                if not element:
                    element = self.locator.find_checkbox_by_semantic_label(identifier, timeout=3, context=self.context)
            
            if element:
                if context_key and context_key != identifier:
                    element_info = self.context.get_element(identifier) or self.context.get_current()
                    if element_info:
                        self.context.store_element(context_key, element_info)
                print(f"Checkbox identified and stored in context: {identifier}")
                return True
            else:
                print(f"Checkbox not found with identifier: {identifier} (type: {identifier_type})")
                return False
                
        except Exception as e:
            print(f"Error identifying checkbox: {str(e)}")
            return False
    
    def check_checkbox(self, identifier: str, group_name: Optional[str] = None,
                      identifier_type: str = 'auto', timeout: int = 10,
                      retry_count: int = 3, retry_delay: float = 0.5) -> bool:
        """
        Check a checkbox (set to checked state)
        Handles "Check All" behavior automatically
        
        Args:
            identifier: Value to identify the checkbox (label, data-attr-id, or position)
            group_name: Optional checkbox group name to narrow search
            identifier_type: Type of identifier ('data_attr_id', 'label', 'position', 'auto')
            timeout: Maximum wait time in seconds
            retry_count: Number of retries if check fails
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if checkbox was checked successfully, False otherwise
        """
        element = self._find_checkbox(identifier, group_name, identifier_type, timeout)
        if not element:
            print(f"Checkbox not found: {identifier}")
            return False
        
        # Check if checkbox can be checked
        checkbox_info = self.identifier.identify_checkbox_type(element)
        if checkbox_info['disabled']:
            print(f"Checkbox is disabled, cannot check: {identifier}")
            return False
        
        # If already checked, return True
        if checkbox_info['checked']:
            print(f"Checkbox is already checked: {identifier}")
            return True
        
        # Handle "Check All" behavior
        if checkbox_info['has_check_all']:
            return self._handle_check_all(element, checkbox_info, retry_count, retry_delay)
        
        # Check the checkbox using multiple strategies
        return self._check_checkbox_element(element, retry_count, retry_delay)
    
    def uncheck_checkbox(self, identifier: str, group_name: Optional[str] = None,
                        identifier_type: str = 'auto', timeout: int = 10,
                        retry_count: int = 3, retry_delay: float = 0.5) -> bool:
        """
        Uncheck a checkbox (set to unchecked state)
        Handles "Check All" behavior automatically
        
        Args:
            identifier: Value to identify the checkbox (label, data-attr-id, or position)
            group_name: Optional checkbox group name to narrow search
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            retry_count: Number of retries if uncheck fails
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if checkbox was unchecked successfully, False otherwise
        """
        element = self._find_checkbox(identifier, group_name, identifier_type, timeout)
        if not element:
            print(f"Checkbox not found: {identifier}")
            return False
        
        # Check if checkbox can be unchecked
        checkbox_info = self.identifier.identify_checkbox_type(element)
        if checkbox_info['disabled']:
            print(f"Checkbox is disabled, cannot uncheck: {identifier}")
            return False
        
        # If already unchecked, return True
        if not checkbox_info['checked'] and not checkbox_info['indeterminate']:
            print(f"Checkbox is already unchecked: {identifier}")
            return True
        
        # Handle "Check All" behavior
        if checkbox_info['has_check_all']:
            return self._handle_uncheck_all(element, checkbox_info, retry_count, retry_delay)
        
        # Uncheck the checkbox
        return self._uncheck_checkbox_element(element, retry_count, retry_delay)
    
    def toggle_checkbox(self, identifier: str, group_name: Optional[str] = None,
                       identifier_type: str = 'auto', timeout: int = 10,
                       retry_count: int = 3, retry_delay: float = 0.5) -> bool:
        """
        Toggle checkbox state (check if unchecked, uncheck if checked)
        
        Args:
            identifier: Value to identify the checkbox
            group_name: Optional checkbox group name to narrow search
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            retry_count: Number of retries
            retry_delay: Delay between retries
            
        Returns:
            True if toggle was successful, False otherwise
        """
        element = self._find_checkbox(identifier, group_name, identifier_type, timeout)
        if not element:
            print(f"Checkbox not found: {identifier}")
            return False
        
        checkbox_info = self.identifier.identify_checkbox_type(element)
        if checkbox_info['disabled']:
            print(f"Checkbox is disabled, cannot toggle: {identifier}")
            return False
        
        if checkbox_info['checked'] or checkbox_info['indeterminate']:
            return self.uncheck_checkbox(identifier, group_name, identifier_type, timeout, retry_count, retry_delay)
        else:
            return self.check_checkbox(identifier, group_name, identifier_type, timeout, retry_count, retry_delay)
    
    def get_checkbox_state(self, identifier: str, group_name: Optional[str] = None,
                          identifier_type: str = 'auto', timeout: int = 10) -> Optional[Dict[str, any]]:
        """
        Get current state and properties of a checkbox
        
        Args:
            identifier: Value to identify the checkbox
            group_name: Optional checkbox group name to narrow search
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            Dictionary with checkbox state and properties, or None if not found
        """
        element = self._find_checkbox(identifier, group_name, identifier_type, timeout)
        if not element:
            print(f"Checkbox not found: {identifier}")
            return None
        
        return self.identifier.identify_checkbox_type(element)
    
    def is_checkbox_checked(self, identifier: str, group_name: Optional[str] = None,
                           identifier_type: str = 'auto', timeout: int = 10) -> Optional[bool]:
        """
        Check if checkbox is checked
        
        Args:
            identifier: Value to identify the checkbox
            group_name: Optional checkbox group name to narrow search
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            True if checked, False if unchecked, None if not found
        """
        state = self.get_checkbox_state(identifier, group_name, identifier_type, timeout)
        if state is None:
            return None
        return state['checked']
    
    def is_checkbox_indeterminate(self, identifier: str, group_name: Optional[str] = None,
                                 identifier_type: str = 'auto', timeout: int = 10) -> Optional[bool]:
        """
        Check if checkbox is in indeterminate state
        
        Args:
            identifier: Value to identify the checkbox
            group_name: Optional checkbox group name to narrow search
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            True if indeterminate, False otherwise, None if not found
        """
        state = self.get_checkbox_state(identifier, group_name, identifier_type, timeout)
        if state is None:
            return None
        return state['indeterminate']
    
    def get_group_info(self, group_name: str, timeout: int = 10) -> Optional[Dict[str, any]]:
        """
        Get information about a checkbox group
        
        Args:
            group_name: Group name or label
            timeout: Maximum wait time in seconds
            
        Returns:
            Dictionary with group information:
            {
                'group_name': str,
                'group_id': str|None,
                'total_options': int,
                'checked_options': List[str],  # List of checked option labels
                'checked_count': int,  # Number of checked options
                'checkboxes': List[Dict]  # Detailed info for each checkbox
            }
        """
        try:
            checkboxes = self.locator.find_checkboxes_in_group(group_name, timeout)
            if not checkboxes:
                print(f"Checkbox group not found: {group_name}")
                return None
            
            group_info = {
                'group_name': group_name,
                'group_id': None,
                'total_options': len(checkboxes),
                'checked_options': [],
                'checked_count': 0,
                'checkboxes': []
            }
            
            # Get group container
            group = self.locator.find_checkbox_group_by_name(group_name, timeout)
            if group:
                group_id_attr = group.get_attribute('data-attr-id') or group.get_attribute('data-atr-id')
                if group_id_attr:
                    group_info['group_id'] = group_id_attr
            
            # Analyze each checkbox
            for checkbox in checkboxes:
                checkbox_info = self.identifier.identify_checkbox_type(checkbox)
                group_info['checkboxes'].append(checkbox_info)
                
                if checkbox_info['checked']:
                    label = checkbox_info.get('label_text') or checkbox_info.get('value') or 'Checked'
                    group_info['checked_options'].append(label)
                    group_info['checked_count'] += 1
            
            return group_info
            
        except Exception as e:
            print(f"Error getting group info: {str(e)}")
            return None
    
    def get_all_checkboxes_summary(self, timeout: int = 10) -> Dict[str, any]:
        """
        Get a summary of all checkboxes on the page
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            Dictionary with summary:
            {
                'total_count': int,
                'total_groups': int,
                'checked_count': int,
                'disabled_count': int,
                'indeterminate_count': int,
                'groups': Dict[str, Dict],  # Group info by group name
                'checkboxes': List[Dict]  # Detailed info for each checkbox
            }
        """
        import time
        start_time = time.time()
        
        print(f"   → Finding all checkboxes (timeout: {timeout}s)...")
        checkboxes = self.locator.find_all_checkboxes(timeout)
        print(f"   → Found {len(checkboxes)} checkbox(es), analyzing...")
        
        summary = {
            'total_count': len(checkboxes),
            'total_groups': 0,
            'checked_count': 0,
            'disabled_count': 0,
            'indeterminate_count': 0,
            'groups': {},
            'checkboxes': []
        }
        
        # Track groups
        groups_seen = set()
        
        # Analyze checkboxes with timeout protection
        max_analysis_time = 30
        for idx, checkbox in enumerate(checkboxes):
            if time.time() - start_time > max_analysis_time:
                print(f"   ⚠ Analysis timeout after {idx}/{len(checkboxes)} checkboxes")
                break
            
            try:
                # Quick analysis
                checkbox_info = self._quick_identify_checkbox(checkbox)
                
                if checkbox_info['checked']:
                    summary['checked_count'] += 1
                
                if checkbox_info['disabled']:
                    summary['disabled_count'] += 1
                
                if checkbox_info['indeterminate']:
                    summary['indeterminate_count'] += 1
                
                # Track groups
                group_name = checkbox_info.get('group_name')
                if group_name:
                    if group_name not in groups_seen:
                        groups_seen.add(group_name)
                        summary['total_groups'] += 1
                        # Get full group info only once per group
                        try:
                            group_info = self.get_group_info(group_name, timeout=2)
                            if group_info:
                                summary['groups'][group_name] = {
                                    'group_name': group_name,
                                    'group_id': group_info.get('group_id'),
                                    'total_options': group_info.get('total_options', 0),
                                    'checked_count': group_info.get('checked_count', 0),
                                    'checked_options': group_info.get('checked_options', [])
                                }
                            else:
                                summary['groups'][group_name] = {
                                    'group_name': group_name,
                                    'group_id': checkbox_info.get('group_id'),
                                    'total_options': checkbox_info.get('total_in_group', 0),
                                    'checked_count': len(checkbox_info.get('checked_in_group', [])),
                                    'checked_options': checkbox_info.get('checked_in_group', [])
                                }
                        except:
                            summary['groups'][group_name] = {
                                'group_name': group_name,
                                'group_id': checkbox_info.get('group_id'),
                                'total_options': checkbox_info.get('total_in_group', 0),
                                'checked_count': len(checkbox_info.get('checked_in_group', [])),
                                'checked_options': checkbox_info.get('checked_in_group', [])
                            }
                
                # Add identifier for each checkbox
                checkbox_info['identifier'] = checkbox_info.get('data_attr_id') or checkbox_info.get('label_text') or f"checkbox_{idx + 1}"
                summary['checkboxes'].append(checkbox_info)
                
            except Exception as e:
                print(f"   ⚠ Error analyzing checkbox {idx + 1}: {str(e)}")
                summary['checkboxes'].append({
                    'identifier': f"checkbox_{idx + 1}",
                    'checked': False,
                    'disabled': False,
                    'indeterminate': False,
                    'error': str(e)
                })
        
        return summary
    
    def print_checkboxes_summary(self, timeout: int = 10):
        """
        Print a readable summary of all detected checkboxes
        
        Args:
            timeout: Maximum wait time in seconds
        """
        summary = self.get_all_checkboxes_summary(timeout)
        
        print("\n" + "="*60)
        print("CHECKBOX SUMMARY")
        print("="*60)
        print(f"Total Checkboxes: {summary['total_count']}")
        print(f"Total Groups: {summary['total_groups']}")
        print(f"  Checked:      {summary['checked_count']}")
        print(f"  Unchecked:    {summary['total_count'] - summary['checked_count']}")
        print(f"  Disabled:     {summary['disabled_count']}")
        print(f"  Indeterminate: {summary['indeterminate_count']}")
        print("-"*60)
        
        if summary['groups']:
            print("\nCheckbox Groups:")
            for group_name, group_info in summary['groups'].items():
                print(f"  Group: {group_name}")
                if group_info.get('group_id'):
                    print(f"    ID: {group_info['group_id']}")
                print(f"    Total Options: {group_info.get('total_options', 0)}")
                print(f"    Checked: {group_info.get('checked_count', 0)}")
                if group_info.get('checked_options'):
                    print(f"    Checked Options: {', '.join(group_info['checked_options'])}")
        
        if summary['checkboxes']:
            print("\nDetailed Checkbox Information:")
            for idx, checkbox_info in enumerate(summary['checkboxes'], 1):
                state = "CHECKED" if checkbox_info['checked'] else "UNCHECKED"
                if checkbox_info.get('indeterminate'):
                    state = "INDETERMINATE"
                disabled = " (DISABLED)" if checkbox_info['disabled'] else ""
                identifier = checkbox_info.get('identifier', f"Checkbox {idx}")
                
                print(f"  {idx}. {identifier}: {state}{disabled}")
                if checkbox_info.get('label_text'):
                    print(f"      Label: {checkbox_info['label_text']}")
                if checkbox_info.get('group_name'):
                    print(f"      Group: {checkbox_info['group_name']}")
                if checkbox_info.get('type') != 'basic':
                    print(f"      Type: {checkbox_info['type']}")
                if checkbox_info.get('has_check_all'):
                    print(f"      Has Check All: Yes")
        
        print("="*60 + "\n")
    
    def _find_checkbox(self, identifier: str, group_name: Optional[str], identifier_type: str, timeout: int) -> Optional[WebElement]:
        """
        Internal method to find a checkbox element
        
        Args:
            identifier: Value to identify the checkbox
            group_name: Optional checkbox group name to narrow search
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement if found, None otherwise
        """
        element = None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_checkbox_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'label' or identifier_type == 'semantic':
                element = self.locator.find_checkbox_by_semantic_label(identifier, group_name, timeout, self.context)
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                element = self.locator.find_checkbox_by_position(position, timeout=timeout, context=self.context)
            elif identifier_type == 'auto':
                # Try pattern discovery first
                try:
                    from framework.utils.pattern_discovery import PatternDiscovery
                    pattern_discovery = PatternDiscovery(self.driver)
                    normalized_id = identifier.lower().replace(' ', '-').replace('_', '-')
                    matching_attr_id = pattern_discovery.find_matching_data_attr_id(normalized_id, 'checkbox')
                    if matching_attr_id:
                        element = self.locator.find_checkbox_by_data_attr(matching_attr_id, timeout=3, context=self.context)
                    
                    if not element:
                        candidates = pattern_discovery.generate_candidates(normalized_id, 'checkbox')
                        for candidate in candidates:
                            element = self.locator.find_checkbox_by_data_attr(candidate, timeout=2, context=self.context)
                            if element:
                                break
                except:
                    pass
                
                if not element:
                    element = self.locator.find_checkbox_by_data_attr(identifier, timeout=3, context=self.context)
                
                if not element:
                    element = self.locator.find_checkbox_by_semantic_label(identifier, group_name, timeout=3, context=self.context)
            
        except Exception as e:
            print(f"Error finding checkbox: {str(e)}")
        
        return element
    
    def _check_checkbox_element(self, element: WebElement, retry_count: int = 3, retry_delay: float = 0.5) -> bool:
        """
        Check a checkbox element directly (internal method)
        
        Args:
            element: WebElement of the checkbox to check
            retry_count: Number of retries
            retry_delay: Delay between retries
            
        Returns:
            True if checked successfully, False otherwise
        """
        try:
            # Check if already checked
            checkbox_info = self.identifier.identify_checkbox_type(element)
            if checkbox_info['checked']:
                print(f"            [INFO] Checkbox is already checked, no action needed")
                return True
            
            if checkbox_info['disabled']:
                print(f"            [WARN] Checkbox is disabled, cannot check")
                return False
            
            # Scroll into view
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", element)
                time.sleep(0.1)
            except:
                pass
            
            # Get clickable element
            clickable_element = self._get_clickable_checkbox_element(element)
            
            # Try multiple strategies
            for attempt in range(retry_count):
                try:
                    # Strategy 1: Click wrapper (most reliable for Ant Design)
                    wrapper = self.identifier._find_checkbox_wrapper(element)
                    if wrapper:
                        try:
                            wrapper.click()
                            clicked = True
                        except:
                            self.driver.execute_script("arguments[0].click();", wrapper)
                            clicked = True
                    else:
                        clicked = False
                    
                    # Strategy 2: If no wrapper, click input directly
                    if not clicked and clickable_element:
                        if clickable_element.tag_name.lower() == 'input':
                            # Use JavaScript to set checked and trigger events
                            self.driver.execute_script("""
                                var elem = arguments[0];
                                if (elem.type === 'checkbox') {
                                    elem.checked = true;
                                    elem.dispatchEvent(new Event('change', {bubbles: true, cancelable: true}));
                                    elem.dispatchEvent(new Event('click', {bubbles: true, cancelable: true}));
                                    elem.dispatchEvent(new Event('input', {bubbles: true, cancelable: true}));
                                }
                            """, clickable_element)
                            clicked = True
                        else:
                            clickable_element.click()
                            clicked = True
                    
                    # Verify check
                    time.sleep(retry_delay * 0.8)
                    fresh_info = self.identifier.identify_checkbox_type(element)
                    if fresh_info['checked']:
                        print(f"            [VERIFIED] ✓ Checkbox checked successfully!")
                        return True
                    
                    if attempt < retry_count - 1:
                        time.sleep(retry_delay)
                    
                except Exception as e:
                    if attempt < retry_count - 1:
                        time.sleep(retry_delay)
                    else:
                        print(f"            [ERROR] Exception during attempt {attempt + 1}: {str(e)[:50]}")
            
            print(f"            [FAILED] Could not check checkbox after {retry_count} attempts")
            return False
            
        except Exception as e:
            print(f"            [ERROR] Fatal error: {str(e)[:50]}")
            return False
    
    def _uncheck_checkbox_element(self, element: WebElement, retry_count: int = 3, retry_delay: float = 0.5) -> bool:
        """
        Uncheck a checkbox element directly (internal method)
        
        Args:
            element: WebElement of the checkbox to uncheck
            retry_count: Number of retries
            retry_delay: Delay between retries
            
        Returns:
            True if unchecked successfully, False otherwise
        """
        try:
            # Check if already unchecked
            checkbox_info = self.identifier.identify_checkbox_type(element)
            if not checkbox_info['checked'] and not checkbox_info['indeterminate']:
                print(f"            [INFO] Checkbox is already unchecked, no action needed")
                return True
            
            if checkbox_info['disabled']:
                print(f"            [WARN] Checkbox is disabled, cannot uncheck")
                return False
            
            # Scroll into view
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", element)
                time.sleep(0.1)
            except:
                pass
            
            # Get clickable element
            clickable_element = self._get_clickable_checkbox_element(element)
            
            # Try multiple strategies
            for attempt in range(retry_count):
                try:
                    # Strategy 1: Click wrapper
                    wrapper = self.identifier._find_checkbox_wrapper(element)
                    if wrapper:
                        try:
                            wrapper.click()
                            clicked = True
                        except:
                            self.driver.execute_script("arguments[0].click();", wrapper)
                            clicked = True
                    else:
                        clicked = False
                    
                    # Strategy 2: If no wrapper, click input directly
                    if not clicked and clickable_element:
                        if clickable_element.tag_name.lower() == 'input':
                            # Use JavaScript to uncheck and trigger events
                            self.driver.execute_script("""
                                var elem = arguments[0];
                                if (elem.type === 'checkbox') {
                                    elem.checked = false;
                                    elem.indeterminate = false;
                                    elem.dispatchEvent(new Event('change', {bubbles: true, cancelable: true}));
                                    elem.dispatchEvent(new Event('click', {bubbles: true, cancelable: true}));
                                    elem.dispatchEvent(new Event('input', {bubbles: true, cancelable: true}));
                                }
                            """, clickable_element)
                            clicked = True
                        else:
                            clickable_element.click()
                            clicked = True
                    
                    # Verify uncheck
                    time.sleep(retry_delay * 0.8)
                    fresh_info = self.identifier.identify_checkbox_type(element)
                    if not fresh_info['checked'] and not fresh_info['indeterminate']:
                        print(f"            [VERIFIED] ✓ Checkbox unchecked successfully!")
                        return True
                    
                    if attempt < retry_count - 1:
                        time.sleep(retry_delay)
                    
                except Exception as e:
                    if attempt < retry_count - 1:
                        time.sleep(retry_delay)
                    else:
                        print(f"            [ERROR] Exception during attempt {attempt + 1}: {str(e)[:50]}")
            
            print(f"            [FAILED] Could not uncheck checkbox after {retry_count} attempts")
            return False
            
        except Exception as e:
            print(f"            [ERROR] Fatal error: {str(e)[:50]}")
            return False
    
    def _handle_check_all(self, element: WebElement, checkbox_info: Dict, retry_count: int, retry_delay: float) -> bool:
        """
        Handle "Check All" behavior - checking this checkbox should check all children
        
        Args:
            element: WebElement of the "Check All" checkbox
            checkbox_info: Checkbox information dictionary
            retry_count: Number of retries
            retry_delay: Delay between retries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"            [INFO] Detected 'Check All' checkbox, checking all children...")
            
            # First, check the "Check All" checkbox itself
            if not self._check_checkbox_element(element, retry_count, retry_delay):
                return False
            
            # Find all child checkboxes in the group
            group = self.identifier._find_checkbox_group(element)
            if group:
                from selenium.webdriver.common.by import By
                child_checkboxes = group.find_elements(By.CSS_SELECTOR, '.ant-checkbox-wrapper input[type="checkbox"]')
                
                # Filter out the "Check All" checkbox itself
                checkbox_input = self.identifier._find_checkbox_input(element)
                child_checkboxes = [cb for cb in child_checkboxes if cb != checkbox_input]
                
                # Check all child checkboxes
                for child_cb in child_checkboxes:
                    try:
                        wrapper = child_cb.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-checkbox-wrapper")][1]')
                        self._check_checkbox_element(wrapper, retry_count=1, retry_delay=0.2)
                    except:
                        continue
            
            # Verify that all are checked
            time.sleep(retry_delay)
            fresh_info = self.identifier.identify_checkbox_type(element)
            if fresh_info['checked']:
                print(f"            [VERIFIED] ✓ 'Check All' and all children checked successfully!")
                return True
            
            return False
            
        except Exception as e:
            print(f"            [ERROR] Error handling 'Check All': {str(e)[:50]}")
            return False
    
    def _handle_uncheck_all(self, element: WebElement, checkbox_info: Dict, retry_count: int, retry_delay: float) -> bool:
        """
        Handle "Check All" behavior - unchecking this checkbox should uncheck all children
        
        Args:
            element: WebElement of the "Check All" checkbox
            checkbox_info: Checkbox information dictionary
            retry_count: Number of retries
            retry_delay: Delay between retries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"            [INFO] Detected 'Check All' checkbox, unchecking all children...")
            
            # First, uncheck the "Check All" checkbox itself
            if not self._uncheck_checkbox_element(element, retry_count, retry_delay):
                return False
            
            # Find all child checkboxes in the group
            group = self.identifier._find_checkbox_group(element)
            if group:
                from selenium.webdriver.common.by import By
                child_checkboxes = group.find_elements(By.CSS_SELECTOR, '.ant-checkbox-wrapper input[type="checkbox"]')
                
                # Filter out the "Check All" checkbox itself
                checkbox_input = self.identifier._find_checkbox_input(element)
                child_checkboxes = [cb for cb in child_checkboxes if cb != checkbox_input]
                
                # Uncheck all child checkboxes
                for child_cb in child_checkboxes:
                    try:
                        wrapper = child_cb.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-checkbox-wrapper")][1]')
                        self._uncheck_checkbox_element(wrapper, retry_count=1, retry_delay=0.2)
                    except:
                        continue
            
            # Verify that all are unchecked
            time.sleep(retry_delay)
            fresh_info = self.identifier.identify_checkbox_type(element)
            if not fresh_info['checked'] and not fresh_info['indeterminate']:
                print(f"            [VERIFIED] ✓ 'Check All' and all children unchecked successfully!")
                return True
            
            return False
            
        except Exception as e:
            print(f"            [ERROR] Error handling 'Check All': {str(e)[:50]}")
            return False
    
    def _quick_identify_checkbox(self, element: WebElement) -> Dict[str, any]:
        """
        Quick checkbox identification for summary (faster, skips expensive operations)
        
        Args:
            element: WebElement representing the checkbox
            
        Returns:
            Dictionary with basic checkbox properties
        """
        checkbox_info = {
            'type': 'basic',
            'checked': False,
            'disabled': False,
            'indeterminate': False,
            'label_text': None,
            'data_attr_id': None,
            'group_name': None,
            'group_id': None,
            'total_in_group': None,
            'checked_in_group': None,
            'has_check_all': False,
            'identifier': None
        }
        
        try:
            from selenium.webdriver.common.by import By
            
            # Quick check - find checkbox input
            try:
                if element.tag_name.lower() == 'input' and element.get_attribute('type') == 'checkbox':
                    checkbox_input = element
                else:
                    checkbox_input = element.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                
                if checkbox_input:
                    checkbox_info['checked'] = checkbox_input.is_selected()
                    checkbox_info['disabled'] = not checkbox_input.is_enabled() or checkbox_input.get_attribute('disabled') is not None
                    checkbox_info['group_name'] = checkbox_input.get_attribute('name')
                    checkbox_info['value'] = checkbox_input.get_attribute('value')
                    
                    # Check for indeterminate via JavaScript
                    try:
                        is_indeterminate = checkbox_input.get_property('indeterminate')
                        if is_indeterminate:
                            checkbox_info['indeterminate'] = True
                    except:
                        pass
            except:
                pass
            
            # Quick label extraction
            try:
                class_attr = element.get_attribute('class') or ''
                if 'ant-checkbox-checked' in class_attr:
                    checkbox_info['checked'] = True
                if 'ant-checkbox-disabled' in class_attr:
                    checkbox_info['disabled'] = True
                if 'ant-checkbox-indeterminate' in class_attr:
                    checkbox_info['indeterminate'] = True
                
                # Get text quickly
                text = element.text.strip()
                if text:
                    checkbox_info['label_text'] = text[:50]  # Limit length
            except:
                pass
            
            # Get data-attr-id quickly
            try:
                checkbox_info['data_attr_id'] = element.get_attribute('data-attr-id') or element.get_attribute('data-atr-id')
            except:
                pass
            
        except:
            pass
        
        return checkbox_info
    
    def _get_clickable_checkbox_element(self, element: WebElement) -> WebElement:
        """
        Get the actual clickable checkbox element
        Ant Design checkboxes might be wrapped, so we need to find the actual input
        
        Args:
            element: Potential checkbox element or wrapper
            
        Returns:
            The actual clickable checkbox WebElement
        """
        from selenium.webdriver.common.by import By
        
        try:
            # Check if element is already input[type="checkbox"]
            if element.tag_name.lower() == 'input' and element.get_attribute('type') == 'checkbox':
                return element
            
            # Try to find checkbox input inside
            try:
                checkbox_input = element.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                if checkbox_input:
                    return checkbox_input
            except:
                pass
            
            # Try to find in wrapper
            try:
                wrapper = self.identifier._find_checkbox_wrapper(element)
                if wrapper:
                    checkbox_input = wrapper.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                    if checkbox_input:
                        return checkbox_input
                    return wrapper
            except:
                pass
            
            # Return wrapper if it's clickable
            wrapper = self.identifier._find_checkbox_wrapper(element)
            if wrapper:
                return wrapper
            
            # Return original element if we can't find better
            return element
            
        except Exception as e:
            print(f"   → Warning: Could not get clickable checkbox element: {str(e)}")
            return element

