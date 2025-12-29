"""
Generic Ant Design Switch Handler
Handles switch interactions (toggle, read state, etc.)
Uses SwitchLocator for finding switches and SwitchIdentifier for analyzing them
Uses ElementContext for context-driven interactions
"""
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from typing import Optional, Dict, List
from framework.base.base_page import BasePage
from framework.components.switch_locator import SwitchLocator
from framework.components.switch_identifier import SwitchIdentifier
from framework.context.element_context import ElementContext, ElementInfo
import time


class SwitchHandler(BasePage):
    """
    Generic handler for Ant Design Switch component interactions
    Single Responsibility: Handle switch interactions (toggle, read state, etc.)
    Uses SwitchLocator to find switches and SwitchIdentifier to analyze them
    """
    
    def __init__(self, driver: webdriver, context: Optional[ElementContext] = None):
        """
        Initialize Switch Handler
        
        Args:
            driver: Selenium WebDriver instance
            context: Optional ElementContext for context-driven interactions
        """
        super().__init__(driver)
        self.locator = SwitchLocator(driver)
        self.identifier = SwitchIdentifier()
        self.context = context
    
    def identify_and_store(self, identifier: str, identifier_type: str = 'auto',
                          timeout: int = 10, context_key: Optional[str] = None) -> bool:
        """
        Identify a switch and store it in context
        
        Args:
            identifier: Value to identify the switch (data-attr-id, label, or position)
            identifier_type: Type of identifier ('data_attr_id', 'label', 'position', 'auto')
            timeout: Maximum wait time in seconds
            context_key: Optional key to use in context
            
        Returns:
            True if switch was identified and stored, False otherwise
        """
        if not self.context:
            print("Context not available. Cannot store element.")
            return False
        
        element = None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_switch_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'label' or identifier_type == 'semantic':
                element = self.locator.find_switch_by_semantic_label(identifier, timeout, self.context)
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                element = self.locator.find_switch_by_position(position, timeout=timeout, context=self.context)
            elif identifier_type == 'auto':
                # PRIORITY ORDER: pattern discovery -> data-attr-id -> semantic label -> position
                try:
                    from framework.utils.pattern_discovery import PatternDiscovery
                    pattern_discovery = PatternDiscovery(self.driver)
                    
                    # Normalize identifier for pattern matching
                    normalized_id = identifier.lower().replace(' ', '-').replace('_', '-')
                    
                    # Try to find matching data-attr-id using pattern discovery
                    matching_attr_id = pattern_discovery.find_matching_data_attr_id(normalized_id, 'switch')
                    if matching_attr_id:
                        element = self.locator.find_switch_by_data_attr(matching_attr_id, timeout=3, context=self.context)
                        if element:
                            print(f"   >> Found using pattern discovery: {matching_attr_id}")
                    
                    # If not found, generate candidates based on discovered pattern
                    if not element:
                        candidates = pattern_discovery.generate_candidates(normalized_id, 'switch')
                        for candidate in candidates:
                            element = self.locator.find_switch_by_data_attr(candidate, timeout=2, context=self.context)
                            if element:
                                print(f"   >> Found using pattern candidate: {candidate}")
                                break
                except Exception as e:
                    print(f"   >> Pattern discovery failed: {str(e)}")
                
                # Fallback to direct data-attr-id search
                if not element:
                    element = self.locator.find_switch_by_data_attr(identifier, timeout=3, context=self.context)
                
                # Fallback to semantic label search
                if not element:
                    element = self.locator.find_switch_by_semantic_label(identifier, timeout=3, context=self.context)
            
            if element:
                if context_key and context_key != identifier:
                    element_info = self.context.get_element(identifier) or self.context.get_current()
                    if element_info:
                        self.context.store_element(context_key, element_info)
                print(f"Switch identified and stored in context: {identifier}")
                return True
            else:
                print(f"Switch not found with identifier: {identifier} (type: {identifier_type})")
                return False
                
        except Exception as e:
            print(f"Error identifying switch: {str(e)}")
            return False
    
    def toggle_switch(self, identifier: str, identifier_type: str = 'auto',
                     timeout: int = 10, retry_count: int = 3, retry_delay: float = 0.5) -> bool:
        """
        Toggle a switch (turn ON if OFF, turn OFF if ON)
        Only toggles if switch is not disabled and not loading
        
        Args:
            identifier: Value to identify the switch
            identifier_type: Type of identifier ('data_attr_id', 'label', 'position', 'auto')
            timeout: Maximum wait time in seconds
            retry_count: Number of retries if toggle fails
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if switch was toggled successfully, False otherwise
        """
        element = self._find_switch(identifier, identifier_type, timeout)
        if not element:
            print(f"Switch not found: {identifier}")
            return False
        
        # Check if switch can be toggled
        switch_info = self.identifier.identify_switch_type(element)
        if switch_info['disabled']:
            print(f"Switch is disabled, cannot toggle: {identifier}")
            return False
        
        if switch_info['loading']:
            print(f"Switch is loading, cannot toggle: {identifier}")
            return False
        
        # Get current state
        current_state = switch_info['checked']
        target_state = not current_state
        
        # Toggle the switch using multiple strategies
        for attempt in range(retry_count):
            try:
                # Scroll into view (only if needed, faster)
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", element)
                    time.sleep(0.05)  # Reduced from 0.2
                except:
                    pass
                
                # Get the actual clickable element (checkbox input or switch itself)
                clickable_element = self._get_clickable_switch_element(element)
                
                # Strategy 1: Try regular click on clickable element
                try:
                    clickable_element.click()
                    # Success - no need to print
                    pass
                except (ElementNotInteractableException, Exception) as e:
                    # Strategy 2: Try JavaScript click (silent for speed)
                    try:
                        self.driver.execute_script("arguments[0].click();", clickable_element)
                    except Exception as js_e:
                        # Strategy 3: Try clicking the switch wrapper (silent for speed)
                        # Strategy 3: Try clicking the switch wrapper (parent)
                        try:
                            from selenium.webdriver.common.by import By
                            # Try to find and click the switch wrapper
                            switch_wrapper = clickable_element.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-switch")][1]')
                            if switch_wrapper:
                                switch_wrapper.click()
                            else:
                                raise Exception("No wrapper found")
                        except Exception as wrapper_e:
                            # Strategy 4: Try clicking parent element
                            try:
                                parent = clickable_element.find_element(By.XPATH, './..')
                                parent.click()
                            except Exception as parent_e:
                                # Strategy 5: Force click via JavaScript with event dispatch
                                try:
                                    self.driver.execute_script("""
                                        var element = arguments[0];
                                        // Try to trigger change event for checkbox
                                        if (element.type === 'checkbox') {
                                            element.checked = !element.checked;
                                        }
                                        // Dispatch click event
                                        var event = new MouseEvent('click', {
                                            view: window,
                                            bubbles: true,
                                            cancelable: true
                                        });
                                        element.dispatchEvent(event);
                                        // Also try change event
                                        var changeEvent = new Event('change', {
                                            bubbles: true,
                                            cancelable: true
                                        });
                                        element.dispatchEvent(changeEvent);
                                    """, clickable_element)
                                except Exception as event_e:
                                    # Strategy 6: Last resort - click anywhere on the switch
                                    try:
                                        from selenium.webdriver.common.action_chains import ActionChains
                                        ActionChains(self.driver).move_to_element(clickable_element).click().perform()
                                    except Exception as action_e:
                                        raise Exception(f"All click strategies failed. Last error: {str(action_e)}")
                
                # Wait for state change with animation delay (optimized for speed)
                # Ant Design switches have animations, but we can check faster
                time.sleep(retry_delay * 0.5)  # Reduced initial wait
                
                # Wait for DOM to update (check for class changes) - faster polling
                max_wait = retry_delay * 1.5  # Reduced max wait
                waited = 0
                state_changed = False
                
                while waited < max_wait:
                    try:
                        # Re-find element to avoid stale element issues (only if needed)
                        if waited > 0.2:  # Only re-find after initial check
                            fresh_element = self._find_switch(identifier, identifier_type, timeout=1)
                            if not fresh_element:
                                fresh_element = element  # Fallback to original
                        else:
                            fresh_element = element
                        
                        # Verify state changed
                        new_switch_info = self.identifier.identify_switch_type(fresh_element)
                        if new_switch_info['checked'] == target_state:
                            state_changed = True
                            break
                        
                        time.sleep(0.1)  # Faster polling (reduced from 0.2)
                        waited += 0.1
                    except:
                        time.sleep(0.1)
                        waited += 0.1
                
                if state_changed:
                    print(f"   ✓ Switch toggled successfully: {identifier} ({'ON' if target_state else 'OFF'})")
                    return True
                else:
                    # Get final state for error message
                    try:
                        final_element = self._find_switch(identifier, identifier_type, timeout=2)
                        if not final_element:
                            final_element = element
                        final_info = self.identifier.identify_switch_type(final_element)
                        final_state = final_info['checked']
                    except:
                        final_state = current_state
                    
                    if attempt < retry_count - 1:
                        print(f"   ⚠ State change not detected (current: {'ON' if final_state else 'OFF'}, expected: {'ON' if target_state else 'OFF'}), retrying... (attempt {attempt + 1}/{retry_count})")
                        time.sleep(retry_delay * 1.5)  # Longer wait on retry
                    else:
                        print(f"   ✗ Switch state did not change after {retry_count} attempts: {identifier}")
                        print(f"      Current state: {'ON' if final_state else 'OFF'}, Expected: {'ON' if target_state else 'OFF'}")
                        # Try one more time with force JavaScript toggle
                        try:
                            print(f"   → Attempting force JavaScript toggle...")
                            final_element = self._find_switch(identifier, identifier_type, timeout=2) or element
                            clickable = self._get_clickable_switch_element(final_element)
                            self.driver.execute_script("""
                                var elem = arguments[0];
                                if (elem.type === 'checkbox') {
                                    elem.checked = arguments[1];
                                    elem.dispatchEvent(new Event('change', {bubbles: true}));
                                }
                            """, clickable, target_state)
                            time.sleep(0.5)
                            # Verify one more time
                            final_info = self.identifier.identify_switch_type(final_element)
                            if final_info['checked'] == target_state:
                                print(f"   ✓ Switch toggled via force JavaScript: {identifier}")
                                return True
                        except:
                            pass
                        return False
                        
            except ElementNotInteractableException as e:
                if attempt < retry_count - 1:
                    print(f"   ⚠ Switch not interactable, retrying... (attempt {attempt + 1}/{retry_count}): {str(e)}")
                    time.sleep(retry_delay)
                else:
                    print(f"   ✗ Switch not interactable after {retry_count} attempts: {identifier}")
                    return False
            except Exception as e:
                if attempt < retry_count - 1:
                    print(f"   ⚠ Error toggling switch, retrying... (attempt {attempt + 1}/{retry_count}): {str(e)}")
                    time.sleep(retry_delay)
                else:
                    print(f"   ✗ Error toggling switch after {retry_count} attempts: {str(e)}")
                    return False
        
        return False
    
    def turn_on(self, identifier: str, identifier_type: str = 'auto',
               timeout: int = 10, retry_count: int = 3, retry_delay: float = 0.5) -> bool:
        """
        Turn switch ON (only if currently OFF)
        Idempotent: does nothing if already ON
        
        Args:
            identifier: Value to identify the switch
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            retry_count: Number of retries if toggle fails
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if switch is ON (was already ON or successfully turned ON), False otherwise
        """
        element = self._find_switch(identifier, identifier_type, timeout)
        if not element:
            print(f"Switch not found: {identifier}")
            return False
        
        switch_info = self.identifier.identify_switch_type(element)
        
        # Already ON
        if switch_info['checked']:
            print(f"Switch is already ON: {identifier}")
            return True
        
        # Turn ON
        return self.toggle_switch(identifier, identifier_type, timeout, retry_count, retry_delay)
    
    def toggle_switch_element(self, element: WebElement, target_state: Optional[bool] = None,
                             retry_count: int = 3, retry_delay: float = 0.5) -> bool:
        """
        Toggle a switch element directly (without re-finding it)
        Works with the WebElement object directly - more reliable for batch operations
        
        Args:
            element: WebElement of the switch to toggle
            target_state: True to turn ON, False to turn OFF, None to toggle
            retry_count: Number of retries if toggle fails
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if switch was toggled successfully, False otherwise
        """
        try:
            # Check if switch can be toggled
            switch_info = self.identifier.identify_switch_type(element)
            if switch_info['disabled']:
                return False
            if switch_info['loading']:
                return False
            
            # Get current state
            current_state = switch_info['checked']
            if target_state is None:
                target_state = not current_state
            
            # If already in target state, return True
            if current_state == target_state:
                return True
            
            # Toggle the switch using multiple strategies
            for attempt in range(retry_count):
                try:
                    # Scroll into view
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", element)
                        time.sleep(0.05)
                    except:
                        pass
                    
                    # Get the actual clickable element
                    clickable_element = self._get_clickable_switch_element(element)
                    
                    # Strategy 1: Try clicking the switch wrapper/container (Ant Design pattern)
                    clicked = False
                    try:
                        from selenium.webdriver.common.by import By
                        # Try to find and click the ant-switch wrapper
                        switch_wrapper = element.find_element(By.XPATH, './/*[contains(@class, "ant-switch")]')
                        if switch_wrapper:
                            switch_wrapper.click()
                            clicked = True
                    except:
                        pass
                    
                    # Strategy 2: Try regular click on clickable element
                    if not clicked:
                        try:
                            clickable_element.click()
                            clicked = True
                        except Exception:
                            pass
                    
                    # Strategy 3: Try JavaScript click on switch element
                    if not clicked:
                        try:
                            self.driver.execute_script("arguments[0].click();", element)
                            clicked = True
                        except Exception:
                            pass
                    
                    # Strategy 4: Try JavaScript click on clickable element
                    if not clicked:
                        try:
                            self.driver.execute_script("arguments[0].click();", clickable_element)
                            clicked = True
                        except Exception:
                            pass
                    
                    # Strategy 5: Force toggle via JavaScript (for React-controlled switches)
                    if not clicked:
                        try:
                            self.driver.execute_script("""
                                var elem = arguments[0];
                                var targetState = arguments[1];
                                
                                // Try to find checkbox input
                                var checkbox = elem;
                                if (elem.tagName !== 'INPUT') {
                                    checkbox = elem.querySelector('input[type="checkbox"]');
                                    if (!checkbox) {
                                        checkbox = elem;
                                    }
                                }
                                
                                // Set checked state
                                if (checkbox.type === 'checkbox') {
                                    checkbox.checked = targetState;
                                    // Trigger React onChange event
                                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                    nativeInputValueSetter.call(checkbox, targetState);
                                    var ev2 = new Event('input', { bubbles: true});
                                    checkbox.dispatchEvent(ev2);
                                    // Also trigger change event
                                    var changeEvent = new Event('change', {bubbles: true, cancelable: true});
                                    checkbox.dispatchEvent(changeEvent);
                                    // And click event
                                    var clickEvent = new MouseEvent('click', {bubbles: true, cancelable: true});
                                    checkbox.dispatchEvent(clickEvent);
                                }
                            """, element, target_state)
                            clicked = True
                        except Exception:
                            pass
                    
                    # Strategy 6: Try ActionChains
                    if not clicked:
                        try:
                            from selenium.webdriver.common.action_chains import ActionChains
                            ActionChains(self.driver).move_to_element(element).click().perform()
                            clicked = True
                        except Exception:
                            pass
                    
                    if not clicked and attempt == retry_count - 1:
                        return False
                    
                    # Wait for state change (longer wait for Ant Design animations)
                    time.sleep(retry_delay * 0.8)  # Increased initial wait
                    max_wait = retry_delay * 2.0  # Increased max wait for React state updates
                    waited = 0
                    state_changed = False
                    
                    while waited < max_wait:
                        try:
                            # Re-check state - try to refresh element if stale
                            try:
                                new_switch_info = self.identifier.identify_switch_type(element)
                            except:
                                # Element might be stale, try to re-find by class
                                try:
                                    from selenium.webdriver.common.by import By
                                    # Try to find a fresh element with same classes
                                    classes = element.get_attribute('class') or ''
                                    if 'ant-switch' in classes:
                                        fresh_elements = self.driver.find_elements(By.CSS_SELECTOR, '.ant-switch')
                                        if fresh_elements:
                                            # Use first matching element (simplified)
                                            element = fresh_elements[0]
                                            new_switch_info = self.identifier.identify_switch_type(element)
                                        else:
                                            break
                                    else:
                                        break
                                except:
                                    break
                            
                            if new_switch_info['checked'] == target_state:
                                state_changed = True
                                break
                            time.sleep(0.15)  # Slightly longer polling
                            waited += 0.15
                        except:
                            time.sleep(0.15)
                            waited += 0.15
                    
                    if state_changed:
                        return True
                    elif attempt < retry_count - 1:
                        time.sleep(retry_delay)
                    else:
                        return False
                        
                except Exception as e:
                    if attempt < retry_count - 1:
                        time.sleep(retry_delay)
                    else:
                        return False
            
            return False
        except Exception as e:
            return False
    
    def turn_off(self, identifier: str, identifier_type: str = 'auto',
                 timeout: int = 10, retry_count: int = 3, retry_delay: float = 0.5) -> bool:
        """
        Turn switch OFF (only if currently ON)
        Idempotent: does nothing if already OFF
        
        Args:
            identifier: Value to identify the switch
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            retry_count: Number of retries if toggle fails
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if switch is OFF (was already OFF or successfully turned OFF), False otherwise
        """
        element = self._find_switch(identifier, identifier_type, timeout)
        if not element:
            print(f"Switch not found: {identifier}")
            return False
        
        switch_info = self.identifier.identify_switch_type(element)
        
        # Already OFF
        if not switch_info['checked']:
            print(f"Switch is already OFF: {identifier}")
            return True
        
        # Turn OFF
        return self.toggle_switch(identifier, identifier_type, timeout, retry_count, retry_delay)
    
    def get_switch_state(self, identifier: str, identifier_type: str = 'auto',
                        timeout: int = 10) -> Optional[Dict[str, any]]:
        """
        Get current state and properties of a switch
        
        Args:
            identifier: Value to identify the switch
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            Dictionary with switch state and properties, or None if not found
        """
        element = self._find_switch(identifier, identifier_type, timeout)
        if not element:
            print(f"Switch not found: {identifier}")
            return None
        
        return self.identifier.identify_switch_type(element)
    
    def is_switch_on(self, identifier: str, identifier_type: str = 'auto',
                    timeout: int = 10) -> Optional[bool]:
        """
        Check if switch is ON (checked)
        
        Args:
            identifier: Value to identify the switch
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            True if ON, False if OFF, None if not found
        """
        state = self.get_switch_state(identifier, identifier_type, timeout)
        if state is None:
            return None
        return state['checked']
    
    def is_switch_off(self, identifier: str, identifier_type: str = 'auto',
                     timeout: int = 10) -> Optional[bool]:
        """
        Check if switch is OFF (unchecked)
        
        Args:
            identifier: Value to identify the switch
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            True if OFF, False if ON, None if not found
        """
        state = self.get_switch_state(identifier, identifier_type, timeout)
        if state is None:
            return None
        return not state['checked']
    
    def toggle_first_switch(self, timeout: int = 10, retry_count: int = 3,
                           retry_delay: float = 0.5) -> bool:
        """
        Toggle the first switch on the page
        
        Args:
            timeout: Maximum wait time in seconds
            retry_count: Number of retries if toggle fails
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if switch was toggled successfully, False otherwise
        """
        return self.toggle_switch('1', 'position', timeout, retry_count, retry_delay)
    
    def toggle_switch_by_index(self, index: int, timeout: int = 10,
                               retry_count: int = 3, retry_delay: float = 0.5) -> bool:
        """
        Toggle switch by index (1-based)
        
        Args:
            index: Index of switch (1-based)
            timeout: Maximum wait time in seconds
            retry_count: Number of retries if toggle fails
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if switch was toggled successfully, False otherwise
        """
        return self.toggle_switch(str(index), 'position', timeout, retry_count, retry_delay)
    
    def toggle_all_switches_matching(self, condition: Dict[str, any], timeout: int = 10,
                                    retry_count: int = 3, retry_delay: float = 0.5) -> List[bool]:
        """
        Toggle all switches matching a condition
        
        Args:
            condition: Dictionary with conditions (e.g., {'checked': True, 'disabled': False})
            timeout: Maximum wait time in seconds
            retry_count: Number of retries if toggle fails
            retry_delay: Delay between retries in seconds
            
        Returns:
            List of boolean results for each toggle operation
        """
        switches = self.locator.find_all_switches(timeout)
        results = []
        
        for switch in switches:
            switch_info = self.identifier.identify_switch_type(switch)
            
            # Check if switch matches condition
            matches = True
            for key, value in condition.items():
                if switch_info.get(key) != value:
                    matches = False
                    break
            
            if matches:
                # Get identifier for this switch
                identifier = switch_info.get('data_attr_id') or f"switch_{switches.index(switch) + 1}"
                result = self.toggle_switch(identifier, 'auto', timeout, retry_count, retry_delay)
                results.append(result)
        
        return results
    
    def turn_all_switches_on(self, timeout: int = 10, retry_count: int = 1, 
                            retry_delay: float = 0.1, skip_disabled: bool = True) -> Dict[str, int]:
        """
        Turn all switches ON (idempotent - skips already ON switches)
        
        Args:
            timeout: Maximum wait time in seconds
            retry_count: Number of retries if toggle fails
            retry_delay: Delay between retries in seconds
            skip_disabled: If True, skip disabled switches
            
        Returns:
            Dictionary with counts: {'turned_on': int, 'already_on': int, 'skipped': int, 'failed': int}
        """
        switches = self.locator.find_all_switches(timeout)
        results = {
            'turned_on': 0,
            'already_on': 0,
            'skipped': 0,
            'failed': 0
        }
        
        for idx, switch in enumerate(switches, 1):
            try:
                switch_info = self.identifier.identify_switch_type(switch)
                
                # Skip disabled or loading switches
                if skip_disabled and (switch_info['disabled'] or switch_info['loading']):
                    results['skipped'] += 1
                    continue
                
                # Already ON
                if switch_info['checked']:
                    results['already_on'] += 1
                    continue
                
                # Turn ON
                identifier = switch_info.get('data_attr_id') or f"switch_{idx}"
                success = self.turn_on(identifier, 'auto', timeout, retry_count, retry_delay)
                if success:
                    results['turned_on'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                results['failed'] += 1
                # Reduced verbosity for speed
                if idx <= 3:  # Only print first few errors
                    pass
        
        return results
    
    def turn_all_switches_off(self, timeout: int = 10, retry_count: int = 1,
                             retry_delay: float = 0.1, skip_disabled: bool = True) -> Dict[str, int]:
        """
        Turn all switches OFF (idempotent - skips already OFF switches)
        
        Args:
            timeout: Maximum wait time in seconds
            retry_count: Number of retries if toggle fails
            retry_delay: Delay between retries in seconds
            skip_disabled: If True, skip disabled switches
            
        Returns:
            Dictionary with counts: {'turned_off': int, 'already_off': int, 'skipped': int, 'failed': int}
        """
        switches = self.locator.find_all_switches(timeout)
        results = {
            'turned_off': 0,
            'already_off': 0,
            'skipped': 0,
            'failed': 0
        }
        
        for idx, switch in enumerate(switches, 1):
            try:
                switch_info = self.identifier.identify_switch_type(switch)
                
                # Skip disabled or loading switches
                if skip_disabled and (switch_info['disabled'] or switch_info['loading']):
                    results['skipped'] += 1
                    continue
                
                # Already OFF
                if not switch_info['checked']:
                    results['already_off'] += 1
                    continue
                
                # Turn OFF
                identifier = switch_info.get('data_attr_id') or f"switch_{idx}"
                success = self.turn_off(identifier, 'auto', timeout, retry_count, retry_delay)
                if success:
                    results['turned_off'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                results['failed'] += 1
                # Reduced verbosity for speed
                if idx <= 3:  # Only print first few errors
                    pass
        
        return results
    
    def toggle_all_switches(self, timeout: int = 10, retry_count: int = 1,
                           retry_delay: float = 0.1, skip_disabled: bool = True) -> Dict[str, int]:
        """
        Toggle all switches (turn ON if OFF, turn OFF if ON)
        
        Args:
            timeout: Maximum wait time in seconds
            retry_count: Number of retries if toggle fails
            retry_delay: Delay between retries in seconds
            skip_disabled: If True, skip disabled switches
            
        Returns:
            Dictionary with counts: {'toggled': int, 'skipped': int, 'failed': int}
        """
        switches = self.locator.find_all_switches(timeout)
        results = {
            'toggled': 0,
            'skipped': 0,
            'failed': 0
        }
        
        for idx, switch in enumerate(switches, 1):
            try:
                switch_info = self.identifier.identify_switch_type(switch)
                
                # Skip disabled or loading switches
                if skip_disabled and (switch_info['disabled'] or switch_info['loading']):
                    results['skipped'] += 1
                    continue
                
                # Toggle
                identifier = switch_info.get('data_attr_id') or f"switch_{idx}"
                success = self.toggle_switch(identifier, 'auto', timeout, retry_count, retry_delay)
                if success:
                    results['toggled'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                results['failed'] += 1
                # Reduced verbosity for speed
                if idx <= 3:  # Only print first few errors
                    print(f"   ⚠ Error toggling switch {idx}: {str(e)}")
        
        return results
    
    def get_all_switches_summary(self, timeout: int = 10) -> Dict[str, any]:
        """
        Get a summary of all switches on the page
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            Dictionary with summary:
            {
                'total_count': int,
                'on_count': int,
                'off_count': int,
                'disabled_count': int,
                'loading_count': int,
                'switches': List[Dict]  # Detailed info for each switch
            }
        """
        import time
        start_time = time.time()
        
        print(f"   → Finding all switches (timeout: {timeout}s)...")
        switches = self.locator.find_all_switches(timeout)
        print(f"   → Found {len(switches)} switch(es), analyzing...")
        
        summary = {
            'total_count': len(switches),
            'on_count': 0,
            'off_count': 0,
            'disabled_count': 0,
            'loading_count': 0,
            'switches': []
        }
        
        # Analyze switches with timeout protection
        max_analysis_time = 10  # Maximum 10 seconds for analysis
        for idx, switch in enumerate(switches):
            if time.time() - start_time > max_analysis_time:
                print(f"   ⚠ Analysis timeout after {idx}/{len(switches)} switches")
                break
            
            try:
                switch_info = self.identifier.identify_switch_type(switch)
                
                if switch_info['checked']:
                    summary['on_count'] += 1
                else:
                    summary['off_count'] += 1
                
                if switch_info['disabled']:
                    summary['disabled_count'] += 1
                
                if switch_info['loading']:
                    summary['loading_count'] += 1
                
                # Add identifier for each switch
                switch_info['identifier'] = switch_info.get('data_attr_id') or f"switch_{idx + 1}"
                summary['switches'].append(switch_info)
            except Exception as e:
                print(f"   ⚠ Error analyzing switch {idx + 1}: {str(e)}")
                # Add basic info even if analysis fails
                summary['switches'].append({
                    'identifier': f"switch_{idx + 1}",
                    'checked': False,
                    'disabled': False,
                    'loading': False,
                    'error': str(e)
                })
        
        return summary
    
    def print_switches_summary(self, timeout: int = 10):
        """
        Print a readable summary of all detected switches
        
        Args:
            timeout: Maximum wait time in seconds
        """
        summary = self.get_all_switches_summary(timeout)
        
        print("\n" + "="*60)
        print("SWITCH SUMMARY")
        print("="*60)
        print(f"Total Switches: {summary['total_count']}")
        print(f"  ON (Checked):  {summary['on_count']}")
        print(f"  OFF (Unchecked): {summary['off_count']}")
        print(f"  Disabled:      {summary['disabled_count']}")
        print(f"  Loading:       {summary['loading_count']}")
        print("-"*60)
        
        if summary['switches']:
            print("\nDetailed Switch Information:")
            for idx, switch_info in enumerate(summary['switches'], 1):
                state = "ON" if switch_info['checked'] else "OFF"
                disabled = " (DISABLED)" if switch_info['disabled'] else ""
                loading = " (LOADING)" if switch_info['loading'] else ""
                identifier = switch_info.get('identifier', f"Switch {idx}")
                
                print(f"  {idx}. {identifier}: {state}{disabled}{loading}")
                if switch_info.get('checked_label'):
                    print(f"      Checked Label: {switch_info['checked_label']}")
                if switch_info.get('unchecked_label'):
                    print(f"      Unchecked Label: {switch_info['unchecked_label']}")
                if switch_info.get('size') != 'default':
                    print(f"      Size: {switch_info['size']}")
        
        print("="*60 + "\n")
    
    def _find_switch(self, identifier: str, identifier_type: str, timeout: int) -> Optional[WebElement]:
        """
        Internal method to find a switch element
        Also ensures we get the actual clickable switch element (not wrapper)
        
        Args:
            identifier: Value to identify the switch
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement if found, None otherwise
        """
        element = None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_switch_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'label' or identifier_type == 'semantic':
                element = self.locator.find_switch_by_semantic_label(identifier, timeout, self.context)
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                element = self.locator.find_switch_by_position(position, timeout=timeout, context=self.context)
            elif identifier_type == 'auto':
                # Try pattern discovery first
                try:
                    from framework.utils.pattern_discovery import PatternDiscovery
                    pattern_discovery = PatternDiscovery(self.driver)
                    normalized_id = identifier.lower().replace(' ', '-').replace('_', '-')
                    matching_attr_id = pattern_discovery.find_matching_data_attr_id(normalized_id, 'switch')
                    if matching_attr_id:
                        element = self.locator.find_switch_by_data_attr(matching_attr_id, timeout=3, context=self.context)
                    
                    if not element:
                        candidates = pattern_discovery.generate_candidates(normalized_id, 'switch')
                        for candidate in candidates:
                            element = self.locator.find_switch_by_data_attr(candidate, timeout=2, context=self.context)
                            if element:
                                break
                except:
                    pass
                
                if not element:
                    element = self.locator.find_switch_by_data_attr(identifier, timeout=3, context=self.context)
                
                if not element:
                    element = self.locator.find_switch_by_semantic_label(identifier, timeout=3, context=self.context)
            
            # Ensure we have the actual switch element (not a wrapper)
            if element:
                element = self._get_clickable_switch_element(element)
                
        except Exception as e:
            print(f"Error finding switch: {str(e)}")
        
        return element
    
    def _get_clickable_switch_element(self, element: WebElement) -> WebElement:
        """
        Get the actual clickable switch element
        Ant Design switches might be wrapped, so we need to find the actual switch
        
        Args:
            element: Potential switch element or wrapper
            
        Returns:
            The actual clickable switch WebElement
        """
        from selenium.webdriver.common.by import By
        
        try:
            # Check if this element is already a switch
            if self.identifier.is_switch_element(element):
                # Check if it has a clickable input inside (preferred)
                try:
                    checkbox = element.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                    if checkbox:
                        return checkbox
                except:
                    pass
                return element
            
            # Try to find switch inside this element
            try:
                switch = element.find_element(By.CSS_SELECTOR, '.ant-switch, [role="switch"]')
                if switch:
                    # Check for checkbox inside
                    try:
                        checkbox = switch.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                        if checkbox:
                            return checkbox
                    except:
                        pass
                    return switch
            except:
                pass
            
            # Try to find checkbox input
            try:
                checkbox = element.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                if checkbox:
                    return checkbox
            except:
                pass
            
            # Return original element if we can't find better
            return element
            
        except Exception as e:
            print(f"   → Warning: Could not get clickable switch element: {str(e)}")
            return element

