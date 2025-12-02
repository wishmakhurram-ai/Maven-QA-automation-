"""
Pagination Locator - Handles finding and locating Ant Design Pagination components
Single Responsibility: Locate pagination by various criteria without hardcoded selectors
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from typing import Optional, List, Dict
from framework.base.base_page import BasePage
from framework.context.element_context import ElementContext, ElementInfo
from framework.components.pagination_identifier import PaginationIdentifier


class PaginationLocator(BasePage):
    """
    Handles locating/finding Ant Design Pagination components on the page
    Single Responsibility: Find pagination by various identification methods
    Uses Ant Design class patterns, data-attr-id, and semantic detection
    """
    
    def __init__(self, driver: webdriver):
        """
        Initialize Pagination Locator
        
        Args:
            driver: Selenium WebDriver instance
        """
        super().__init__(driver)
        self.identifier = PaginationIdentifier()
    
    def find_all_paginations(self, timeout: int = 10) -> List[WebElement]:
        """
        Find all Ant Design pagination components on the page
        Uses multiple strategies to detect pagination elements
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            List of pagination container WebElements
        """
        paginations = []
        
        # Strategy 1: Find by ant-pagination class
        try:
            elements = self.find_elements(By.CSS_SELECTOR, '.ant-pagination', timeout=3)
            paginations.extend(elements)
        except:
            pass
        
        # Strategy 2: Find by ul.ant-pagination
        try:
            elements = self.find_elements(By.CSS_SELECTOR, 'ul.ant-pagination', timeout=3)
            paginations.extend(elements)
        except:
            pass
        
        # Strategy 3: JavaScript-based detection for dynamic content
        try:
            js_paginations = self.execute_js("""
                var paginations = [];
                var elements = document.querySelectorAll('.ant-pagination, ul.ant-pagination, [class*="ant-pagination"]');
                for (var i = 0; i < elements.length; i++) {
                    var el = elements[i];
                    // Check if it has pagination-like structure
                    if (el.querySelector('.ant-pagination-item') || 
                        el.querySelector('.ant-pagination-prev') || 
                        el.querySelector('.ant-pagination-next')) {
                        paginations.push(el);
                    }
                }
                return paginations;
            """)
            if js_paginations:
                # Convert to WebElements (they're already WebElements from JS)
                for elem in js_paginations:
                    if elem not in paginations:
                        paginations.append(elem)
        except:
            pass
        
        # Deduplicate by location
        unique_paginations = []
        seen_locations = set()
        for pag in paginations:
            try:
                location = (pag.location['x'], pag.location['y'])
                if location not in seen_locations:
                    seen_locations.add(location)
                    unique_paginations.append(pag)
            except:
                # If we can't get location, add it anyway
                if pag not in unique_paginations:
                    unique_paginations.append(pag)
        
        return unique_paginations
    
    def find_pagination_by_data_attr(self, data_attr_id: str, timeout: int = 10,
                                     context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find pagination by custom data-atr-id attribute
        
        Args:
            data_attr_id: Value of data-atr-id attribute
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            # Try direct match
            element = self.find_element(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"].ant-pagination', timeout)
            if not element:
                # Try parent container
                element = self.find_element(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"] .ant-pagination', timeout)
            if not element:
                # Try any element with data-atr-id that contains pagination
                candidates = self.find_elements(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"]', timeout)
                for candidate in candidates:
                    class_attr = candidate.get_attribute('class') or ''
                    if 'ant-pagination' in class_attr:
                        element = candidate
                        break
                    # Check if candidate contains pagination
                    try:
                        pag_elem = candidate.find_element(By.CSS_SELECTOR, '.ant-pagination')
                        element = pag_elem
                        break
                    except:
                        pass
            
            if element and context:
                self._store_element_in_context(element, data_attr_id, context)
            return element
        except TimeoutException:
            return None
    
    def find_pagination_by_position(self, position: int, timeout: int = 10,
                                    context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find pagination by position/index (1-based)
        
        Args:
            position: Position number (1 = first pagination, 2 = second, etc.)
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            paginations = self.find_all_paginations(timeout)
            if paginations and 1 <= position <= len(paginations):
                element = paginations[position - 1]
                if context:
                    self._store_element_in_context(element, str(position), context)
                return element
            return None
        except Exception:
            return None
    
    def find_pagination_with_features(self, has_size_changer: bool = False, 
                                     has_jump_to: bool = False,
                                     has_next_prev: bool = True,
                                     timeout: int = 10,
                                     context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find a pagination that has specific features
        Handles stale elements by re-finding paginations
        
        Args:
            has_size_changer: Require page size changer
            has_jump_to: Require jump-to input
            has_next_prev: Require next/prev buttons (default True)
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                paginations = self.find_all_paginations(timeout)
                for idx, pag in enumerate(paginations):
                    try:
                        # Re-find pagination if stale
                        try:
                            _ = pag.location
                        except:
                            # Re-find by position
                            paginations = self.find_all_paginations(timeout)
                            if idx < len(paginations):
                                pag = paginations[idx]
                            else:
                                continue
                        
                        info = self.identifier.identify_pagination(pag)
                        
                        # Check requirements
                        if has_size_changer and not info.get('has_page_size_changer', False):
                            continue
                        if has_jump_to and not info.get('has_jump_to', False):
                            continue
                        if has_next_prev:
                            if not info.get('next_enabled', False) and not info.get('prev_enabled', False):
                                # Check if buttons exist even if disabled
                                try:
                                    page_elements = self.identifier.get_page_elements(pag)
                                    if not page_elements.get('next_button') and not page_elements.get('prev_button'):
                                        continue
                                except:
                                    # If we can't get page elements, assume buttons exist if pagination exists
                                    pass
                        
                        # Found a matching pagination
                        if context:
                            self._store_element_in_context(pag, 'feature_match', context)
                        return pag
                    except Exception as e:
                        # Skip this pagination if we can't identify it
                        if 'stale' not in str(e).lower():
                            print(f"   >> Warning: Error identifying pagination {idx+1}: {str(e)}")
                        continue
                
                return None
            except Exception as e:
                if attempt < max_attempts - 1:
                    import time
                    time.sleep(0.5)
                    continue
                return None
        
        return None
    
    def _store_element_in_context(self, element: WebElement, key: str, context: ElementContext) -> None:
        """
        Store an element in the context after identifying it
        
        Args:
            element: WebElement to store
            key: Key to use for storing in context
            context: ElementContext to store the element
        """
        try:
            # Identify pagination properties
            pagination_info = self.identifier.identify_pagination(element)
            
            # Get data_attr_id from pagination_info or use key if it's a data-attr-id
            data_attr_id = pagination_info.get('data_attr_id')
            if not data_attr_id and key and not key.isdigit():
                data_attr_id = key
            
            # Create ElementInfo
            element_info = ElementInfo(
                element=element,
                element_type='pagination',
                application_type=pagination_info.get('type', 'pagination'),
                data_attr_id=data_attr_id,
                metadata=pagination_info
            )
            
            context.store_element(key, element_info)
            print(f"   >> Stored pagination in context with key: '{key}'")
            print(f"      Element type: pagination, Application type: {pagination_info.get('type', 'N/A')}, "
                  f"Data-attr-id: {data_attr_id}")
        except Exception as e:
            print(f"   >> Warning: Could not store pagination in context: {str(e)}")
    
    def _create_element_info(self, element: WebElement, key: str, pagination_info: Optional[Dict] = None) -> ElementInfo:
        """
        Create ElementInfo for a pagination element
        
        Args:
            element: WebElement to create info for
            key: Key to use for storing in context
            pagination_info: Optional pre-identified pagination info
            
        Returns:
            ElementInfo object
        """
        if pagination_info is None:
            pagination_info = self.identifier.identify_pagination(element)
        
        data_attr_id = pagination_info.get('data_attr_id')
        if not data_attr_id and key and not key.isdigit():
            data_attr_id = key
        
        return ElementInfo(
            element=element,
            element_type='pagination',
            application_type=pagination_info.get('type', 'pagination'),
            data_attr_id=data_attr_id,
            metadata=pagination_info
        )

