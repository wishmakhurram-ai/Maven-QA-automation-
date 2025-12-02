"""
Pagination Identifier - Identifies properties of Ant Design Pagination components
Single Responsibility: Analyze pagination elements and extract their properties
"""
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Dict, List, Optional
from framework.identifiers.generic_element_identifier import GenericElementIdentifier


class PaginationIdentifier:
    """
    Identifies properties of Ant Design Pagination components
    Single Responsibility: Extract pagination metadata and state
    """
    
    def __init__(self):
        """Initialize Pagination Identifier"""
        self.generic_identifier = GenericElementIdentifier()
    
    def identify_pagination(self, pagination_element: WebElement) -> Dict:
        """
        Identify all properties of a pagination component
        
        Args:
            pagination_element: The pagination container WebElement
            
        Returns:
            Dictionary with pagination properties:
            - type: 'pagination'
            - current_page: Current active page number
            - total_pages: Total number of pages
            - total_items: Total number of items (if available)
            - page_size: Current page size
            - available_page_sizes: List of available page sizes
            - next_enabled: Whether next button is enabled
            - prev_enabled: Whether previous button is enabled
            - has_jump_to: Whether jump-to input exists
            - has_page_size_changer: Whether page size changer exists
            - style: 'mini', 'small', 'default', 'large'
            - simple_mode: Whether in simple mode (only prev/next)
            - data_attr_id: Custom data-attr-id if present
        """
        try:
            info = {
                'type': 'pagination',
                'data_attr_id': None,
                'current_page': None,
                'total_pages': None,
                'total_items': None,
                'page_size': None,
                'available_page_sizes': [],
                'next_enabled': False,
                'prev_enabled': False,
                'has_jump_to': False,
                'has_page_size_changer': False,
                'style': 'default',
                'simple_mode': False,
                'page_numbers': [],
                'has_ellipsis': False
            }
            
            # Get data-attr-id if present
            data_attr_id = pagination_element.get_attribute('data-atr-id')
            if data_attr_id:
                info['data_attr_id'] = data_attr_id
            
            # Detect style
            class_attr = pagination_element.get_attribute('class') or ''
            if 'ant-pagination-mini' in class_attr:
                info['style'] = 'mini'
            elif 'ant-pagination-small' in class_attr:
                info['style'] = 'small'
            elif 'ant-pagination-large' in class_attr:
                info['style'] = 'large'
            
            # Check for simple mode
            if 'ant-pagination-simple' in class_attr:
                info['simple_mode'] = True
            
            # Find current page
            try:
                active_item = pagination_element.find_element(By.CSS_SELECTOR, '.ant-pagination-item-active')
                active_text = active_item.text.strip()
                if active_text.isdigit():
                    info['current_page'] = int(active_text)
            except:
                pass
            
            # Find all page numbers
            try:
                page_items = pagination_element.find_elements(By.CSS_SELECTOR, '.ant-pagination-item:not(.ant-pagination-item-active)')
                page_numbers = []
                for item in page_items:
                    text = item.text.strip()
                    if text.isdigit():
                        page_numbers.append(int(text))
                info['page_numbers'] = sorted(page_numbers)
            except:
                pass
            
            # Check for ellipsis
            try:
                ellipsis = pagination_element.find_elements(By.CSS_SELECTOR, '.ant-pagination-item-ellipsis')
                info['has_ellipsis'] = len(ellipsis) > 0
            except:
                pass
            
            # Check next/prev buttons
            try:
                next_btn = pagination_element.find_element(By.CSS_SELECTOR, '.ant-pagination-next')
                next_class = next_btn.get_attribute('class') or ''
                info['next_enabled'] = 'ant-pagination-disabled' not in next_class
            except:
                pass
            
            try:
                prev_btn = pagination_element.find_element(By.CSS_SELECTOR, '.ant-pagination-prev')
                prev_class = prev_btn.get_attribute('class') or ''
                info['prev_enabled'] = 'ant-pagination-disabled' not in prev_class
            except:
                pass
            
            # Find total pages (try multiple methods)
            try:
                # Method 1: Look for last page number
                all_items = pagination_element.find_elements(By.CSS_SELECTOR, '.ant-pagination-item')
                page_nums = []
                for item in all_items:
                    text = item.text.strip()
                    if text.isdigit():
                        page_nums.append(int(text))
                if page_nums:
                    info['total_pages'] = max(page_nums)
                    # If we have ellipsis, total might be higher - try to get from total text
                    if info['has_ellipsis']:
                        # Look for total text like "1-10 of 100"
                        total_text_elem = pagination_element.find_elements(By.XPATH, ".//*[contains(text(), 'of') or contains(text(), '共')]")
                        for elem in total_text_elem:
                            text = elem.text.strip()
                            # Try to extract total from text
                            import re
                            match = re.search(r'of\s+(\d+)', text, re.IGNORECASE)
                            if match:
                                total_items = int(match.group(1))
                                if info['page_size']:
                                    info['total_pages'] = (total_items + info['page_size'] - 1) // info['page_size']
                                break
            except:
                pass
            
            # Check for page size changer
            try:
                size_changer = pagination_element.find_element(By.CSS_SELECTOR, '.ant-pagination-options-size-changer')
                info['has_page_size_changer'] = True
                
                # Get current page size
                try:
                    size_select = size_changer.find_element(By.CSS_SELECTOR, '.ant-select-selection-item')
                    size_text = size_select.text.strip()
                    # Extract number from text like "10 / page"
                    import re
                    match = re.search(r'(\d+)', size_text)
                    if match:
                        info['page_size'] = int(match.group(1))
                except:
                    pass
                
                # Get available page sizes
                try:
                    # Click to open dropdown (we'll just detect it exists, actual sizes need interaction)
                    size_options = pagination_element.find_elements(By.CSS_SELECTOR, '.ant-select-item-option')
                    available_sizes = []
                    for option in size_options:
                        text = option.text.strip()
                        match = re.search(r'(\d+)', text)
                        if match:
                            available_sizes.append(int(match.group(1)))
                    if available_sizes:
                        info['available_page_sizes'] = sorted(available_sizes)
                    else:
                        # Default sizes if not found
                        info['available_page_sizes'] = [10, 20, 50, 100]
                except:
                    # Default sizes
                    info['available_page_sizes'] = [10, 20, 50, 100]
            except:
                pass
            
            # Check for jump-to input
            try:
                jump_input = pagination_element.find_element(By.CSS_SELECTOR, '.ant-pagination-options-quick-jumper input')
                info['has_jump_to'] = True
            except:
                try:
                    # Alternative selector
                    jump_input = pagination_element.find_element(By.CSS_SELECTOR, 'input[placeholder*="跳转" i], input[placeholder*="Go to" i], input[placeholder*="jump" i]')
                    info['has_jump_to'] = True
                except:
                    pass
            
            # Get total items if available
            try:
                total_text_elem = pagination_element.find_elements(By.XPATH, ".//*[contains(text(), 'of') or contains(text(), '共') or contains(text(), 'Total')]")
                for elem in total_text_elem:
                    text = elem.text.strip()
                    import re
                    # Try patterns like "1-10 of 100", "共 100 条", "Total: 100"
                    match = re.search(r'(?:of|共|Total:?)\s*(\d+)', text, re.IGNORECASE)
                    if match:
                        info['total_items'] = int(match.group(1))
                        break
            except:
                pass
            
            return info
            
        except Exception as e:
            print(f"Error identifying pagination: {str(e)}")
            return {
                'type': 'pagination',
                'error': str(e)
            }
    
    def get_page_elements(self, pagination_element: WebElement) -> Dict[str, Optional[WebElement]]:
        """
        Get all interactive elements within a pagination component
        Handles stale elements by re-finding them
        
        Args:
            pagination_element: The pagination container WebElement
            
        Returns:
            Dictionary with element types as keys and WebElements as values:
            - next_button: Next page button
            - prev_button: Previous page button
            - first_button: First page button (if exists)
            - last_button: Last page button (if exists)
            - page_items: List of page number items
            - jump_input: Jump-to input field
            - size_changer: Page size changer dropdown
            - go_button: Go/Submit button (if exists)
        """
        elements = {
            'next_button': None,
            'prev_button': None,
            'first_button': None,
            'last_button': None,
            'page_items': [],
            'jump_input': None,
            'size_changer': None,
            'go_button': None
        }
        
        try:
            # Helper function to safely find element with stale element handling
            def safe_find_element(selector, multiple=False):
                try:
                    if multiple:
                        return pagination_element.find_elements(By.CSS_SELECTOR, selector)
                    else:
                        return pagination_element.find_element(By.CSS_SELECTOR, selector)
                except Exception as e:
                    # If stale, return None - caller should re-find pagination element
                    if 'stale' in str(e).lower():
                        return None
                    return None
            
            # Next button
            elements['next_button'] = safe_find_element('.ant-pagination-next')
            
            # Previous button
            elements['prev_button'] = safe_find_element('.ant-pagination-prev')
            
            # Page items
            page_items = safe_find_element('.ant-pagination-item', multiple=True)
            if page_items:
                elements['page_items'] = page_items
            
            # Jump-to input - try multiple selectors
            jump_selectors = [
                '.ant-pagination-options-quick-jumper input',
                'input[placeholder*="跳转" i]',
                'input[placeholder*="Go to" i]',
                'input[placeholder*="jump" i]',
                '.ant-pagination-options input[type="text"]'
            ]
            for selector in jump_selectors:
                jump_input = safe_find_element(selector)
                if jump_input:
                    elements['jump_input'] = jump_input
                    break
            
            # Size changer - try multiple selectors
            size_selectors = [
                '.ant-pagination-options-size-changer',
                '.ant-pagination-options .ant-select',
                '.ant-pagination-options-size-changer .ant-select'
            ]
            for selector in size_selectors:
                size_changer = safe_find_element(selector)
                if size_changer:
                    elements['size_changer'] = size_changer
                    break
            
            # Go button (usually next to jump input)
            go_selectors = [
                '.ant-pagination-options-quick-jumper button',
                '.ant-pagination-options-quick-jumper .ant-btn',
                '.ant-pagination-options button'
            ]
            for selector in go_selectors:
                go_button = safe_find_element(selector)
                if go_button:
                    elements['go_button'] = go_button
                    break
            
        except Exception as e:
            print(f"Error getting page elements: {str(e)}")
        
        return elements

