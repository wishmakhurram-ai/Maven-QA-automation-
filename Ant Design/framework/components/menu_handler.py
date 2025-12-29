"""
Generic Ant Design Menu Handler
Handles menu interactions (clicking, expanding, navigating, etc.)
Uses MenuLocator for finding menus and MenuIdentifier for analyzing them
Uses ElementContext for context-driven interactions
"""
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, StaleElementReferenceException
from typing import Optional, Dict, List
from framework.base.base_page import BasePage
from framework.components.menu_locator import MenuLocator
from framework.components.menu_identifier import MenuIdentifier
from framework.context.element_context import ElementContext, ElementInfo
import time


class MenuHandler(BasePage):
    """
    Generic handler for Ant Design menu interactions
    Single Responsibility: Handle menu interactions (clicking, expanding, navigating, etc.)
    Uses MenuLocator to find menus and MenuIdentifier to analyze them
    """
    
    def __init__(self, driver: webdriver, context: Optional[ElementContext] = None):
        """
        Initialize Menu Handler
        
        Args:
            driver: Selenium WebDriver instance
            context: Optional ElementContext for context-driven interactions
        """
        super().__init__(driver)
        self.locator = MenuLocator(driver)
        self.identifier = MenuIdentifier()
        self.context = context
    
    def click_menu_item(self, menu_text: str, parent_menu: Optional[WebElement] = None,
                       timeout: int = 15, auto_expand: bool = True) -> bool:
        """
        Click a menu item by text
        
        Args:
            menu_text: Text of menu item to click
            parent_menu: Optional parent menu element to search within
            timeout: Maximum wait time in seconds
            auto_expand: If True, automatically expands parent submenus if needed
            
        Returns:
            True if menu item was clicked successfully, False otherwise
        """
        try:
            # Find the menu item
            item = self.locator.find_menu_item_by_text(menu_text, timeout=timeout, 
                                                      context=self.context, parent_menu=parent_menu)
            
            if not item:
                print(f"Menu item '{menu_text}' not found")
                return False
            
            # Check if it's disabled
            if not self.identifier.is_item_clickable(item):
                print(f"Menu item '{menu_text}' is disabled")
                return False
            
            # If auto_expand is enabled, expand parent submenus if needed
            if auto_expand:
                self._expand_parent_submenus(item, timeout)
            
            # Scroll into view
            self.execute_js("arguments[0].scrollIntoView({block: 'center'});", item)
            time.sleep(0.5)
            
            # Store URL before clicking to detect navigation
            url_before = self.driver.current_url
            
            # Click the item
            clicked = False
            try:
                item.click()
                clicked = True
                print(f"Clicked menu item '{menu_text}'")
            except ElementNotInteractableException:
                # Try JavaScript click
                try:
                    self.execute_js("arguments[0].click();", item)
                    clicked = True
                    print(f"Clicked menu item '{menu_text}' (via JavaScript)")
                except:
                    # Try ActionChains
                    try:
                        actions = ActionChains(self.driver)
                        actions.move_to_element(item).click().perform()
                        clicked = True
                        print(f"Clicked menu item '{menu_text}' (via ActionChains)")
                    except:
                        print(f"Failed to click menu item '{menu_text}'")
                        return False
            
            if clicked:
                # Wait a bit for navigation to start
                time.sleep(0.5)
                
                # If URL changed, wait for navigation to complete
                try:
                    wait = WebDriverWait(self.driver, 10)
                    # Wait until URL changes or page loads
                    wait.until(
                        lambda driver: driver.current_url != url_before or 
                        driver.execute_script('return document.readyState') == 'complete'
                    )
                    # Additional wait for dynamic content
                    time.sleep(1)
                except TimeoutException:
                    # Navigation might not have happened (e.g., submenu expansion)
                    pass
                
                return True
            
            return False
        except Exception as e:
            print(f"Error clicking menu item: {str(e)}")
            return False
    
    def click_submenu_item(self, submenu_text: str, item_text: str,
                          parent_menu: Optional[WebElement] = None,
                          timeout: int = 15) -> bool:
        """
        Click an item inside a submenu
        
        Args:
            submenu_text: Text of the submenu to open
            item_text: Text of the item inside the submenu to click
            parent_menu: Optional parent menu element to search within
            timeout: Maximum wait time in seconds
            
        Returns:
            True if item was clicked successfully, False otherwise
        """
        try:
            # Step 1: Find and expand the submenu
            submenu_opened = self.expand_submenu(submenu_text, parent_menu, timeout)
            if not submenu_opened:
                print(f"Failed to open submenu '{submenu_text}'")
                return False
            
            # Step 2: Find the item within the submenu
            # Wait a bit for submenu to render
            time.sleep(1.0)
            
            # Find the submenu element
            submenu_element = self.locator.find_menu_item_by_text(submenu_text, timeout=timeout,
                                                                  parent_menu=parent_menu)
            
            if not submenu_element:
                print(f"Submenu '{submenu_text}' not found")
                return False
            
            # Find parent submenu container
            try:
                submenu_container = submenu_element.find_element(By.XPATH, 
                    './ancestor::li[contains(@class, "ant-menu-submenu")]')
            except:
                print(f"Could not find submenu container for '{submenu_text}'")
                return False
            
            # Step 3: Find and click the item within the submenu
            submenu_items = self.locator.find_submenu_items(submenu_container)
            
            for sub_item in submenu_items:
                try:
                    item_info = self.identifier.identify_menu_item(sub_item)
                    if item_text.lower() in item_info.get('text', '').lower() or \
                       item_info.get('text', '').lower() in item_text.lower():
                        # Found the item, click it
                        if not self.identifier.is_item_clickable(sub_item):
                            print(f"Menu item '{item_text}' is disabled")
                            continue
                        
                        self.execute_js("arguments[0].scrollIntoView({block: 'center'});", sub_item)
                        time.sleep(0.3)
                        
                        try:
                            sub_item.click()
                            time.sleep(0.5)
                            print(f"Clicked '{item_text}' inside submenu '{submenu_text}'")
                            return True
                        except:
                            self.execute_js("arguments[0].click();", sub_item)
                            time.sleep(0.5)
                            print(f"Clicked '{item_text}' inside submenu '{submenu_text}' (via JavaScript)")
                            return True
                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue
            
            print(f"Item '{item_text}' not found in submenu '{submenu_text}'")
            return False
        except Exception as e:
            print(f"Error clicking submenu item: {str(e)}")
            return False
    
    def expand_submenu(self, submenu_text: str, parent_menu: Optional[WebElement] = None,
                      timeout: int = 15) -> bool:
        """
        Expand a submenu by text
        
        Args:
            submenu_text: Text of submenu to expand
            parent_menu: Optional parent menu element to search within
            timeout: Maximum wait time in seconds
            
        Returns:
            True if submenu was expanded successfully, False otherwise
        """
        try:
            # Find the submenu
            submenu_item = self.locator.find_menu_item_by_text(submenu_text, timeout=timeout,
                                                              parent_menu=parent_menu)
            
            if not submenu_item:
                print(f"Submenu '{submenu_text}' not found")
                return False
            
            # Check if already expanded
            item_info = self.identifier.identify_menu_item(submenu_item)
            if item_info.get('expanded'):
                print(f"Submenu '{submenu_text}' is already expanded")
                return True
            
            # Scroll into view
            self.execute_js("arguments[0].scrollIntoView({block: 'center'});", submenu_item)
            time.sleep(0.5)
            
            # Click to expand
            try:
                submenu_item.click()
                time.sleep(1.0)  # Wait for submenu to open
                
                # Verify it's expanded
                item_info = self.identifier.identify_menu_item(submenu_item)
                if item_info.get('expanded'):
                    print(f"Expanded submenu '{submenu_text}'")
                    return True
                else:
                    # Try again with JavaScript
                    self.execute_js("arguments[0].click();", submenu_item)
                    time.sleep(1.0)
                    item_info = self.identifier.identify_menu_item(submenu_item)
                    if item_info.get('expanded'):
                        print(f"Expanded submenu '{submenu_text}' (via JavaScript)")
                        return True
                    else:
                        print(f"Submenu '{submenu_text}' did not expand")
                        return False
            except Exception as e:
                print(f"Error expanding submenu: {str(e)}")
                return False
        except Exception as e:
            print(f"Error expanding submenu: {str(e)}")
            return False
    
    def _expand_parent_submenus(self, item_element: WebElement, timeout: int = 15) -> None:
        """
        Automatically expand all parent submenus of an item
        
        Args:
            item_element: Menu item WebElement
            timeout: Maximum wait time in seconds
        """
        try:
            # Find all parent submenus
            parent_submenus = item_element.find_elements(By.XPATH, 
                './ancestor::li[contains(@class, "ant-menu-submenu")]')
            
            # Expand from outermost to innermost
            for parent_submenu in reversed(parent_submenus):
                try:
                    # Find the submenu title
                    submenu_title = parent_submenu.find_element(By.CSS_SELECTOR, '.ant-menu-submenu-title')
                    
                    # Check if already expanded
                    item_info = self.identifier.identify_menu_item(submenu_title)
                    if not item_info.get('expanded'):
                        # Expand it
                        self.execute_js("arguments[0].scrollIntoView({block: 'center'});", submenu_title)
                        time.sleep(0.3)
                        submenu_title.click()
                        time.sleep(0.8)  # Wait for submenu to open
                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue
        except Exception:
            pass
    
    def is_menu_present(self, menu_text: str, parent_menu: Optional[WebElement] = None,
                       timeout: int = 10) -> bool:
        """
        Check if a menu item is present
        
        Args:
            menu_text: Text of menu item to check
            parent_menu: Optional parent menu element to search within
            timeout: Maximum wait time in seconds
            
        Returns:
            True if menu item is present, False otherwise
        """
        try:
            item = self.locator.find_menu_item_by_text(menu_text, timeout=timeout,
                                                      parent_menu=parent_menu)
            return item is not None
        except:
            return False
    
    def print_menu_structure(self, menu_element: Optional[WebElement] = None) -> None:
        """
        Print the menu structure in a readable format (for debugging)
        
        Args:
            menu_element: Optional menu element, if None uses first menu found
        """
        try:
            structure = self.locator.get_menu_structure(menu_element)
            
            print("\n" + "="*70)
            print("Detected Menu Structure:")
            print("="*70)
            
            menu_type = structure.get('type', 'unknown')
            collapsed = structure.get('collapsed', False)
            
            print(f"Menu Type: {menu_type}")
            if collapsed:
                print("Status: Collapsed")
            print()
            
            def print_items(items, indent=0):
                for item in items:
                    prefix = "   " * indent + "- "
                    text = item.get('text', '(no text)')
                    item_type = item.get('type', 'menu-item')
                    disabled = item.get('disabled', False)
                    expanded = item.get('expanded', False)
                    
                    status_parts = []
                    if disabled:
                        status_parts.append("disabled")
                    if expanded:
                        status_parts.append("expanded")
                    if item_type == 'submenu-title':
                        status_parts.append("submenu")
                    
                    status = f" ({', '.join(status_parts)})" if status_parts else ""
                    
                    print(f"{prefix}{text}{status}")
                    
                    # Print children if any
                    if item.get('children'):
                        print_items(item['children'], indent + 1)
            
            print_items(structure.get('items', []))
            print("="*70 + "\n")
        except Exception as e:
            print(f"Error printing menu structure: {str(e)}")
    
    def identify_and_store(self, identifier: str, identifier_type: str = 'data_attr_id',
                          timeout: int = 10, context_key: Optional[str] = None) -> bool:
        """
        Identify a menu and store it in context
        
        Args:
            identifier: Value to identify the menu (data-attr-id, text, or position)
            identifier_type: Type of identifier ('data_attr_id', 'text', 'position', 'auto')
            timeout: Maximum wait time in seconds
            context_key: Optional key to use in context (defaults to identifier)
            
        Returns:
            True if menu was identified and stored, False otherwise
        """
        try:
            element = None
            
            if identifier_type == 'data_attr_id':
                element = self.locator.find_menu_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                element = self.locator.find_menu_by_position(position, timeout, self.context)
            elif identifier_type == 'text':
                # Find first menu, then find item by text
                menus = self.locator.find_all_menus(timeout)
                if menus:
                    element = self.locator.find_menu_item_by_text(identifier, timeout, 
                                                                 self.context, menus[0])
            
            if element:
                if context_key:
                    self.locator._store_element_in_context(element, context_key, self.context)
                else:
                    self.locator._store_element_in_context(element, identifier, self.context)
                return True
            
            return False
        except Exception as e:
            print(f"Error identifying menu: {str(e)}")
            return False
    
    def identify_menu_item_by_text_and_parent(self, menu_text: str, parent_menu_text: Optional[str] = None,
                                              parent_menu: Optional[WebElement] = None,
                                              timeout: int = 15, context_key: Optional[str] = None) -> bool:
        """
        Identify a menu item by text and optionally by parent menu, then store in context
        
        Args:
            menu_text: Text of the menu item to find
            parent_menu_text: Optional text of parent menu/submenu to search within
            parent_menu: Optional parent menu WebElement to search within
            timeout: Maximum wait time in seconds
            context_key: Optional key to use in context (defaults to menu_text)
            
        Returns:
            True if menu item was identified and stored, False otherwise
        """
        try:
            search_menu = parent_menu
            
            # If parent_menu_text is provided, find the parent menu first
            if parent_menu_text and not search_menu:
                menus = self.locator.find_all_menus(timeout)
                for menu in menus:
                    parent_item = self.locator.find_menu_item_by_text(parent_menu_text, timeout=5,
                                                                     parent_menu=menu)
                    if parent_item:
                        # Found parent, now find its submenu container
                        try:
                            submenu_container = parent_item.find_element(By.XPATH,
                                './ancestor::li[contains(@class, "ant-menu-submenu")]')
                            search_menu = submenu_container
                            break
                        except:
                            search_menu = menu
                            break
            
            # Find the menu item
            item = self.locator.find_menu_item_by_text(menu_text, timeout=timeout,
                                                      context=self.context, parent_menu=search_menu)
            
            if item:
                key = context_key if context_key else f"{parent_menu_text}_{menu_text}" if parent_menu_text else menu_text
                self.locator._store_element_in_context(item, key, self.context)
                print(f"   >> Stored menu item '{menu_text}' in context with key: '{key}'")
                return True
            
            print(f"   >> Menu item '{menu_text}' not found")
            return False
        except Exception as e:
            print(f"Error identifying menu item: {str(e)}")
            return False
    
    def identify_menu_item_by_position(self, position: int, parent_menu: Optional[WebElement] = None,
                                      timeout: int = 15, context_key: Optional[str] = None) -> bool:
        """
        Identify a menu item by position (1-based index) and store in context
        
        Args:
            position: Position of menu item (1-based)
            parent_menu: Optional parent menu to search within
            timeout: Maximum wait time in seconds
            context_key: Optional key to use in context
            
        Returns:
            True if menu item was identified and stored, False otherwise
        """
        try:
            search_menu = parent_menu
            if not search_menu:
                menus = self.locator.find_all_menus(timeout)
                if menus:
                    search_menu = menus[0]
            
            if not search_menu:
                print("   >> No menu found to search")
                return False
            
            items = self.locator.find_all_menu_items(search_menu, include_submenus=True)
            
            if 1 <= position <= len(items):
                item = items[position - 1]
                key = context_key if context_key else f"menu_item_{position}"
                self.locator._store_element_in_context(item, key, self.context)
                print(f"   >> Stored menu item at position {position} in context with key: '{key}'")
                return True
            
            print(f"   >> Position {position} out of range. Found {len(items)} items")
            return False
        except Exception as e:
            print(f"Error identifying menu item by position: {str(e)}")
            return False
    
    def click_from_context(self, context_key: str, timeout: int = 15) -> bool:
        """
        Click a menu item stored in context
        
        Args:
            context_key: Key of the menu item in context
            timeout: Maximum wait time in seconds
            
        Returns:
            True if menu item was clicked successfully, False otherwise
        """
        try:
            if not self.context:
                print("No context available")
                return False
            
            element_info = self.context.get_element(context_key)
            if not element_info:
                print(f"Menu item '{context_key}' not found in context")
                return False
            
            element = element_info.element
            
            # Re-find element if stale
            try:
                element.is_displayed()
            except StaleElementReferenceException:
                # Try to re-find by data-attr-id or text
                data_attr_id = element_info.data_attr_id
                if data_attr_id:
                    element = self.locator.find_menu_item_by_data_attr(data_attr_id, timeout, 
                                                                      self.context)
                else:
                    text = element_info.metadata.get('text', '')
                    if text:
                        element = self.locator.find_menu_item_by_text(text, timeout, self.context)
                
                if not element:
                    print(f"Could not re-find menu item '{context_key}'")
                    return False
            
            # Check if clickable
            if not self.identifier.is_item_clickable(element):
                print(f"Menu item '{context_key}' is disabled")
                return False
            
            # Expand parent submenus if needed
            self._expand_parent_submenus(element, timeout)
            
            # Scroll and click
            self.execute_js("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            
            try:
                element.click()
                time.sleep(0.5)
                print(f"Clicked menu item '{context_key}' from context")
                return True
            except:
                self.execute_js("arguments[0].click();", element)
                time.sleep(0.5)
                print(f"Clicked menu item '{context_key}' from context (via JavaScript)")
                return True
        except Exception as e:
            print(f"Error clicking from context: {str(e)}")
            return False

