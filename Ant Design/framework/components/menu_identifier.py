"""
Menu Identifier - Identifies and analyzes Ant Design Menu and SubMenu properties
Single Responsibility: Analyze menu items and extract their properties
"""
from selenium.webdriver.remote.webelement import WebElement
from typing import Dict, Optional
from selenium.webdriver.common.by import By


class MenuIdentifier:
    """
    Handles identifying and analyzing Ant Design Menu and SubMenu items
    Single Responsibility: Extract properties from menu elements
    """
    
    def identify_menu_type(self, menu_element: WebElement) -> str:
        """
        Identify the type of menu (vertical, horizontal, inline, collapsed)
        
        Args:
            menu_element: Menu WebElement
            
        Returns:
            Menu type string
        """
        try:
            class_attr = menu_element.get_attribute('class') or ''
            
            if 'ant-menu-inline-collapsed' in class_attr:
                return 'inline-collapsed'
            elif 'ant-menu-inline' in class_attr:
                return 'inline'
            elif 'ant-menu-vertical' in class_attr:
                return 'vertical'
            elif 'ant-menu-horizontal' in class_attr:
                return 'horizontal'
            else:
                return 'default'
        except:
            return 'unknown'
    
    def is_menu_collapsed(self, menu_element: WebElement) -> bool:
        """
        Check if menu is collapsed
        
        Args:
            menu_element: Menu WebElement
            
        Returns:
            True if collapsed, False otherwise
        """
        try:
            class_attr = menu_element.get_attribute('class') or ''
            return 'ant-menu-inline-collapsed' in class_attr
        except:
            return False
    
    def identify_menu_item(self, item_element: WebElement) -> Dict:
        """
        Identify properties of a menu item or submenu
        
        Args:
            item_element: Menu item WebElement
            
        Returns:
            Dictionary with item properties
        """
        try:
            class_attr = item_element.get_attribute('class') or ''
            
            # Determine item type
            item_type = 'menu-item'
            if 'ant-menu-submenu-title' in class_attr:
                item_type = 'submenu-title'
            elif 'ant-menu-submenu' in class_attr:
                item_type = 'submenu'
            
            # Get text
            text = item_element.text.strip()
            
            # If no text, try to get from aria-label or title
            if not text:
                text = item_element.get_attribute('aria-label') or ''
            if not text:
                text = item_element.get_attribute('title') or ''
            
            # Get data-attr-id
            data_attr_id = item_element.get_attribute('data-attr-id')
            
            # Check if disabled
            disabled = 'ant-menu-item-disabled' in class_attr
            if not disabled:
                aria_disabled = item_element.get_attribute('aria-disabled')
                disabled = aria_disabled == 'true'
            
            # Check if selected
            selected = 'ant-menu-item-selected' in class_attr
            
            # Check if expanded (for submenus)
            expanded = False
            if item_type in ['submenu', 'submenu-title']:
                # Check parent submenu element
                try:
                    parent_li = item_element.find_element(By.XPATH, './ancestor-or-self::li[contains(@class, "ant-menu-submenu")]')
                    parent_class = parent_li.get_attribute('class') or ''
                    expanded = 'ant-menu-submenu-open' in parent_class
                    
                    # Also check aria-expanded
                    aria_expanded = item_element.get_attribute('aria-expanded')
                    if aria_expanded:
                        expanded = aria_expanded.lower() == 'true'
                except:
                    pass
            
            # Check if has children (submenu)
            has_children = False
            try:
                # Check if it's a submenu or has submenu class
                if 'ant-menu-submenu' in class_attr:
                    has_children = True
                else:
                    # Check if parent is a submenu
                    parent_li = item_element.find_element(By.XPATH, './ancestor::li[contains(@class, "ant-menu-submenu")]')
                    if parent_li:
                        has_children = False  # This is a child item
                    else:
                        # Check if this item contains submenu
                        submenu = item_element.find_elements(By.CSS_SELECTOR, '.ant-menu-submenu')
                        has_children = len(submenu) > 0
            except:
                pass
            
            # Determine level (depth)
            level = 1
            try:
                # Count parent submenus
                parent_submenus = item_element.find_elements(By.XPATH, './ancestor::li[contains(@class, "ant-menu-submenu")]')
                level = len(parent_submenus) + 1
            except:
                pass
            
            # Check if icon-only (no text but has icon)
            icon_only = False
            if not text:
                try:
                    icons = item_element.find_elements(By.CSS_SELECTOR, '.anticon, [class*="icon"]')
                    if icons:
                        icon_only = True
                except:
                    pass
            
            return {
                'type': item_type,
                'text': text,
                'data_attr_id': data_attr_id,
                'disabled': disabled,
                'selected': selected,
                'expanded': expanded,
                'has_children': has_children,
                'level': level,
                'icon_only': icon_only,
                'class': class_attr
            }
        except Exception as e:
            print(f"Error identifying menu item: {str(e)}")
            return {
                'type': 'unknown',
                'text': '',
                'data_attr_id': None,
                'disabled': False,
                'selected': False,
                'expanded': False,
                'has_children': False,
                'level': 1,
                'icon_only': False,
                'class': ''
            }
    
    def get_menu_item_text(self, item_element: WebElement) -> str:
        """
        Get text from menu item (handles icon-only items)
        
        Args:
            item_element: Menu item WebElement
            
        Returns:
            Text string
        """
        try:
            # Try regular text first
            text = item_element.text.strip()
            if text:
                return text
            
            # Try aria-label
            text = item_element.get_attribute('aria-label') or ''
            if text:
                return text
            
            # Try title
            text = item_element.get_attribute('title') or ''
            if text:
                return text
            
            # Try data-attr-id as fallback
            text = item_element.get_attribute('data-attr-id') or ''
            return text
        except:
            return ''
    
    def is_item_clickable(self, item_element: WebElement) -> bool:
        """
        Check if menu item is clickable (not disabled)
        
        Args:
            item_element: Menu item WebElement
            
        Returns:
            True if clickable, False otherwise
        """
        try:
            class_attr = item_element.get_attribute('class') or ''
            if 'ant-menu-item-disabled' in class_attr:
                return False
            
            aria_disabled = item_element.get_attribute('aria-disabled')
            if aria_disabled == 'true':
                return False
            
            return True
        except:
            return False








