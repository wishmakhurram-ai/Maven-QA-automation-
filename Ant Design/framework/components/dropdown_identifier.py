"""
Dropdown Identifier - Handles analyzing and identifying Ant Design dropdown properties
Single Responsibility: Analyze dropdown elements and extract their properties
"""
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Dict, Optional, List
from framework.identifiers.generic_element_identifier import GenericElementIdentifier


class DropdownIdentifier:
    """
    Handles identifying and analyzing Ant Design dropdown/Select field properties
    Single Responsibility: Extract dropdown type, size, state, options, and other properties
    """
    
    # Ant Design dropdown size classes
    SIZE_CLASSES = {
        'large': 'ant-select-lg',
        'small': 'ant-select-sm'
    }
    
    # Ant Design dropdown type patterns
    DROPDOWN_TYPES = {
        'single': 'single',
        'multiple': 'multiple',
        'tags': 'tags',
        'searchable': 'searchable',
        'tree': 'tree',
        'cascader': 'cascader'
    }
    
    @staticmethod
    def identify_dropdown_type(element: WebElement) -> Dict[str, any]:
        """
        Automatically identify the type and properties of an Ant Design dropdown
        PRIORITY: data-attr-id is checked first to determine field type
        Integrates with GenericElementIdentifier to read custom attributes
        
        Args:
            element: WebElement representing the dropdown
            
        Returns:
            Dictionary containing dropdown properties:
            {
                'type': 'single'|'multiple'|'tags'|'searchable'|'tree'|'cascader',
                'size': 'large'|'middle'|'small',
                'disabled': bool,
                'loading': bool,
                'searchable': bool,
                'placeholder': str,
                'label': str,
                'selected_values': list,
                'available_options': list,
                'options_count': int,
                'data_attr_id': str|None,
                'application_type': str|None,
                'metadata': dict
            }
        """
        # First, get generic element information
        generic_info = GenericElementIdentifier.identify_element(element)
        
        dropdown_info = {
            'type': 'single',
            'size': 'middle',
            'disabled': False,
            'loading': False,
            'searchable': False,
            'placeholder': '',
            'label': '',
            'selected_values': [],
            'available_options': [],
            'options_count': 0,
            'data_attr_id': generic_info.get('data_attr_id'),
            'application_type': generic_info.get('application_type'),
            'metadata': generic_info.get('metadata', {})
        }
        
        try:
            tag_name = element.tag_name.lower()
            class_attr = element.get_attribute('class') or ''
            classes = class_attr.split()
            
            # PRIORITY 1: Determine dropdown type from data-attr-id (if it contains type info)
            data_attr_id = dropdown_info['data_attr_id']
            if data_attr_id:
                data_attr_lower = data_attr_id.lower()
                if 'multiple' in data_attr_lower or 'multi' in data_attr_lower:
                    dropdown_info['type'] = 'multiple'
                elif 'tag' in data_attr_lower:
                    dropdown_info['type'] = 'tags'
                elif 'search' in data_attr_lower or 'searchable' in data_attr_lower:
                    dropdown_info['type'] = 'searchable'
                elif 'tree' in data_attr_lower:
                    dropdown_info['type'] = 'tree'
                elif 'cascader' in data_attr_lower or 'cascade' in data_attr_lower:
                    dropdown_info['type'] = 'cascader'
            
            # Check if it's a native select element
            if tag_name == 'select':
                multiple = element.get_attribute('multiple')
                if multiple is not None:
                    dropdown_info['type'] = 'multiple'
                dropdown_info['searchable'] = False  # Native selects are not searchable
            else:
                # Check if it's Ant Design Dropdown component (menu dropdown, not Select)
                if 'ant-dropdown' in class_attr or 'ant-dropdown-trigger' in class_attr:
                    dropdown_info['type'] = 'dropdown'  # Menu dropdown
                    dropdown_info['searchable'] = False
                    # Get label from text content or aria-label
                    try:
                        text = element.text.strip()
                        if text:
                            dropdown_info['label'] = text
                        aria_label = element.get_attribute('aria-label') or ''
                        if aria_label:
                            dropdown_info['label'] = aria_label
                    except:
                        pass
                    return dropdown_info
                
                # Ant Design Select component (div with ant-select class)
                if 'ant-select' not in class_attr:
                    # Not an Ant Design dropdown
                    return dropdown_info
                
                # Identify type from classes
                if 'ant-select-multiple' in class_attr:
                    dropdown_info['type'] = 'multiple'
                elif 'ant-select-show-search' in class_attr:
                    dropdown_info['type'] = 'searchable'
                    dropdown_info['searchable'] = True
                elif 'ant-select-tree-select' in class_attr:
                    dropdown_info['type'] = 'tree'
                elif 'ant-cascader' in class_attr:
                    dropdown_info['type'] = 'cascader'
                
                # Check for tags mode (multiple with tags)
                if 'ant-select-multiple' in class_attr:
                    try:
                        selector = element.find_element(By.CSS_SELECTOR, '.ant-select-selector')
                        if 'ant-select-selection-overflow' in (selector.get_attribute('class') or ''):
                            dropdown_info['type'] = 'tags'
                    except:
                        pass
                
                # Check if searchable (show-search or allowClear with search)
                if 'ant-select-show-search' in class_attr:
                    dropdown_info['searchable'] = True
                else:
                    # Check if has search input inside
                    try:
                        search_input = element.find_element(By.CSS_SELECTOR, '.ant-select-selection-search input')
                        dropdown_info['searchable'] = True
                    except:
                        dropdown_info['searchable'] = False
                
                # Get placeholder
                try:
                    selector = element.find_element(By.CSS_SELECTOR, '.ant-select-selector')
                    placeholder_elem = selector.find_element(By.CSS_SELECTOR, '.ant-select-selection-placeholder')
                    dropdown_info['placeholder'] = placeholder_elem.text.strip()
                except:
                    try:
                        # Try getting placeholder from aria-placeholder
                        placeholder = element.get_attribute('aria-placeholder') or selector.get_attribute('placeholder') or ''
                        dropdown_info['placeholder'] = placeholder
                    except:
                        dropdown_info['placeholder'] = ''
                
                # Get label from Form.Item or aria-label
                try:
                    aria_label = element.get_attribute('aria-label') or ''
                    if aria_label:
                        dropdown_info['label'] = aria_label
                    else:
                        # Try to find associated label
                        try:
                            parent = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'ant-form-item')]")
                            label_elem = parent.find_element(By.CSS_SELECTOR, 'label')
                            dropdown_info['label'] = label_elem.text.strip()
                        except:
                            pass
                except:
                    pass
                
                # Get selected values
                try:
                    selected_items = element.find_elements(By.CSS_SELECTOR, '.ant-select-selection-item')
                    selected_values = []
                    for item in selected_items:
                        text = item.text.strip()
                        if text:
                            selected_values.append(text)
                    dropdown_info['selected_values'] = selected_values
                except:
                    dropdown_info['selected_values'] = []
            
            # Identify size
            for size, size_class in DropdownIdentifier.SIZE_CLASSES.items():
                if size_class in classes:
                    dropdown_info['size'] = size
                    break
            
            # Check if disabled
            dropdown_info['disabled'] = (
                'ant-select-disabled' in classes or
                element.get_attribute('disabled') is not None or
                element.get_attribute('aria-disabled') == 'true' or
                element.get_attribute('class') and 'disabled' in element.get_attribute('class').lower()
            )
            
            # Check if loading
            dropdown_info['loading'] = (
                'ant-select-loading' in classes or
                element.find_elements(By.CSS_SELECTOR, '.ant-select-loading-icon')
            )
            
            # Get available options (if dropdown is open or can be queried)
            try:
                options = DropdownIdentifier._get_available_options(element)
                dropdown_info['available_options'] = options
                dropdown_info['options_count'] = len(options)
            except:
                dropdown_info['available_options'] = []
                dropdown_info['options_count'] = 0
            
            return dropdown_info
            
        except Exception as e:
            print(f"Error identifying dropdown: {str(e)}")
            return dropdown_info
    
    @staticmethod
    def _get_available_options(element: WebElement) -> List[str]:
        """
        Get available options from dropdown
        Tries to find options in dropdown menu (if open) or from select element
        
        Args:
            element: Dropdown WebElement
            
        Returns:
            List of option text strings
        """
        options = []
        
        try:
            # If it's a native select element
            if element.tag_name.lower() == 'select':
                option_elements = element.find_elements(By.TAG_NAME, 'option')
                for opt in option_elements:
                    text = opt.text.strip()
                    if text:
                        options.append(text)
            else:
                # Ant Design Select - try to find dropdown menu
                # Check if dropdown is open
                try:
                    # Look for dropdown menu (could be in portal/overlay)
                    menu = element.find_element(By.CSS_SELECTOR, '.ant-select-dropdown, .rc-select-dropdown')
                    option_elements = menu.find_elements(By.CSS_SELECTOR, '.ant-select-item, .rc-select-item')
                    for opt in option_elements:
                        text = opt.text.strip()
                        if text and text not in options:
                            options.append(text)
                except:
                    # Dropdown not open, cannot get options without opening it
                    # Options will be retrieved when dropdown is opened in handler
                    pass
        except:
            pass
        
        return options

