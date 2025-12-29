"""
Button Locator - Handles finding and locating buttons
Single Responsibility: Locate buttons by various criteria
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from typing import Optional, List
from framework.base.base_page import BasePage
from framework.context.element_context import ElementContext, ElementInfo
from framework.components.button_identifier import ButtonIdentifier
from framework.utils.pattern_discovery import PatternDiscovery


class ButtonLocator(BasePage):
    """
    Handles locating/finding Ant Design buttons on the page
    Single Responsibility: Find buttons by various identification methods
    Automatically discovers data-attr-id patterns from the page
    """
    
    # Ant Design button class patterns
    BUTTON_CLASSES = {
        'primary': 'ant-btn-primary',
        'default': 'ant-btn-default',
        'dashed': 'ant-btn-dashed',
        'text': 'ant-btn-text',
        'link': 'ant-btn-link',
        'danger': 'ant-btn-dangerous'
    }
    
    def __init__(self, driver: webdriver):
        """
        Initialize Button Locator
        
        Args:
            driver: Selenium WebDriver instance
        """
        super().__init__(driver)
        self.identifier = ButtonIdentifier()
        self.pattern_discovery = PatternDiscovery(driver)
    
    def find_button_by_data_attr(self, data_attr_id: str, timeout: int = 10, 
                                   context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find button by custom data-atr-id or data-attr-id attribute
        Automatically stores element in context if context is provided
        
        Args:
            data_attr_id: Value of data-atr-id or data-attr-id attribute
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            # Try data-atr-id first (original attribute name)
            element = self.find_element(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"]', timeout)
            if element and context:
                self._store_element_in_context(element, data_attr_id, context)
                return element
        except TimeoutException:
            pass
        
        # Try data-attr-id as fallback (alternative attribute name)
        try:
            element = self.find_element(By.CSS_SELECTOR, f'[data-attr-id="{data_attr_id}"]', timeout)
            if element and context:
                self._store_element_in_context(element, data_attr_id, context)
            return element
        except TimeoutException:
            return None
    
    def find_button_by_text(self, text: str, exact_match: bool = False, timeout: int = 10,
                             context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find button by its text content
        Automatically discovers data-attr-id patterns if text search fails
        Automatically stores element in context if context is provided
        
        Args:
            text: Text to search for
            exact_match: If True, match exact text; if False, partial match
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        element = None
        
        # Strategy 1: Try text-based search first
        try:
            if exact_match:
                xpath = f"//button[normalize-space(text())='{text}'] | //a[normalize-space(text())='{text}']"
            else:
                xpath = f"//button[contains(text(), '{text}')] | //a[contains(text(), '{text}')]"
            
            element = self.find_element(By.XPATH, xpath, timeout)
            if element and context:
                # Use text as key, or generate key from data-attr-id if available
                key = self._generate_context_key(element, text)
                self._store_element_in_context(element, key, context)
            if element:
                return element
        except TimeoutException:
            pass
        
        # Strategy 2: If text search failed, try pattern discovery
        try:
            # Normalize text for pattern matching (e.g., "Login" -> "login")
            normalized_text = text.lower().replace(' ', '-').replace('_', '-')
            
            # Try to find matching data-attr-id using pattern discovery
            matching_attr_id = self.pattern_discovery.find_matching_data_attr_id(normalized_text, 'button')
            if matching_attr_id:
                element = self.find_button_by_data_attr(matching_attr_id, timeout=3, context=context)
                if element:
                    print(f"   >> Found button using pattern discovery: {matching_attr_id}")
                    return element
            
            # Strategy 3: Generate candidates based on discovered pattern structure
            candidates = self.pattern_discovery.generate_candidates(normalized_text, 'button')
            for candidate in candidates:
                try:
                    element = self.find_button_by_data_attr(candidate, timeout=2, context=context)
                    if element:
                        print(f"   >> Found button using pattern candidate: {candidate}")
                        return element
                except:
                    continue
        except:
            pass
        
        return None
    
    def find_button_by_type(self, button_type: str, timeout: int = 10,
                             context: Optional[ElementContext] = None) -> List[WebElement]:
        """
        Find all buttons of a specific type
        Automatically stores first element in context if context is provided
        
        Args:
            button_type: Type of button ('primary', 'default', 'dashed', 'text', 'link', 'danger')
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            List of WebElements matching the type
        """
        try:
            button_class = self.BUTTON_CLASSES.get(button_type, 'ant-btn-default')
            elements = self.find_elements(By.CSS_SELECTOR, f'button.{button_class}, a.{button_class}', timeout)
            if elements and context:
                # Store first element
                key = self._generate_context_key(elements[0], f"{button_type}_button")
                self._store_element_in_context(elements[0], key, context)
            return elements
        except TimeoutException:
            return []
    
    def find_all_ant_buttons(self, timeout: int = 10) -> List[WebElement]:
        """
        Find all Ant Design buttons on the page
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            List of all Ant Design button WebElements
        """
        try:
            # Ant Design buttons have 'ant-btn' class
            return self.find_elements(By.CSS_SELECTOR, 'button.ant-btn, a.ant-btn', timeout)
        except TimeoutException:
            return []
    
    def _store_element_in_context(self, element: WebElement, key: str, context: ElementContext) -> None:
        """
        Store an element in the context after identifying it
        
        Args:
            element: WebElement to store
            key: Key to use for storing in context
            context: ElementContext to store the element
        """
        try:
            # Identify button properties
            button_info = self.identifier.identify_button_type(element)
            
            # Get data_attr_id from button_info or use key if it's a data-attr-id
            data_attr_id = button_info.get('data_attr_id')
            if not data_attr_id and key and not key.startswith(('primary_', 'default_', 'dashed_', 'text_', 'link_', 'danger_')):
                # If key looks like a data-attr-id, use it
                data_attr_id = key
            
            # Create ElementInfo
            element_info = ElementInfo(
                element=element,
                element_type='button',
                application_type=button_info.get('application_type'),
                data_attr_id=data_attr_id,
                metadata={
                    'button_type': button_info.get('type'),
                    'size': button_info.get('size'),
                    'disabled': button_info.get('disabled'),
                    'loading': button_info.get('loading'),
                    'text': button_info.get('text'),
                    'icon': button_info.get('icon'),
                    'shape': button_info.get('shape'),
                    **button_info.get('metadata', {})
                }
            )
            
            # Use data_attr_id as key if available, otherwise use provided key
            context_key = data_attr_id or key
            context.store_element(context_key, element_info)
        except Exception as e:
            print(f"Error storing element in context: {str(e)}")
    
    def _generate_context_key(self, element: WebElement, fallback: str) -> str:
        """
        Generate a context key for an element
        
        Args:
            element: WebElement to generate key for
            fallback: Fallback key if data-attr-id is not available
            
        Returns:
            Generated key string
        """
        try:
            # Try data-atr-id first
            data_attr_id = element.get_attribute('data-attr-id')
            if not data_attr_id:
                # Try data-attr-id as fallback
                data_attr_id = element.get_attribute('data-attr-id')
            if data_attr_id:
                return data_attr_id
            # Use fallback with element text or index
            text = element.text.strip()[:20] if element.text else fallback
            return f"{fallback}_{text}".replace(' ', '_').lower()
        except:
            return fallback


