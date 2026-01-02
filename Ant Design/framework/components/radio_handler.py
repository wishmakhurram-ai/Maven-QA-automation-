"""
Generic Ant Design Radio Handler
Handles radio interactions (selecting, reading state, validating, etc.)
Uses RadioLocator for finding radios and RadioIdentifier for analyzing them
Uses ElementContext for context-driven interactions
"""
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from typing import Optional, Dict, List
from framework.base.base_page import BasePage
from framework.components.radio_locator import RadioLocator
from framework.components.radio_identifier import RadioIdentifier
from framework.context.element_context import ElementContext, ElementInfo
import time


class RadioHandler(BasePage):
    """
    Generic handler for Ant Design Radio component interactions
    Single Responsibility: Handle radio interactions (selecting, validating, etc.)
    Uses RadioLocator to find radios and RadioIdentifier to analyze them
    """
    
    def __init__(self, driver: webdriver, context: Optional[ElementContext] = None):
        """
        Initialize Radio Handler
        
        Args:
            driver: Selenium WebDriver instance
            context: Optional ElementContext for context-driven interactions
        """
        super().__init__(driver)
        self.locator = RadioLocator(driver)
        self.identifier = RadioIdentifier()
        self.context = context
    
    def identify_and_store(self, identifier: str, identifier_type: str = 'auto',
                          timeout: int = 10, context_key: Optional[str] = None) -> bool:
        """
        Identify a radio and store it in context
        
        Args:
            identifier: Value to identify the radio (data-attr-id, label, or position)
            identifier_type: Type of identifier ('data_attr_id', 'label', 'position', 'auto')
            timeout: Maximum wait time in seconds
            context_key: Optional key to use in context
            
        Returns:
            True if radio was identified and stored, False otherwise
        """
        if not self.context:
            print("Context not available. Cannot store element.")
            return False
        
        element = None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_radio_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'label' or identifier_type == 'semantic':
                element = self.locator.find_radio_by_semantic_label(identifier, timeout=timeout, context=self.context)
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                element = self.locator.find_radio_by_position(position, timeout=timeout, context=self.context)
            elif identifier_type == 'auto':
                # PRIORITY ORDER: pattern discovery -> data-attr-id -> semantic label -> position
                try:
                    from framework.utils.pattern_discovery import PatternDiscovery
                    pattern_discovery = PatternDiscovery(self.driver)
                    
                    # Normalize identifier for pattern matching
                    normalized_id = identifier.lower().replace(' ', '-').replace('_', '-')
                    
                    # Try to find matching data-attr-id using pattern discovery
                    matching_attr_id = pattern_discovery.find_matching_data_attr_id(normalized_id, 'radio')
                    if matching_attr_id:
                        element = self.locator.find_radio_by_data_attr(matching_attr_id, timeout=3, context=self.context)
                        if element:
                            print(f"   >> Found using pattern discovery: {matching_attr_id}")
                    
                    # If not found, generate candidates based on discovered pattern
                    if not element:
                        candidates = pattern_discovery.generate_candidates(normalized_id, 'radio')
                        for candidate in candidates:
                            element = self.locator.find_radio_by_data_attr(candidate, timeout=2, context=self.context)
                            if element:
                                print(f"   >> Found using pattern candidate: {candidate}")
                                break
                except Exception as e:
                    print(f"   >> Pattern discovery failed: {str(e)}")
                
                # Fallback to direct data-attr-id search
                if not element:
                    element = self.locator.find_radio_by_data_attr(identifier, timeout=3, context=self.context)
                
                # Fallback to semantic label search
                if not element:
                    element = self.locator.find_radio_by_semantic_label(identifier, timeout=3, context=self.context)
            
            if element:
                if context_key and context_key != identifier:
                    element_info = self.context.get_element(identifier) or self.context.get_current()
                    if element_info:
                        self.context.store_element(context_key, element_info)
                print(f"Radio identified and stored in context: {identifier}")
                return True
            else:
                print(f"Radio not found with identifier: {identifier} (type: {identifier_type})")
                return False
                
        except Exception as e:
            print(f"Error identifying radio: {str(e)}")
            return False
    
    def select_radio(self, identifier: str, group_name: Optional[str] = None,
                    identifier_type: str = 'auto', timeout: int = 10,
                    retry_count: int = 3, retry_delay: float = 0.5) -> bool:
        """
        Select a radio option
        If radio is in a group, automatically deselects other options in the same group
        
        Args:
            identifier: Value to identify the radio (label, data-attr-id, or position)
            group_name: Optional radio group name to narrow search
            identifier_type: Type of identifier ('data_attr_id', 'label', 'position', 'auto')
            timeout: Maximum wait time in seconds
            retry_count: Number of retries if selection fails
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if radio was selected successfully, False otherwise
        """
        element = self._find_radio(identifier, group_name, identifier_type, timeout)
        if not element:
            print(f"Radio not found: {identifier}")
            return False
        
        # Check if radio can be selected
        radio_info = self.identifier.identify_radio_type(element)
        if radio_info['disabled']:
            print(f"Radio is disabled, cannot select: {identifier}")
            return False
        
        # If already selected, return True
        if radio_info['selected']:
            print(f"Radio is already selected: {identifier}")
            return True
        
        # Select the radio using multiple strategies
        for attempt in range(retry_count):
            try:
                # Scroll into view
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", element)
                    time.sleep(0.05)
                except:
                    pass
                
                # Get the actual clickable element (radio input or wrapper)
                clickable_element = self._get_clickable_radio_element(element)
                
                # Strategy 1: Try clicking the wrapper first (most reliable for Ant Design)
                clicked = False
                try:
                    wrapper = self.identifier._find_radio_wrapper(element)
                    if wrapper:
                        # Try wrapper click first
                        try:
                            wrapper.click()
                            clicked = True
                        except:
                            # Try JavaScript on wrapper
                            self.driver.execute_script("arguments[0].click();", wrapper)
                            clicked = True
                except:
                    pass
                
                # Strategy 2: If wrapper click failed, try radio input
                if not clicked:
                    try:
                        if clickable_element.tag_name.lower() == 'input':
                            # For input, use JavaScript to set checked and trigger events
                            self.driver.execute_script("""
                                var elem = arguments[0];
                                if (elem.type === 'radio') {
                                    // Uncheck other radios in same group first
                                    var name = elem.name;
                                    if (name) {
                                        var radios = document.querySelectorAll('input[type="radio"][name="' + name + '"]');
                                        radios.forEach(function(r) { r.checked = false; });
                                    }
                                    // Check this radio
                                    elem.checked = true;
                                    // Trigger events
                                    elem.dispatchEvent(new Event('change', {bubbles: true, cancelable: true}));
                                    elem.dispatchEvent(new Event('click', {bubbles: true, cancelable: true}));
                                    elem.dispatchEvent(new Event('input', {bubbles: true, cancelable: true}));
                                }
                            """, clickable_element)
                            clicked = True
                        else:
                            # Try regular click
                            clickable_element.click()
                            clicked = True
                    except (ElementNotInteractableException, Exception) as e:
                        # Strategy 3: Try JavaScript click on element
                        try:
                            self.driver.execute_script("arguments[0].click();", clickable_element)
                            clicked = True
                        except Exception as js_e:
                            # Strategy 4: Force select via JavaScript
                            try:
                                self.driver.execute_script("""
                                    var elem = arguments[0];
                                    if (elem.type === 'radio') {
                                        var name = elem.name;
                                        if (name) {
                                            var radios = document.querySelectorAll('input[type="radio"][name="' + name + '"]');
                                            radios.forEach(function(r) { r.checked = false; });
                                        }
                                        elem.checked = true;
                                        elem.dispatchEvent(new Event('change', {bubbles: true}));
                                        elem.dispatchEvent(new Event('click', {bubbles: true}));
                                    }
                                """, clickable_element)
                                clicked = True
                            except:
                                clicked = False
                
                if not clicked:
                    if attempt < retry_count - 1:
                        print(f"   ⚠ Click failed, retrying... (attempt {attempt + 1}/{retry_count})")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"   ✗ Failed to select radio after {retry_count} attempts: {identifier}")
                        return False
                
                # Wait for selection to take effect
                time.sleep(retry_delay * 0.5)
                
                # Verify selection
                max_wait = retry_delay * 1.5
                waited = 0
                selection_confirmed = False
                
                while waited < max_wait:
                    try:
                        # Re-find element to avoid stale element issues
                        fresh_element = self._find_radio(identifier, group_name, identifier_type, timeout=1)
                        if not fresh_element:
                            fresh_element = element
                        
                        new_radio_info = self.identifier.identify_radio_type(fresh_element)
                        if new_radio_info['selected']:
                            selection_confirmed = True
                            break
                        
                        time.sleep(0.1)
                        waited += 0.1
                    except:
                        time.sleep(0.1)
                        waited += 0.1
                
                if selection_confirmed:
                    print(f"   ✓ Radio selected successfully: {identifier}")
                    return True
                else:
                    if attempt < retry_count - 1:
                        print(f"   ⚠ Selection not confirmed, retrying... (attempt {attempt + 1}/{retry_count})")
                        time.sleep(retry_delay)
                    else:
                        print(f"   ✗ Radio selection not confirmed after {retry_count} attempts: {identifier}")
                        return False
                        
            except Exception as e:
                if attempt < retry_count - 1:
                    print(f"   ⚠ Error selecting radio, retrying... (attempt {attempt + 1}/{retry_count}): {str(e)}")
                    time.sleep(retry_delay)
                else:
                    print(f"   ✗ Error selecting radio after {retry_count} attempts: {str(e)}")
                    return False
        
        return False
    
    def _select_radio_element(self, element: WebElement, retry_count: int = 3, retry_delay: float = 0.5) -> bool:
        """
        Select a radio element directly (internal method for better performance)
        
        Args:
            element: WebElement of the radio to select
            retry_count: Number of retries
            retry_delay: Delay between retries
            
        Returns:
            True if selected successfully, False otherwise
        """
        try:
            print(f"            [STEP 2] Checking radio state...")
            # Check if already selected
            radio_info = self.identifier.identify_radio_type(element)
            if radio_info['selected']:
                print(f"            [INFO] Radio is already selected, no action needed")
                return True
            
            if radio_info['disabled']:
                print(f"            [WARN] Radio is disabled, cannot select")
                return False
            
            print(f"            [STEP 3] Scrolling radio into view...")
            # Scroll into view
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", element)
                time.sleep(0.1)
                print(f"            [OK] Radio scrolled into view")
            except Exception as e:
                print(f"            [WARN] Could not scroll into view: {str(e)[:30]}")
            
            print(f"            [STEP 4] Finding clickable radio element...")
            # Get clickable element
            clickable_element = self._get_clickable_radio_element(element)
            element_type = clickable_element.tag_name.lower() if clickable_element else "unknown"
            print(f"            [OK] Found clickable element: {element_type}")
            
            # Try multiple strategies
            for attempt in range(retry_count):
                try:
                    print(f"            [STEP 5] Attempt {attempt + 1}/{retry_count}: Attempting to click radio...")
                    
                    # Strategy 1: Click wrapper (most reliable for Ant Design)
                    wrapper = self.identifier._find_radio_wrapper(element)
                    if wrapper:
                        print(f"               [STRATEGY 1] Trying to click radio wrapper...")
                        try:
                            wrapper.click()
                            clicked = True
                            print(f"               [SUCCESS] Clicked wrapper successfully")
                        except Exception as e:
                            print(f"               [FALLBACK] Regular click failed, trying JavaScript click...")
                            self.driver.execute_script("arguments[0].click();", wrapper)
                            clicked = True
                            print(f"               [SUCCESS] JavaScript click on wrapper successful")
                    else:
                        clicked = False
                        print(f"               [INFO] No wrapper found, will try input element")
                    
                    # Strategy 2: If no wrapper, click input directly with JavaScript
                    if not clicked and clickable_element:
                        print(f"               [STRATEGY 2] Clicking radio input via JavaScript...")
                        print(f"                  [ACTION] Unchecking other radios in same group...")
                        self.driver.execute_script("""
                            var elem = arguments[0];
                            if (elem.type === 'radio') {
                                var name = elem.name;
                                if (name) {
                                    var radios = document.querySelectorAll('input[type="radio"][name="' + name + '"]');
                                    radios.forEach(function(r) { 
                                        r.checked = false;
                                        r.dispatchEvent(new Event('change', {bubbles: true}));
                                    });
                                }
                                elem.checked = true;
                                elem.dispatchEvent(new Event('change', {bubbles: true, cancelable: true}));
                                elem.dispatchEvent(new Event('click', {bubbles: true, cancelable: true}));
                                elem.dispatchEvent(new Event('input', {bubbles: true, cancelable: true}));
                            }
                        """, clickable_element)
                        clicked = True
                        print(f"               [SUCCESS] JavaScript selection successful")
                    
                    if not clicked:
                        print(f"               [WARN] All click strategies failed")
                    
                    # Verify selection
                    print(f"            [STEP 6] Verifying selection...")
                    time.sleep(retry_delay * 0.8)
                    fresh_info = self.identifier.identify_radio_type(element)
                    if fresh_info['selected']:
                        print(f"            [VERIFIED] ✓ Radio selection confirmed!")
                        return True
                    else:
                        print(f"            [WARN] Selection not yet confirmed, current state: {'selected' if fresh_info['selected'] else 'unselected'}")
                    
                    if attempt < retry_count - 1:
                        print(f"            [RETRY] Waiting {retry_delay}s before retry...")
                        time.sleep(retry_delay)
                    
                except Exception as e:
                    print(f"            [ERROR] Exception during attempt {attempt + 1}: {str(e)[:50]}")
                    if attempt < retry_count - 1:
                        print(f"            [RETRY] Waiting {retry_delay}s before retry...")
                        time.sleep(retry_delay)
                    else:
                        print(f"            [FAILED] All attempts exhausted")
                        return False
            
            print(f"            [FAILED] Could not select radio after {retry_count} attempts")
            return False
            
        except Exception as e:
            print(f"            [ERROR] Fatal error: {str(e)[:50]}")
            return False
    
    def get_radio_state(self, identifier: str, group_name: Optional[str] = None,
                       identifier_type: str = 'auto', timeout: int = 10) -> Optional[Dict[str, any]]:
        """
        Get current state and properties of a radio
        
        Args:
            identifier: Value to identify the radio
            group_name: Optional radio group name to narrow search
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            Dictionary with radio state and properties, or None if not found
        """
        element = self._find_radio(identifier, group_name, identifier_type, timeout)
        if not element:
            print(f"Radio not found: {identifier}")
            return None
        
        return self.identifier.identify_radio_type(element)
    
    def is_radio_selected(self, identifier: str, group_name: Optional[str] = None,
                          identifier_type: str = 'auto', timeout: int = 10) -> Optional[bool]:
        """
        Check if radio is selected
        
        Args:
            identifier: Value to identify the radio
            group_name: Optional radio group name to narrow search
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            True if selected, False if not selected, None if not found
        """
        state = self.get_radio_state(identifier, group_name, identifier_type, timeout)
        if state is None:
            return None
        return state['selected']
    
    def get_group_info(self, group_name: str, timeout: int = 10) -> Optional[Dict[str, any]]:
        """
        Get information about a radio group
        
        Args:
            group_name: Group name or label
            timeout: Maximum wait time in seconds
            
        Returns:
            Dictionary with group information:
            {
                'group_name': str,
                'group_id': str|None,
                'total_options': int,
                'selected_option': str|None,
                'radios': List[Dict]  # Detailed info for each radio
            }
        """
        try:
            radios = self.locator.find_radios_in_group(group_name, timeout)
            if not radios:
                print(f"Radio group not found: {group_name}")
                return None
            
            group_info = {
                'group_name': group_name,
                'group_id': None,
                'total_options': len(radios),
                'selected_option': None,
                'radios': []
            }
            
            # Get group container
            group = self.locator.find_radio_group_by_name(group_name, timeout)
            if group:
                group_id_attr = group.get_attribute('data-attr-id') or group.get_attribute('data-atr-id')
                if group_id_attr:
                    group_info['group_id'] = group_id_attr
            
            # Analyze each radio
            for radio in radios:
                radio_info = self.identifier.identify_radio_type(radio)
                group_info['radios'].append(radio_info)
                
                if radio_info['selected']:
                    group_info['selected_option'] = radio_info.get('label_text') or radio_info.get('value') or 'Selected'
            
            return group_info
            
        except Exception as e:
            print(f"Error getting group info: {str(e)}")
            return None
    
    def get_all_radios_summary(self, timeout: int = 10) -> Dict[str, any]:
        """
        Get a summary of all radios on the page
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            Dictionary with summary:
            {
                'total_count': int,
                'total_groups': int,
                'selected_count': int,
                'disabled_count': int,
                'groups': Dict[str, Dict],  # Group info by group name
                'radios': List[Dict]  # Detailed info for each radio
            }
        """
        import time
        start_time = time.time()
        
        print(f"   → Finding all radios (timeout: {timeout}s)...")
        radios = self.locator.find_all_radios(timeout)
        print(f"   → Found {len(radios)} radio(s), analyzing...")
        
        summary = {
            'total_count': len(radios),
            'total_groups': 0,
            'selected_count': 0,
            'disabled_count': 0,
            'groups': {},
            'radios': []
        }
        
        # Track groups
        groups_seen = set()
        
        # Analyze radios with timeout protection - increased timeout and optimized
        max_analysis_time = 30  # Increased to 30 seconds for analysis
        for idx, radio in enumerate(radios):
            if time.time() - start_time > max_analysis_time:
                print(f"   ⚠ Analysis timeout after {idx}/{len(radios)} radios")
                break
            
            try:
                # Quick analysis - skip expensive operations for summary
                radio_info = self._quick_identify_radio(radio)
                
                if radio_info['selected']:
                    summary['selected_count'] += 1
                
                if radio_info['disabled']:
                    summary['disabled_count'] += 1
                
                # Track groups
                group_name = radio_info.get('group_name')
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
                                    'selected_option': group_info.get('selected_option')
                                }
                            else:
                                summary['groups'][group_name] = {
                                    'group_name': group_name,
                                    'group_id': radio_info.get('group_id'),
                                    'total_options': radio_info.get('total_in_group', 0),
                                    'selected_option': radio_info.get('selected_in_group')
                                }
                        except:
                            summary['groups'][group_name] = {
                                'group_name': group_name,
                                'group_id': radio_info.get('group_id'),
                                'total_options': radio_info.get('total_in_group', 0),
                                'selected_option': radio_info.get('selected_in_group')
                            }
                
                # Add identifier for each radio
                radio_info['identifier'] = radio_info.get('data_attr_id') or radio_info.get('label_text') or f"radio_{idx + 1}"
                summary['radios'].append(radio_info)
                
            except Exception as e:
                print(f"   ⚠ Error analyzing radio {idx + 1}: {str(e)}")
                summary['radios'].append({
                    'identifier': f"radio_{idx + 1}",
                    'selected': False,
                    'disabled': False,
                    'error': str(e)
                })
        
        return summary
    
    def print_radios_summary(self, timeout: int = 10):
        """
        Print a readable summary of all detected radios
        
        Args:
            timeout: Maximum wait time in seconds
        """
        summary = self.get_all_radios_summary(timeout)
        
        print("\n" + "="*60)
        print("RADIO SUMMARY")
        print("="*60)
        print(f"Total Radios: {summary['total_count']}")
        print(f"Total Groups: {summary['total_groups']}")
        print(f"  Selected:   {summary['selected_count']}")
        print(f"  Disabled:   {summary['disabled_count']}")
        print("-"*60)
        
        if summary['groups']:
            print("\nRadio Groups:")
            for group_name, group_info in summary['groups'].items():
                print(f"  Group: {group_name}")
                if group_info.get('group_id'):
                    print(f"    ID: {group_info['group_id']}")
                print(f"    Total Options: {group_info.get('total_options', 0)}")
                if group_info.get('selected_option'):
                    print(f"    Selected: {group_info['selected_option']}")
                else:
                    print(f"    Selected: None")
        
        if summary['radios']:
            print("\nDetailed Radio Information:")
            for idx, radio_info in enumerate(summary['radios'], 1):
                state = "SELECTED" if radio_info['selected'] else "UNSELECTED"
                disabled = " (DISABLED)" if radio_info['disabled'] else ""
                identifier = radio_info.get('identifier', f"Radio {idx}")
                
                print(f"  {idx}. {identifier}: {state}{disabled}")
                if radio_info.get('label_text'):
                    print(f"      Label: {radio_info['label_text']}")
                if radio_info.get('group_name'):
                    print(f"      Group: {radio_info['group_name']}")
                if radio_info.get('type') != 'basic':
                    print(f"      Type: {radio_info['type']}")
        
        print("="*60 + "\n")
    
    def _find_radio(self, identifier: str, group_name: Optional[str], identifier_type: str, timeout: int) -> Optional[WebElement]:
        """
        Internal method to find a radio element
        
        Args:
            identifier: Value to identify the radio
            group_name: Optional radio group name to narrow search
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement if found, None otherwise
        """
        element = None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_radio_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'label' or identifier_type == 'semantic':
                element = self.locator.find_radio_by_semantic_label(identifier, group_name, timeout, self.context)
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                element = self.locator.find_radio_by_position(position, timeout=timeout, context=self.context)
            elif identifier_type == 'auto':
                # Try pattern discovery first
                try:
                    from framework.utils.pattern_discovery import PatternDiscovery
                    pattern_discovery = PatternDiscovery(self.driver)
                    normalized_id = identifier.lower().replace(' ', '-').replace('_', '-')
                    matching_attr_id = pattern_discovery.find_matching_data_attr_id(normalized_id, 'radio')
                    if matching_attr_id:
                        element = self.locator.find_radio_by_data_attr(matching_attr_id, timeout=3, context=self.context)
                    
                    if not element:
                        candidates = pattern_discovery.generate_candidates(normalized_id, 'radio')
                        for candidate in candidates:
                            element = self.locator.find_radio_by_data_attr(candidate, timeout=2, context=self.context)
                            if element:
                                break
                except:
                    pass
                
                if not element:
                    element = self.locator.find_radio_by_data_attr(identifier, timeout=3, context=self.context)
                
                if not element:
                    element = self.locator.find_radio_by_semantic_label(identifier, group_name, timeout=3, context=self.context)
            
        except Exception as e:
            print(f"Error finding radio: {str(e)}")
        
        return element
    
    def _quick_identify_radio(self, element: WebElement) -> Dict[str, any]:
        """
        Quick radio identification for summary (faster, skips expensive operations)
        
        Args:
            element: WebElement representing the radio
            
        Returns:
            Dictionary with basic radio properties
        """
        radio_info = {
            'type': 'basic',
            'selected': False,
            'disabled': False,
            'label_text': None,
            'data_attr_id': None,
            'group_name': None,
            'group_id': None,
            'total_in_group': None,
            'selected_in_group': None,
            'identifier': None
        }
        
        try:
            from selenium.webdriver.common.by import By
            
            # Quick check - find radio input
            try:
                if element.tag_name.lower() == 'input' and element.get_attribute('type') == 'radio':
                    radio_input = element
                else:
                    radio_input = element.find_element(By.CSS_SELECTOR, 'input[type="radio"]')
                
                if radio_input:
                    radio_info['selected'] = radio_input.is_selected()
                    radio_info['disabled'] = not radio_input.is_enabled() or radio_input.get_attribute('disabled') is not None
                    radio_info['group_name'] = radio_input.get_attribute('name')
                    radio_info['value'] = radio_input.get_attribute('value')
            except:
                pass
            
            # Quick label extraction
            try:
                class_attr = element.get_attribute('class') or ''
                if 'ant-radio-checked' in class_attr:
                    radio_info['selected'] = True
                if 'ant-radio-disabled' in class_attr:
                    radio_info['disabled'] = True
                
                # Get text quickly
                text = element.text.strip()
                if text:
                    radio_info['label_text'] = text[:50]  # Limit length
            except:
                pass
            
            # Get data-attr-id quickly
            try:
                radio_info['data_attr_id'] = element.get_attribute('data-attr-id') or element.get_attribute('data-atr-id')
            except:
                pass
            
        except:
            pass
        
        return radio_info
    
    def _get_clickable_radio_element(self, element: WebElement) -> WebElement:
        """
        Get the actual clickable radio element
        Ant Design radios might be wrapped, so we need to find the actual input
        
        Args:
            element: Potential radio element or wrapper
            
        Returns:
            The actual clickable radio WebElement
        """
        from selenium.webdriver.common.by import By
        
        try:
            # Check if element is already input[type="radio"]
            if element.tag_name.lower() == 'input' and element.get_attribute('type') == 'radio':
                return element
            
            # Try to find radio input inside
            try:
                radio_input = element.find_element(By.CSS_SELECTOR, 'input[type="radio"]')
                if radio_input:
                    return radio_input
            except:
                pass
            
            # Try to find in wrapper
            try:
                wrapper = self.identifier._find_radio_wrapper(element)
                if wrapper:
                    radio_input = wrapper.find_element(By.CSS_SELECTOR, 'input[type="radio"]')
                    if radio_input:
                        return radio_input
            except:
                pass
            
            # Return wrapper if it's clickable
            wrapper = self.identifier._find_radio_wrapper(element)
            if wrapper:
                return wrapper
            
            # Return original element if we can't find better
            return element
            
        except Exception as e:
            print(f"   → Warning: Could not get clickable radio element: {str(e)}")
            return element

