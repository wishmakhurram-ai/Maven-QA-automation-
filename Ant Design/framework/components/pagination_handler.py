"""
Generic Ant Design Pagination Handler
Handles pagination interactions (navigate pages, change page size, jump to page, etc.)
Uses PaginationLocator for finding paginations and PaginationIdentifier for analyzing them
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
from framework.components.pagination_locator import PaginationLocator
from framework.components.pagination_identifier import PaginationIdentifier
from framework.context.element_context import ElementContext, ElementInfo
import time
import re


class PaginationHandler(BasePage):
    """
    Generic handler for Ant Design Pagination interactions
    Single Responsibility: Handle pagination interactions (navigation, page size, jump-to, etc.)
    Uses PaginationLocator to find paginations and PaginationIdentifier to analyze them
    """
    
    def __init__(self, driver: webdriver, context: Optional[ElementContext] = None):
        """
        Initialize Pagination Handler
        
        Args:
            driver: Selenium WebDriver instance
            context: Optional ElementContext for context-driven interactions
        """
        super().__init__(driver)
        self.locator = PaginationLocator(driver)
        self.identifier = PaginationIdentifier()
        self.context = context
    
    def identify_and_store(self, identifier: str, identifier_type: str = 'data_attr_id',
                          timeout: int = 10, context_key: Optional[str] = None) -> bool:
        """
        Identify a pagination and store it in context
        
        Args:
            identifier: Value to identify the pagination (data-attr-id, position, or 'with_features')
            identifier_type: Type of identifier ('data_attr_id', 'position', 'features')
            timeout: Maximum wait time in seconds
            context_key: Optional key to use in context
            
        Returns:
            True if pagination was identified and stored, False otherwise
        """
        if not self.context:
            print("Context not available. Cannot store element.")
            return False
        
        element = None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_pagination_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                element = self.locator.find_pagination_by_position(position, timeout=timeout, context=self.context)
            elif identifier_type == 'features':
                # Parse features from identifier string like "size_changer", "jump_to", or "all"
                identifier_lower = identifier.lower()
                has_size_changer = 'size_changer' in identifier_lower or identifier_lower == 'all'
                has_jump_to = 'jump_to' in identifier_lower or identifier_lower == 'all'
                element = self.locator.find_pagination_with_features(
                    has_size_changer=has_size_changer,
                    has_jump_to=has_jump_to,
                    timeout=timeout,
                    context=self.context
                )
            
            if element:
                if context_key and context_key != identifier:
                    element_info = self.context.get_element(identifier) or self.context.get_current()
                    if element_info:
                        self.context.store_element(context_key, element_info)
                print(f"Pagination identified and stored in context: {identifier}")
                return True
            else:
                print(f"Pagination not found with identifier: {identifier} (type: {identifier_type})")
                return False
                
        except Exception as e:
            print(f"Error identifying pagination: {str(e)}")
            return False
    
    def go_to_page(self, page_number: int, identifier: Optional[str] = None,
                   identifier_type: str = 'data_attr_id', timeout: int = 10,
                   use_context: bool = False) -> bool:
        """
        Navigate to a specific page number
        
        Args:
            page_number: Page number to navigate to
            identifier: Optional identifier for pagination (if None, uses first pagination)
            identifier_type: Type of identifier ('data_attr_id', 'position')
            timeout: Maximum wait time in seconds
            use_context: If True, tries to use context first
            
        Returns:
            True if navigation was successful, False otherwise
        """
        pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
        if not pagination_element:
            return False
        
        try:
            # Get page elements
            page_elements = self.identifier.get_page_elements(pagination_element)
            
            # Check if simple mode (only prev/next)
            pagination_info = self.identifier.identify_pagination(pagination_element)
            if pagination_info.get('simple_mode', False):
                # For simple mode, use jump-to if available, otherwise can't go to specific page
                if pagination_info.get('has_jump_to', False) and page_elements.get('jump_input'):
                    return self._jump_to_page_via_input(pagination_element, page_number, page_elements['jump_input'])
                else:
                    print("Simple mode pagination - cannot navigate to specific page number")
                    return False
            
            # Get current page and total pages for reference
            current_page = pagination_info.get('current_page', 1)
            total_pages = pagination_info.get('total_pages')
            
            # If already on target page, return success
            if current_page == page_number:
                print(f"Already on page {page_number}")
                return True
            
            # Strategy 1: Try to find and click the page number directly (if visible)
            try:
                page_items = page_elements.get('page_items', [])
                
                for item in page_items:
                    try:
                        text = item.text.strip()
                        if text.isdigit() and int(text) == page_number:
                            # Scroll into view
                            self.execute_js("arguments[0].scrollIntoView({block: 'center'});", item)
                            time.sleep(0.3)
                            
                            # Click the page using multiple methods
                            try:
                                item.click()
                            except:
                                try:
                                    self.execute_js("arguments[0].click();", item)
                                except:
                                    # Try ActionChains as fallback
                                    from selenium.webdriver.common.action_chains import ActionChains
                                    ActionChains(self.driver).move_to_element(item).click().perform()
                            
                            # Wait for page to change
                            time.sleep(1.5)
                            
                            # Verify navigation
                            updated_info = self.identifier.identify_pagination(pagination_element)
                            if updated_info.get('current_page') == page_number:
                                print(f"Successfully navigated to page {page_number}")
                                return True
                    except Exception as e:
                        continue
                
                print(f"Page {page_number} not found in visible page items")
            except Exception as e:
                print(f"Could not find page {page_number} in visible pages: {str(e)}")
            
            # Strategy 2: If page not visible, try jump-to input (preferred for large jumps)
            if pagination_info.get('has_jump_to', False) and page_elements.get('jump_input'):
                print(f"Page {page_number} not visible, using jump-to input...")
                return self._jump_to_page_via_input(pagination_element, page_number, page_elements['jump_input'])
            
            # Strategy 3: If no jump-to and page is close, use next/prev buttons
            if current_page and abs(page_number - current_page) <= 5:
                print(f"Navigating from page {current_page} to page {page_number} using next/prev buttons...")
                steps = page_number - current_page
                if steps > 0:
                    for i in range(steps):
                        if not self.next_page(identifier=identifier, identifier_type=identifier_type, timeout=timeout, use_context=use_context):
                            return False
                        time.sleep(0.5)
                else:
                    for i in range(abs(steps)):
                        if not self.previous_page(identifier=identifier, identifier_type=identifier_type, timeout=timeout, use_context=use_context):
                            return False
                        time.sleep(0.5)
                
                # Verify navigation
                time.sleep(1)
                updated_info = self.identifier.identify_pagination(pagination_element)
                if updated_info.get('current_page') == page_number:
                    print(f"Successfully navigated to page {page_number} via next/prev buttons")
                    return True
                else:
                    print(f"Navigation may have failed - expected page {page_number}, but on page {updated_info.get('current_page')}")
                    return False
            
            # Strategy 4: For large jumps without jump-to, try to click last visible page then navigate
            if total_pages and page_number > current_page:
                # Try clicking the last visible page number to get closer
                try:
                    page_items = page_elements.get('page_items', [])
                    visible_pages = []
                    for item in page_items:
                        try:
                            text = item.text.strip()
                            if text.isdigit():
                                visible_pages.append(int(text))
                        except:
                            continue
                    
                    if visible_pages:
                        last_visible = max(visible_pages)
                        if last_visible < page_number:
                            # Click last visible page to get closer
                            print(f"Clicking page {last_visible} to get closer to target page {page_number}...")
                            self.go_to_page(last_visible, identifier=identifier, identifier_type=identifier_type, timeout=timeout, use_context=use_context)
                            time.sleep(1)
                            # Try again recursively (with limit to prevent infinite loop)
                            if abs(page_number - last_visible) <= 10:
                                return self.go_to_page(page_number, identifier=identifier, identifier_type=identifier_type, timeout=timeout, use_context=use_context)
                except Exception as e:
                    print(f"Error in Strategy 4: {str(e)}")
                    pass
            
            print(f"Could not navigate to page {page_number} (current: {current_page}, total: {total_pages})")
            return False
            
        except Exception as e:
            print(f"Error navigating to page {page_number}: {str(e)}")
            return False
    
    def next_page(self, identifier: Optional[str] = None, identifier_type: str = 'data_attr_id',
                  timeout: int = 10, use_context: bool = False) -> bool:
        """
        Navigate to the next page
        
        Args:
            identifier: Optional identifier for pagination
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            use_context: If True, tries to use context first
            
        Returns:
            True if navigation was successful, False otherwise
        """
        pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
        if not pagination_element:
            return False
        
        try:
            # Re-find pagination element to avoid stale reference
            pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
            if not pagination_element:
                print("Pagination element not found")
                return False
            
            page_elements = self.identifier.get_page_elements(pagination_element)
            next_button = page_elements.get('next_button')
            
            if not next_button:
                # Try to find next button directly
                try:
                    next_button = pagination_element.find_element(By.CSS_SELECTOR, '.ant-pagination-next')
                except:
                    print("Next button not found")
                    return False
            
            # Check if enabled
            pagination_info = self.identifier.identify_pagination(pagination_element)
            if not pagination_info.get('next_enabled', False):
                print("Next button is disabled")
                return False
            
            # Scroll into view and click
            self.execute_js("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(0.3)
            
            try:
                next_button.click()
            except Exception as e:
                if 'stale' in str(e).lower():
                    # Re-find next button
                    next_button = pagination_element.find_element(By.CSS_SELECTOR, '.ant-pagination-next')
                    self.execute_js("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(0.3)
                    next_button.click()
                else:
                    self.execute_js("arguments[0].click();", next_button)
            
            time.sleep(1)
            print("Successfully navigated to next page")
            return True
            
        except Exception as e:
            print(f"Error navigating to next page: {str(e)}")
            return False
    
    def previous_page(self, identifier: Optional[str] = None, identifier_type: str = 'data_attr_id',
                      timeout: int = 10, use_context: bool = False) -> bool:
        """
        Navigate to the previous page
        
        Args:
            identifier: Optional identifier for pagination
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            use_context: If True, tries to use context first
            
        Returns:
            True if navigation was successful, False otherwise
        """
        pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
        if not pagination_element:
            return False
        
        try:
            # Re-find pagination element to avoid stale reference
            pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
            if not pagination_element:
                print("Pagination element not found")
                return False
            
            page_elements = self.identifier.get_page_elements(pagination_element)
            prev_button = page_elements.get('prev_button')
            
            if not prev_button:
                # Try to find prev button directly
                try:
                    prev_button = pagination_element.find_element(By.CSS_SELECTOR, '.ant-pagination-prev')
                except:
                    print("Previous button not found")
                    return False
            
            # Check if enabled
            pagination_info = self.identifier.identify_pagination(pagination_element)
            if not pagination_info.get('prev_enabled', False):
                print("Previous button is disabled")
                return False
            
            # Scroll into view and click
            self.execute_js("arguments[0].scrollIntoView({block: 'center'});", prev_button)
            time.sleep(0.3)
            
            try:
                prev_button.click()
            except Exception as e:
                if 'stale' in str(e).lower():
                    # Re-find prev button
                    prev_button = pagination_element.find_element(By.CSS_SELECTOR, '.ant-pagination-prev')
                    self.execute_js("arguments[0].scrollIntoView({block: 'center'});", prev_button)
                    time.sleep(0.3)
                    prev_button.click()
                else:
                    self.execute_js("arguments[0].click();", prev_button)
            
            time.sleep(1)
            print("Successfully navigated to previous page")
            return True
            
        except Exception as e:
            print(f"Error navigating to previous page: {str(e)}")
            return False
    
    def select_page_size(self, page_size: int, identifier: Optional[str] = None,
                        identifier_type: str = 'data_attr_id', timeout: int = 10,
                        use_context: bool = False) -> bool:
        """
        Change the page size (items per page)
        
        Args:
            page_size: New page size (e.g., 10, 20, 50, 100)
            identifier: Optional identifier for pagination
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            use_context: If True, tries to use context first
            
        Returns:
            True if page size was changed successfully, False otherwise
        """
        pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
        if not pagination_element:
            return False
        
        try:
            # Re-find pagination element to avoid stale reference
            pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
            if not pagination_element:
                print("Pagination element not found")
                return False
            
            page_elements = self.identifier.get_page_elements(pagination_element)
            size_changer = page_elements.get('size_changer')
            
            if not size_changer:
                # Try to find size changer directly
                try:
                    size_changer = pagination_element.find_element(By.CSS_SELECTOR, '.ant-pagination-options-size-changer')
                except:
                    try:
                        size_changer = pagination_element.find_element(By.CSS_SELECTOR, '.ant-pagination-options .ant-select')
                    except:
                        print("Page size changer not found")
                        return False
            
            # Click to open dropdown
            self.execute_js("arguments[0].scrollIntoView({block: 'center'});", size_changer)
            time.sleep(0.3)
            
            try:
                size_changer.click()
            except:
                self.execute_js("arguments[0].click();", size_changer)
            
            time.sleep(0.5)
            
            # Find and click the option
            try:
                # Wait for dropdown to appear and be visible
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-select-dropdown'))
                )
                time.sleep(0.3)  # Additional wait for dropdown animation
                
                # Wait for options to be visible
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-select-item-option'))
                )
                
                # Find option with matching page size
                # Try multiple selectors as Ant Design might use different structures
                option_selectors = [
                    '.ant-select-item-option',
                    '.ant-select-dropdown .ant-select-item-option',
                    'li.ant-select-item-option',
                    '[role="option"]'
                ]
                
                options = []
                for selector in option_selectors:
                    try:
                        options = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if options:
                            break
                    except:
                        continue
                
                if not options:
                    print(f"No options found in dropdown")
                    return False
                
                print(f"Found {len(options)} options in dropdown")
                
                # Try to find and click the matching option
                for option in options:
                    try:
                        # Scroll option into view
                        self.execute_js("arguments[0].scrollIntoView({block: 'center'});", option)
                        time.sleep(0.2)
                        
                        text = option.text.strip()
                        print(f"  Checking option: '{text}'")
                        
                        # Extract number from text like "10 / page", "10", "10条/页", etc.
                        match = re.search(r'(\d+)', text)
                        if match:
                            option_size = int(match.group(1))
                            if option_size == page_size:
                                # Try multiple click methods
                                clicked = False
                                try:
                                    # Method 1: Direct click
                                    option.click()
                                    print(f"  Clicked option via direct click")
                                    clicked = True
                                except:
                                    try:
                                        # Method 2: JavaScript click
                                        self.execute_js("arguments[0].click();", option)
                                        print(f"  Clicked option via JavaScript")
                                        clicked = True
                                    except:
                                        # Method 3: Mouse event
                                        self.execute_js("""
                                            var event = new MouseEvent('click', {
                                                view: window,
                                                bubbles: true,
                                                cancelable: true
                                            });
                                            arguments[0].dispatchEvent(event);
                                        """, option)
                                        print(f"  Clicked option via MouseEvent")
                                        clicked = True
                                
                                if clicked:
                                    time.sleep(2.0)  # Wait for selection to take effect and dropdown to close
                                    
                                    # Verify selection was successful by checking current page size
                                    try:
                                        # Re-find pagination to get updated state
                                        pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
                                        if pagination_element:
                                            updated_info = self.identifier.identify_pagination(pagination_element)
                                            current_size = updated_info.get('page_size')
                                            if current_size == page_size:
                                                print(f"Successfully changed page size to {page_size}")
                                                return True
                                            else:
                                                # Sometimes the page size might not update immediately, wait a bit more
                                                time.sleep(1.0)
                                                updated_info = self.identifier.identify_pagination(pagination_element)
                                                current_size = updated_info.get('page_size')
                                                if current_size == page_size:
                                                    print(f"Successfully changed page size to {page_size} (after retry)")
                                                    return True
                                                else:
                                                    print(f"Page size changed but verification failed: expected {page_size}, got {current_size}")
                                        else:
                                            # If we can't verify, assume success after click
                                            print(f"Successfully changed page size to {page_size} (verification skipped)")
                                            return True
                                    except Exception as e:
                                        # If we can't verify, assume success after successful click
                                        print(f"Successfully changed page size to {page_size} (verification error: {str(e)})")
                                        return True
                                break  # Exit loop after clicking
                    except Exception as e:
                        print(f"  Error checking option: {str(e)}")
                        continue
                
                print(f"Page size option {page_size} not found in dropdown")
                print(f"Available options: {[opt.text.strip() for opt in options[:5]]}")
                return False
                
            except Exception as e:
                print(f"Error selecting page size: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
            
        except Exception as e:
            print(f"Error changing page size: {str(e)}")
            return False
    
    def jump_to_page(self, page_number: int, identifier: Optional[str] = None,
                    identifier_type: str = 'data_attr_id', timeout: int = 10,
                    use_context: bool = False) -> bool:
        """
        Jump to a specific page using the jump-to input field
        
        Args:
            page_number: Page number to jump to
            identifier: Optional identifier for pagination
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            use_context: If True, tries to use context first
            
        Returns:
            True if jump was successful, False otherwise
        """
        pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
        if not pagination_element:
            return False
        
        try:
            # Re-find pagination element to avoid stale reference
            pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
            if not pagination_element:
                print("Pagination element not found")
                return False
            
            page_elements = self.identifier.get_page_elements(pagination_element)
            jump_input = page_elements.get('jump_input')
            
            if not jump_input:
                # Try to find jump input directly
                try:
                    jump_input = pagination_element.find_element(By.CSS_SELECTOR, '.ant-pagination-options-quick-jumper input')
                except:
                    try:
                        jump_input = pagination_element.find_element(By.CSS_SELECTOR, 'input[placeholder*="跳转" i], input[placeholder*="Go to" i], input[placeholder*="jump" i]')
                    except:
                        print("Jump-to input not found")
                        return False
            
            return self._jump_to_page_via_input(pagination_element, page_number, jump_input)
            
        except Exception as e:
            print(f"Error jumping to page: {str(e)}")
            return False
    
    def _jump_to_page_via_input(self, pagination_element: WebElement, page_number: int,
                                jump_input: WebElement) -> bool:
        """
        Helper method to jump to page via input field
        
        Args:
            pagination_element: Pagination container element
            page_number: Page number to jump to
            jump_input: Input field element
            
        Returns:
            True if jump was successful, False otherwise
        """
        try:
            # Scroll into view
            self.execute_js("arguments[0].scrollIntoView({block: 'center'});", jump_input)
            time.sleep(0.3)
            
            # Clear and enter page number
            jump_input.clear()
            jump_input.send_keys(str(page_number))
            time.sleep(0.3)
            
            # Try to submit (Enter key or find Go button)
            page_elements = self.identifier.get_page_elements(pagination_element)
            go_button = page_elements.get('go_button')
            
            if go_button:
                try:
                    go_button.click()
                except:
                    self.execute_js("arguments[0].click();", go_button)
            else:
                # Press Enter
                jump_input.send_keys(Keys.RETURN)
            
            time.sleep(1)
            print(f"Successfully jumped to page {page_number}")
            return True
            
        except Exception as e:
            print(f"Error jumping to page via input: {str(e)}")
            return False
    
    def get_current_page(self, identifier: Optional[str] = None,
                        identifier_type: str = 'data_attr_id', timeout: int = 10,
                        use_context: bool = False) -> Optional[int]:
        """
        Get the current active page number
        
        Args:
            identifier: Optional identifier for pagination
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            use_context: If True, tries to use context first
            
        Returns:
            Current page number if found, None otherwise
        """
        pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
        if not pagination_element:
            return None
        
        try:
            pagination_info = self.identifier.identify_pagination(pagination_element)
            return pagination_info.get('current_page')
        except:
            return None
    
    def get_total_pages(self, identifier: Optional[str] = None,
                       identifier_type: str = 'data_attr_id', timeout: int = 10,
                       use_context: bool = False) -> Optional[int]:
        """
        Get the total number of pages
        
        Args:
            identifier: Optional identifier for pagination
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            use_context: If True, tries to use context first
            
        Returns:
            Total pages if found, None otherwise
        """
        pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
        if not pagination_element:
            return None
        
        try:
            pagination_info = self.identifier.identify_pagination(pagination_element)
            return pagination_info.get('total_pages')
        except:
            return None
    
    def get_current_page_size(self, identifier: Optional[str] = None,
                             identifier_type: str = 'data_attr_id', timeout: int = 10,
                             use_context: bool = False) -> Optional[int]:
        """
        Get the current page size (items per page)
        
        Args:
            identifier: Optional identifier for pagination
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            use_context: If True, tries to use context first
            
        Returns:
            Current page size if found, None otherwise
        """
        pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
        if not pagination_element:
            return None
        
        try:
            pagination_info = self.identifier.identify_pagination(pagination_element)
            return pagination_info.get('page_size')
        except:
            return None
    
    def get_available_page_sizes(self, identifier: Optional[str] = None,
                                identifier_type: str = 'data_attr_id', timeout: int = 10,
                                use_context: bool = False) -> List[int]:
        """
        Get list of available page sizes
        
        Args:
            identifier: Optional identifier for pagination
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            use_context: If True, tries to use context first
            
        Returns:
            List of available page sizes
        """
        pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
        if not pagination_element:
            return []
        
        try:
            pagination_info = self.identifier.identify_pagination(pagination_element)
            return pagination_info.get('available_page_sizes', [])
        except:
            return []
    
    def print_pagination_summary(self, identifier: Optional[str] = None,
                                 identifier_type: str = 'data_attr_id', timeout: int = 10,
                                 use_context: bool = False) -> None:
        """
        Print a readable summary of pagination state
        
        Args:
            identifier: Optional identifier for pagination
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            use_context: If True, tries to use context first
        """
        pagination_element = self._get_pagination_element(identifier, identifier_type, timeout, use_context)
        if not pagination_element:
            print("Pagination not found")
            return
        
        try:
            pagination_info = self.identifier.identify_pagination(pagination_element)
            
            print("\n" + "="*70)
            print("PAGINATION SUMMARY")
            print("="*70)
            print(f"Current page: {pagination_info.get('current_page', 'N/A')}")
            print(f"Total pages: {pagination_info.get('total_pages', 'N/A')}")
            if pagination_info.get('total_items'):
                print(f"Total items: {pagination_info.get('total_items')}")
            print(f"Page sizes: {pagination_info.get('available_page_sizes', [])}")
            print(f"Active size: {pagination_info.get('page_size', 'N/A')}")
            print(f"Next enabled: {pagination_info.get('next_enabled', False)}")
            print(f"Prev enabled: {pagination_info.get('prev_enabled', False)}")
            print(f"Has jump-to: {pagination_info.get('has_jump_to', False)}")
            print(f"Has page size changer: {pagination_info.get('has_page_size_changer', False)}")
            print(f"Style: {pagination_info.get('style', 'default')}")
            print(f"Simple mode: {pagination_info.get('simple_mode', False)}")
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"Error printing pagination summary: {str(e)}")
    
    def _get_pagination_element(self, identifier: Optional[str], identifier_type: str,
                                timeout: int, use_context: bool) -> Optional[WebElement]:
        """
        Helper method to get pagination element from various sources
        Handles stale elements by re-finding them
        
        Args:
            identifier: Optional identifier
            identifier_type: Type of identifier
            timeout: Maximum wait time
            use_context: Whether to use context
            
        Returns:
            Pagination WebElement if found, None otherwise
        """
        # Try context first if enabled
        if use_context and self.context:
            if identifier:
                element_info = self.context.get_element(identifier)
            else:
                element_info = self.context.get_current()
            
            if element_info:
                element = element_info.element
                # Check if element is stale and re-find if needed
                try:
                    # Try to access element to check if stale
                    _ = element.is_displayed()
                    return element
                except Exception:
                    # Element is stale, re-find it
                    print(f"   >> Element in context is stale, re-finding...")
                    if identifier_type == 'position':
                        position = int(identifier) if identifier and identifier.isdigit() else 1
                        fresh_element = self.locator.find_pagination_by_position(position, timeout)
                    elif identifier_type == 'data_attr_id' and identifier:
                        fresh_element = self.locator.find_pagination_by_data_attr(identifier, timeout)
                    else:
                        # Try to get from metadata
                        data_attr_id = element_info.metadata.get('data_attr_id') if element_info.metadata else None
                        if data_attr_id:
                            fresh_element = self.locator.find_pagination_by_data_attr(data_attr_id, timeout)
                        else:
                            fresh_element = None
                    
                    if fresh_element:
                        # Update context with fresh element
                        if identifier:
                            element_info.element = fresh_element
                            self.context.store_element(identifier, element_info)
                        else:
                            element_info.element = fresh_element
                            self.context.set_current(element_info)
                        return fresh_element
        
        # Try to find by identifier
        if identifier:
            if identifier_type == 'data_attr_id':
                return self.locator.find_pagination_by_data_attr(identifier, timeout)
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                return self.locator.find_pagination_by_position(position, timeout)
        
        # Fallback: get first pagination
        paginations = self.locator.find_all_paginations(timeout)
        if paginations:
            return paginations[0]
        
        return None

