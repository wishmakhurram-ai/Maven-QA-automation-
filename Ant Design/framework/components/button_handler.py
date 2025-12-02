"""
Generic Ant Design Button Handler
Handles button interactions (clicking, scrolling, waiting, etc.)
Uses ButtonLocator for finding buttons and ButtonIdentifier for analyzing them
Uses ElementContext for context-driven interactions
"""
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from typing import Optional, Dict, List
from framework.base.base_page import BasePage
from framework.components.button_locator import ButtonLocator
from framework.components.button_identifier import ButtonIdentifier
from framework.context.element_context import ElementContext, ElementInfo


class ButtonHandler(BasePage):
    """
    Generic handler for Ant Design button interactions
    Single Responsibility: Handle button interactions (clicking, scrolling, waiting, js-click, etc.)
    Uses ButtonLocator to find buttons and ButtonIdentifier to analyze them
    """
    
    def __init__(self, driver: webdriver, context: Optional[ElementContext] = None):
        """
        Initialize Button Handler
        
        Args:
            driver: Selenium WebDriver instance
            context: Optional ElementContext for context-driven interactions
        """
        super().__init__(driver)
        self.locator = ButtonLocator(driver)
        self.identifier = ButtonIdentifier()
        self.context = context
    
    def identify_and_store(self, identifier: str, identifier_type: str = 'data_attr', 
                          timeout: int = 10, context_key: Optional[str] = None) -> bool:
        """
        Identify a button and store it in context
        
        Args:
            identifier: Value to identify the button (data-attr-id, text, or type)
            identifier_type: Type of identifier ('data_attr', 'text', 'type', 'auto')
            timeout: Maximum wait time in seconds
            context_key: Optional key to use in context (defaults to identifier or data-attr-id)
            
        Returns:
            True if button was identified and stored, False otherwise
        """
        if not self.context:
            print("Context not available. Cannot store element.")
            return False
        
        element = None
        
        try:
            if identifier_type == 'data_attr':
                element = self.locator.find_button_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'text':
                element = self.locator.find_button_by_text(identifier, exact_match=False, timeout=timeout, context=self.context)
            elif identifier_type == 'type':
                buttons = self.locator.find_button_by_type(identifier, timeout, self.context)
                if buttons:
                    element = buttons[0]
            elif identifier_type == 'auto':
                # Try multiple methods in order
                element = self.locator.find_button_by_data_attr(identifier, timeout=5, context=self.context)
                if not element:
                    element = self.locator.find_button_by_text(identifier, exact_match=False, timeout=5, context=self.context)
                if not element:
                    buttons = self.locator.find_button_by_type(identifier, timeout=5, context=self.context)
                    if buttons:
                        element = buttons[0]
            
            if element:
                # If context_key is provided and different from stored key, update it
                if context_key and context_key != identifier:
                    element_info = self.context.get_element(identifier) or self.context.get_current()
                    if element_info:
                        self.context.store_element(context_key, element_info)
                print(f"Button identified and stored in context: {identifier}")
                return True
            else:
                print(f"Button not found with identifier: {identifier} (type: {identifier_type})")
                return False
                
        except Exception as e:
            print(f"Error identifying button: {str(e)}")
            return False
    
    def click_from_context(self, context_key: Optional[str] = None) -> bool:
        """
        Click a button using context (context-driven interaction)
        
        Args:
            context_key: Optional key to retrieve element from context. If None, uses current element.
            
        Returns:
            True if button was clicked successfully, False otherwise
        """
        if not self.context:
            print("Context not available. Cannot click from context.")
            return False
        
        # Get element from context
        element_info = self.context.get_element(context_key) if context_key else self.context.get_current()
        
        if not element_info:
            print(f"Element not found in context with key: {context_key or 'current'}")
            return False
        
        element = element_info.element
        
        try:
            # Get button info from metadata
            button_info = element_info.metadata
            
            print(f"Clicking button from context - Type: {button_info.get('button_type', 'unknown')}, "
                  f"Text: '{button_info.get('text', '')}', "
                  f"Data-attr-id: {element_info.data_attr_id}")
            
            # Check if button is clickable
            if button_info.get('disabled', False):
                print(f"Button is disabled and cannot be clicked")
                return False
            
            if button_info.get('loading', False):
                print(f"Button is in loading state, waiting...")
                self.wait_for_loading_complete(element, timeout=30)
            
            # Scroll element into view if needed
            try:
                self.execute_js("arguments[0].scrollIntoView({block: 'center'});", element)
            except:
                pass
            
            # Try clicking with JavaScript if normal click fails
            try:
                element.click()
            except (ElementNotInteractableException, Exception) as e:
                # If element is stale or not interactable, try JavaScript click
                try:
                    print("Normal click failed, trying JavaScript click...")
                    self.execute_js("arguments[0].click();", element)
                except Exception as js_error:
                    # If JavaScript click also fails, try to re-find the button
                    print(f"JavaScript click failed: {str(js_error)}. Attempting to re-find button...")
                    
                    # Try to re-find using metadata
                    button_type = button_info.get('button_type') or button_info.get('type')
                    button_text = button_info.get('text', '').strip()
                    data_attr_id = element_info.data_attr_id
                    
                    # Try re-finding by data-attr-id first
                    if data_attr_id:
                        re_found = self.locator.find_button_by_data_attr(data_attr_id, timeout=5, context=self.context)
                        if re_found:
                            try:
                                re_found.click()
                                print("Successfully clicked re-found button (by data-attr-id)")
                                return True
                            except:
                                self.execute_js("arguments[0].click();", re_found)
                                print("Successfully clicked re-found button via JavaScript (by data-attr-id)")
                                return True
                    
                    # Try re-finding by text
                    if button_text:
                        re_found = self.locator.find_button_by_text(button_text, exact_match=False, timeout=5, context=self.context)
                        if re_found:
                            try:
                                re_found.click()
                                print("Successfully clicked re-found button (by text)")
                                return True
                            except:
                                self.execute_js("arguments[0].click();", re_found)
                                print("Successfully clicked re-found button via JavaScript (by text)")
                                return True
                    
                    # Try re-finding by type
                    if button_type:
                        re_found_buttons = self.locator.find_button_by_type(button_type, timeout=5, context=self.context)
                        if re_found_buttons:
                            try:
                                re_found_buttons[0].click()
                                print("Successfully clicked re-found button (by type)")
                                return True
                            except:
                                self.execute_js("arguments[0].click();", re_found_buttons[0])
                                print("Successfully clicked re-found button via JavaScript (by type)")
                                return True
                    
                    print(f"Could not re-find or click button after stale element error")
                    return False
            
            print(f"Successfully clicked button from context")
            return True
            
        except Exception as e:
            print(f"Error clicking button from context: {str(e)}")
            # Try to re-find and click
            try:
                button_info = element_info.metadata
                button_type = button_info.get('button_type') or button_info.get('type')
                button_text = button_info.get('text', '').strip()
                data_attr_id = element_info.data_attr_id
                
                if data_attr_id:
                    re_found = self.locator.find_button_by_data_attr(data_attr_id, timeout=5, context=self.context)
                    if re_found:
                        self.execute_js("arguments[0].click();", re_found)
                        return True
                elif button_text:
                    re_found = self.locator.find_button_by_text(button_text, exact_match=False, timeout=5, context=self.context)
                    if re_found:
                        self.execute_js("arguments[0].click();", re_found)
                        return True
                elif button_type:
                    re_found_buttons = self.locator.find_button_by_type(button_type, timeout=5, context=self.context)
                    if re_found_buttons:
                        self.execute_js("arguments[0].click();", re_found_buttons[0])
                        return True
            except:
                pass
            
            return False
    
    def click_button(self, identifier: str, identifier_type: str = 'data_attr', timeout: int = 10, 
                     use_context: bool = False) -> bool:
        """
        Generic method to click a button using various identification methods
        Can use context if use_context=True and context is available
        
        Args:
            identifier: Value to identify the button (data-attr-id, text, or type)
            identifier_type: Type of identifier ('data_attr', 'text', 'type', 'auto')
            timeout: Maximum wait time in seconds
            use_context: If True, tries to use context first, then falls back to locating
            
        Returns:
            True if button was clicked successfully, False otherwise
        """
        # Try context first if enabled
        if use_context and self.context:
            element_info = self.context.get_element(identifier)
            if element_info:
                return self.click_from_context(identifier)
        
        element = None
        
        try:
            # Pass context to locator methods so they can store elements
            context_to_use = self.context if use_context else None
            
            if identifier_type == 'data_attr':
                element = self.locator.find_button_by_data_attr(identifier, timeout, context_to_use)
            elif identifier_type == 'text':
                element = self.locator.find_button_by_text(identifier, exact_match=False, timeout=timeout, context=context_to_use)
            elif identifier_type == 'type':
                buttons = self.locator.find_button_by_type(identifier, timeout, context_to_use)
                if buttons:
                    element = buttons[0]  # Click first button of this type
            elif identifier_type == 'auto':
                # Try multiple methods in order
                element = self.locator.find_button_by_data_attr(identifier, timeout=5, context=context_to_use)
                if not element:
                    element = self.locator.find_button_by_text(identifier, exact_match=False, timeout=5, context=context_to_use)
                if not element:
                    buttons = self.locator.find_button_by_type(identifier, timeout=5, context=context_to_use)
                    if buttons:
                        element = buttons[0]
            
            if not element:
                print(f"Button not found with identifier: {identifier} (type: {identifier_type})")
                return False
            
            # Identify button type for logging
            button_info = self.identifier.identify_button_type(element)
            print(f"Found button - Type: {button_info['type']}, Text: '{button_info['text']}', "
                  f"Disabled: {button_info['disabled']}, Loading: {button_info['loading']}")
            
            # Check if button is clickable
            if button_info['disabled']:
                print(f"Button is disabled and cannot be clicked")
                return False
            
            if button_info['loading']:
                print(f"Button is in loading state, waiting...")
                # Wait for loading to complete
                self.wait_for_loading_complete(element, timeout=30)
            
            # Wait for element to be clickable
            # Since we already have the element, we'll use it directly
            # The element should already be clickable from the find methods
            clickable_element = element
            
            # Scroll element into view if needed
            try:
                self.execute_js("arguments[0].scrollIntoView({block: 'center'});", element)
            except:
                pass
            
            # Try clicking with JavaScript if normal click fails
            try:
                clickable_element.click()
            except ElementNotInteractableException:
                print("Normal click failed, trying JavaScript click...")
                self.execute_js("arguments[0].click();", clickable_element)
            
            print(f"Successfully clicked button: {identifier}")
            return True
            
        except Exception as e:
            print(f"Error clicking button: {str(e)}")
            return False
    
    def wait_for_loading_complete(self, element: WebElement, timeout: int = 30):
        """
        Wait for button loading state to complete
        
        Args:
            element: Button WebElement
            timeout: Maximum wait time in seconds
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(lambda driver: 'ant-btn-loading' not in element.get_attribute('class'))
        except TimeoutException:
            print("Button loading state did not complete within timeout")
    
    def get_button_info(self, identifier: str, identifier_type: str = 'data_attr') -> Optional[Dict]:
        """
        Get information about a button without clicking it
        
        Args:
            identifier: Value to identify the button
            identifier_type: Type of identifier ('data_attr', 'text', 'type')
            
        Returns:
            Dictionary with button information or None if not found
        """
        element = None
        
        if identifier_type == 'data_attr':
            element = self.locator.find_button_by_data_attr(identifier)
        elif identifier_type == 'text':
            element = self.locator.find_button_by_text(identifier)
        elif identifier_type == 'type':
            buttons = self.locator.find_button_by_type(identifier)
            if buttons:
                element = buttons[0]
        
        if element:
            return self.identifier.identify_button_type(element)
        
        return None
    
    def click_button_by_auto_detect(self, identifier: str, timeout: int = 10) -> bool:
        """
        Automatically detect and click button using multiple strategies
        This is the most generic method - tries all identification methods
        
        Args:
            identifier: Value to identify the button (can be data-attr-id, text, or type)
            timeout: Maximum wait time in seconds
            
        Returns:
            True if button was clicked successfully, False otherwise
        """
        return self.click_button(identifier, identifier_type='auto', timeout=timeout)
    
    # Delegate methods to ButtonLocator for backward compatibility
    def find_button_by_data_attr(self, data_attr_id: str, timeout: int = 10) -> Optional[WebElement]:
        """Delegate to ButtonLocator"""
        return self.locator.find_button_by_data_attr(data_attr_id, timeout, self.context)
    
    def find_button_by_text(self, text: str, exact_match: bool = False, timeout: int = 10) -> Optional[WebElement]:
        """Delegate to ButtonLocator"""
        return self.locator.find_button_by_text(text, exact_match, timeout, self.context)
    
    def find_button_by_type(self, button_type: str, timeout: int = 10) -> List[WebElement]:
        """Delegate to ButtonLocator"""
        return self.locator.find_button_by_type(button_type, timeout, self.context)
    
    def find_all_ant_buttons(self, timeout: int = 10) -> List[WebElement]:
        """Delegate to ButtonLocator"""
        return self.locator.find_all_ant_buttons(timeout)
    
    # Delegate method to ButtonIdentifier for backward compatibility
    def identify_button_type(self, element: WebElement) -> Dict[str, any]:
        """Delegate to ButtonIdentifier"""
        return self.identifier.identify_button_type(element)
