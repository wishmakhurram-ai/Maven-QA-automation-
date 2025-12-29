"""
Menu Locator - Handles finding and locating Ant Design Menu and SubMenu items
Single Responsibility: Locate menus and menu items by various criteria without hardcoded selectors
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from typing import Optional, List, Dict
from framework.base.base_page import BasePage
from framework.context.element_context import ElementContext, ElementInfo
from framework.components.menu_identifier import MenuIdentifier
import time


class MenuLocator(BasePage):
    """
    Handles locating/finding Ant Design Menu and SubMenu items on the page
    Single Responsibility: Find menus and menu items by various identification methods
    Uses Ant Design class patterns, data-attr-id, aria attributes, and semantic labels
    """
    
    # Ant Design menu class patterns
    MENU_CLASSES = {
        'menu': 'ant-menu',
        'menu_item': 'ant-menu-item',
        'submenu': 'ant-menu-submenu',
        'submenu_title': 'ant-menu-submenu-title',
        'submenu_open': 'ant-menu-submenu-open',
        'menu_selected': 'ant-menu-item-selected',
        'menu_disabled': 'ant-menu-item-disabled',
        'menu_inline': 'ant-menu-inline',
        'menu_vertical': 'ant-menu-vertical',
        'menu_horizontal': 'ant-menu-horizontal',
        'menu_collapsed': 'ant-menu-inline-collapsed'
    }
    
    def __init__(self, driver: webdriver):
        """
        Initialize Menu Locator
        
        Args:
            driver: Selenium WebDriver instance
        """
        super().__init__(driver)
        self.identifier = MenuIdentifier()
    
    def find_all_menus(self, timeout: int = 10) -> List[WebElement]:
        """
        Find all Ant Design menu containers on the page
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            List of menu WebElements
        """
        try:
            # Find all menu containers using Ant Design class patterns
            menus = []
            
            # Strategy 1: Find by ant-menu class
            menu_elements = self.find_elements(By.CSS_SELECTOR, '.ant-menu', timeout)
            menus.extend(menu_elements)
            
            # Strategy 2: Find by role="menu"
            role_menus = self.find_elements(By.CSS_SELECTOR, '[role="menu"]', timeout)
            for menu in role_menus:
                if menu not in menus:
                    menus.append(menu)
            
            # Deduplicate by comparing element IDs or locations
            unique_menus = []
            seen_ids = set()
            for menu in menus:
                try:
                    element_id = menu.id
                    if element_id not in seen_ids:
                        seen_ids.add(element_id)
                        unique_menus.append(menu)
                except StaleElementReferenceException:
                    continue
            
            return unique_menus
        except Exception as e:
            print(f"Error finding menus: {str(e)}")
            return []
    
    def find_menu_by_data_attr(self, data_attr_id: str, timeout: int = 10,
                                context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find menu by custom data-attr-id attribute
        PRIORITY: This is the primary method for finding menus
        
        Args:
            data_attr_id: Value of data-attr-id attribute
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            # Try multiple strategies to find menu with data-attr-id
            element = None
            
            # Strategy 1: Direct match on menu element
            element = self.find_element(By.CSS_SELECTOR, f'[data-attr-id="{data_attr_id}"].ant-menu', timeout)
            
            # Strategy 2: Parent container with data-attr-id
            if not element:
                element = self.find_element(By.CSS_SELECTOR, f'[data-attr-id="{data_attr_id}"] .ant-menu', timeout)
            
            # Strategy 3: Any element with data-attr-id that contains menu
            if not element:
                candidates = self.find_elements(By.CSS_SELECTOR, f'[data-attr-id="{data_attr_id}"]', timeout)
                for candidate in candidates:
                    class_attr = candidate.get_attribute('class') or ''
                    if 'ant-menu' in class_attr:
                        element = candidate
                        break
                    # Check if candidate contains menu
                    try:
                        menu_elem = candidate.find_element(By.CSS_SELECTOR, '.ant-menu')
                        element = menu_elem
                        break
                    except:
                        pass
            
            if element and context:
                self._store_element_in_context(element, data_attr_id, context)
            return element
        except TimeoutException:
            return None
    
    def find_menu_item_by_text(self, menu_text: str, timeout: int = 10,
                               context: Optional[ElementContext] = None,
                               parent_menu: Optional[WebElement] = None) -> Optional[WebElement]:
        """
        Find menu item by visible text (supports fuzzy matching)
        
        Args:
            menu_text: Text to search for
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            parent_menu: Optional parent menu element to search within
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            search_scope = parent_menu if parent_menu else self.driver
            
            # Strategy 1: Exact text match
            try:
                items = search_scope.find_elements(By.CSS_SELECTOR, '.ant-menu-item, .ant-menu-submenu-title')
                for item in items:
                    try:
                        text = item.text.strip()
                        if text == menu_text:
                            if context:
                                self._store_element_in_context(item, menu_text, context)
                            return item
                    except StaleElementReferenceException:
                        continue
            except:
                pass
            
            # Strategy 2: Partial text match (case-insensitive)
            try:
                items = search_scope.find_elements(By.CSS_SELECTOR, '.ant-menu-item, .ant-menu-submenu-title')
                for item in items:
                    try:
                        text = item.text.strip().lower()
                        if menu_text.lower() in text or text in menu_text.lower():
                            if context:
                                self._store_element_in_context(item, menu_text, context)
                            return item
                    except StaleElementReferenceException:
                        continue
            except:
                pass
            
            # Strategy 3: Match by aria-label
            try:
                items = search_scope.find_elements(By.CSS_SELECTOR, '[role="menuitem"], .ant-menu-item, .ant-menu-submenu-title')
                for item in items:
                    try:
                        aria_label = item.get_attribute('aria-label') or ''
                        if menu_text.lower() in aria_label.lower() or aria_label.lower() in menu_text.lower():
                            if context:
                                self._store_element_in_context(item, menu_text, context)
                            return item
                    except StaleElementReferenceException:
                        continue
            except:
                pass
            
            # Strategy 4: Match by title attribute
            try:
                items = search_scope.find_elements(By.CSS_SELECTOR, '.ant-menu-item, .ant-menu-submenu-title')
                for item in items:
                    try:
                        title = item.get_attribute('title') or ''
                        if menu_text.lower() in title.lower() or title.lower() in menu_text.lower():
                            if context:
                                self._store_element_in_context(item, menu_text, context)
                            return item
                    except StaleElementReferenceException:
                        continue
            except:
                pass
            
            return None
        except Exception as e:
            print(f"Error finding menu item by text: {str(e)}")
            return None
    
    def find_menu_item_by_data_attr(self, data_attr_id: str, timeout: int = 10,
                                    context: Optional[ElementContext] = None,
                                    parent_menu: Optional[WebElement] = None) -> Optional[WebElement]:
        """
        Find menu item by data-attr-id
        
        Args:
            data_attr_id: Value of data-attr-id attribute
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            parent_menu: Optional parent menu element to search within
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            search_scope = parent_menu if parent_menu else self.driver
            
            # Strategy 1: Direct match
            element = search_scope.find_element(By.CSS_SELECTOR, f'[data-attr-id="{data_attr_id}"]', timeout)
            
            # Strategy 2: Within menu item
            if not element:
                try:
                    items = search_scope.find_elements(By.CSS_SELECTOR, '.ant-menu-item, .ant-menu-submenu-title')
                    for item in items:
                        try:
                            item_data_attr = item.get_attribute('data-attr-id')
                            if item_data_attr == data_attr_id:
                                element = item
                                break
                        except StaleElementReferenceException:
                            continue
                except:
                    pass
            
            if element and context:
                self._store_element_in_context(element, data_attr_id, context)
            return element
        except TimeoutException:
            return None
    
    def find_all_menu_items(self, parent_menu: Optional[WebElement] = None,
                           include_submenus: bool = True) -> List[WebElement]:
        """
        Find all menu items (including submenu titles) in a menu
        
        Args:
            parent_menu: Optional parent menu element to search within
            include_submenus: If True, includes submenu titles
            
        Returns:
            List of menu item WebElements
        """
        try:
            search_scope = parent_menu if parent_menu else self.driver
            
            items = []
            
            # Find all menu items
            menu_items = search_scope.find_elements(By.CSS_SELECTOR, '.ant-menu-item')
            items.extend(menu_items)
            
            # Find all submenu titles if requested
            if include_submenus:
                submenu_titles = search_scope.find_elements(By.CSS_SELECTOR, '.ant-menu-submenu-title')
                items.extend(submenu_titles)
            
            # Filter out disabled items (optional - can be enabled later)
            # active_items = [item for item in items if 'ant-menu-item-disabled' not in (item.get_attribute('class') or '')]
            
            return items
        except Exception as e:
            print(f"Error finding menu items: {str(e)}")
            return []
    
    def find_submenu_items(self, submenu_element: WebElement) -> List[WebElement]:
        """
        Find all items within a submenu
        
        Args:
            submenu_element: Submenu WebElement
            
        Returns:
            List of menu item WebElements within the submenu
        """
        try:
            # Find items within submenu
            submenu_items = submenu_element.find_elements(By.CSS_SELECTOR, '.ant-menu-item, .ant-menu-submenu-title')
            return submenu_items
        except Exception as e:
            print(f"Error finding submenu items: {str(e)}")
            return []
    
    def find_menu_by_position(self, position: int, timeout: int = 10,
                              context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find menu by position (1-based index)
        
        Args:
            position: Position of menu (1-based)
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            menus = self.find_all_menus(timeout)
            if 1 <= position <= len(menus):
                menu = menus[position - 1]
                if context:
                    self._store_element_in_context(menu, f'menu_{position}', context)
                return menu
            return None
        except Exception as e:
            print(f"Error finding menu by position: {str(e)}")
            return None
    
    def _store_element_in_context(self, element: WebElement, key: str, context: ElementContext) -> None:
        """
        Store element in context with metadata
        
        Args:
            element: WebElement to store
            key: Key to use in context
            context: ElementContext instance
        """
        try:
            # Get element properties
            menu_info = self.identifier.identify_menu_item(element)
            
            element_info = ElementInfo(
                element=element,
                element_type='menu_item',
                application_type=menu_info.get('type'),
                data_attr_id=menu_info.get('data_attr_id'),
                metadata={
                    'text': menu_info.get('text'),
                    'level': menu_info.get('level'),
                    'disabled': menu_info.get('disabled'),
                    'expanded': menu_info.get('expanded'),
                    'has_children': menu_info.get('has_children')
                }
            )
            
            context.store_element(key, element_info)
        except Exception as e:
            print(f"Error storing element in context: {str(e)}")
    
    def get_menu_structure(self, menu_element: Optional[WebElement] = None) -> Dict:
        """
        Get the complete structure of a menu (for debugging/printing)
        
        Args:
            menu_element: Optional menu element, if None uses first menu found
            
        Returns:
            Dictionary representing menu structure
        """
        try:
            if not menu_element:
                menus = self.find_all_menus()
                if not menus:
                    return {}
                menu_element = menus[0]
            
            structure = {
                'type': self.identifier.identify_menu_type(menu_element),
                'collapsed': self.identifier.is_menu_collapsed(menu_element),
                'items': []
            }
            
            items = self.find_all_menu_items(menu_element, include_submenus=True)
            
            for item in items:
                try:
                    item_info = self.identifier.identify_menu_item(item)
                    item_data = {
                        'text': item_info.get('text'),
                        'type': item_info.get('type'),
                        'level': item_info.get('level'),
                        'disabled': item_info.get('disabled'),
                        'expanded': item_info.get('expanded'),
                        'data_attr_id': item_info.get('data_attr_id')
                    }
                    
                    # If it's a submenu, get its children
                    if item_info.get('has_children'):
                        submenu = item.find_element(By.XPATH, './ancestor-or-self::li[contains(@class, "ant-menu-submenu")]')
                        submenu_items = self.find_submenu_items(submenu)
                        item_data['children'] = []
                        for sub_item in submenu_items:
                            try:
                                sub_item_info = self.identifier.identify_menu_item(sub_item)
                                item_data['children'].append({
                                    'text': sub_item_info.get('text'),
                                    'type': sub_item_info.get('type'),
                                    'level': sub_item_info.get('level'),
                                    'disabled': sub_item_info.get('disabled')
                                })
                            except:
                                pass
                    
                    structure['items'].append(item_data)
                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue
            
            return structure
        except Exception as e:
            print(f"Error getting menu structure: {str(e)}")
            return {}

