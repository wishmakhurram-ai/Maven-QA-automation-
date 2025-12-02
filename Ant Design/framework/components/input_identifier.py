"""
Input Identifier - Handles analyzing and identifying Ant Design input properties
Single Responsibility: Analyze input elements and extract their properties
"""
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Dict, Optional
from framework.identifiers.generic_element_identifier import GenericElementIdentifier


class InputIdentifier:
    """
    Handles identifying and analyzing Ant Design input field properties
    Single Responsibility: Extract input type, size, state, and other properties
    """
    
    # Ant Design input size classes
    SIZE_CLASSES = {
        'large': 'ant-input-lg',
        'small': 'ant-input-sm'
    }
    
    # Ant Design input type patterns
    INPUT_TYPES = {
        'text': 'text',
        'password': 'password',
        'number': 'number',
        'email': 'email',
        'url': 'url',
        'search': 'search',
        'tel': 'tel',
        'textarea': 'textarea'
    }
    
    @staticmethod
    def identify_input_type(element: WebElement) -> Dict[str, any]:
        """
        Automatically identify the type and properties of an Ant Design input field
        PRIORITY: data-attr-id is checked first to determine field type
        Integrates with GenericElementIdentifier to read custom attributes
        
        Args:
            element: WebElement representing the input
            
        Returns:
            Dictionary containing input properties:
            {
                'input_type': 'text'|'password'|'number'|'email'|'url'|'search'|'textarea',
                'size': 'large'|'middle'|'small',
                'disabled': bool,
                'readonly': bool,
                'clearable': bool,
                'has_prefix': bool,
                'has_suffix': bool,
                'required': bool,
                'placeholder': str,
                'label': str,
                'data_attr_id': str|None,
                'application_type': str|None,
                'metadata': dict
            }
        """
        # First, get generic element information
        generic_info = GenericElementIdentifier.identify_element(element)
        
        input_info = {
            'input_type': 'text',
            'size': 'middle',
            'disabled': False,
            'readonly': False,
            'clearable': False,
            'has_prefix': False,
            'has_suffix': False,
            'required': False,
            'placeholder': '',
            'label': '',
            'data_attr_id': generic_info.get('data_attr_id'),
            'application_type': generic_info.get('application_type'),
            'metadata': generic_info.get('metadata', {})
        }
        
        try:
            tag_name = element.tag_name.lower()
            
            # PRIORITY 1: Determine input type from data-attr-id (if it contains type info)
            data_attr_id = input_info['data_attr_id']
            if data_attr_id:
                # Check if data-attr-id contains type information (e.g., "password-input", "email-field")
                data_attr_lower = data_attr_id.lower()
                if 'password' in data_attr_lower:
                    input_info['input_type'] = 'password'
                elif 'email' in data_attr_lower:
                    input_info['input_type'] = 'email'
                elif 'number' in data_attr_lower or 'num' in data_attr_lower:
                    input_info['input_type'] = 'number'
                elif 'phone' in data_attr_lower or 'tel' in data_attr_lower:
                    input_info['input_type'] = 'tel'
                elif 'url' in data_attr_lower or 'link' in data_attr_lower:
                    input_info['input_type'] = 'url'
                elif 'search' in data_attr_lower:
                    input_info['input_type'] = 'search'
                elif 'textarea' in data_attr_lower or 'text-area' in data_attr_lower:
                    input_info['input_type'] = 'textarea'
                elif 'text' in data_attr_lower:
                    input_info['input_type'] = 'text'
            
            # PRIORITY 2: If type not determined from data-attr-id, use tag and type attribute
            if input_info['input_type'] == 'text' and not data_attr_id:
                if tag_name == 'textarea':
                    input_info['input_type'] = 'textarea'
                else:
                    input_type_attr = element.get_attribute('type') or 'text'
                    input_info['input_type'] = input_type_attr.lower()
            
            # Get class attribute
            class_attr = element.get_attribute('class') or ''
            classes = class_attr.split()
            
            # Identify size
            for size, size_class in InputIdentifier.SIZE_CLASSES.items():
                if size_class in classes:
                    input_info['size'] = size
                    break
            
            # Check if disabled
            input_info['disabled'] = (
                'ant-input-disabled' in classes or 
                element.get_attribute('disabled') is not None or
                element.get_attribute('aria-disabled') == 'true'
            )
            
            # Check if readonly
            input_info['readonly'] = (
                element.get_attribute('readonly') is not None or
                element.get_attribute('readOnly') is not None
            )
            
            # Check if clearable (Ant Design allowClear)
            # Look for clear icon in parent container
            try:
                parent = element.find_element(By.XPATH, "./ancestor::span[contains(@class, 'ant-input-affix-wrapper')]")
                clear_icons = parent.find_elements(By.CSS_SELECTOR, '.ant-input-clear-icon, .anticon-close-circle')
                input_info['clearable'] = len(clear_icons) > 0
            except:
                input_info['clearable'] = False
            
            # Check for prefix/suffix icons
            try:
                parent = element.find_element(By.XPATH, "./ancestor::span[contains(@class, 'ant-input-affix-wrapper')]")
                prefix_icons = parent.find_elements(By.CSS_SELECTOR, '.ant-input-prefix .anticon')
                suffix_icons = parent.find_elements(By.CSS_SELECTOR, '.ant-input-suffix .anticon')
                input_info['has_prefix'] = len(prefix_icons) > 0
                input_info['has_suffix'] = len(suffix_icons) > 0
            except:
                input_info['has_prefix'] = False
                input_info['has_suffix'] = False
            
            # Check for associated action button (search, submit, etc.)
            # Excludes clear buttons which are handled separately
            input_info['has_action_button'] = False
            input_info['action_button_type'] = None
            input_info['action_button_text'] = None
            input_info['action_button_element'] = None
            
            try:
                associated_button = InputIdentifier._find_associated_button(element)
                if associated_button:
                    input_info['has_action_button'] = True
                    # Try to determine button type
                    button_class = associated_button.get_attribute('class') or ''
                    button_text = associated_button.text.strip() if associated_button.text else ''
                    
                    if 'ant-btn-primary' in button_class:
                        input_info['action_button_type'] = 'primary'
                    elif 'ant-btn' in button_class:
                        input_info['action_button_type'] = 'button'
                    else:
                        input_info['action_button_type'] = 'generic'
                    
                    input_info['action_button_text'] = button_text
                    input_info['action_button_element'] = associated_button
                    input_info['metadata']['associated_button'] = {
                        'element': associated_button,
                        'type': input_info['action_button_type'],
                        'text': button_text,
                        'disabled': associated_button.get_attribute('disabled') is not None
                    }
            except Exception as e:
                # Silently fail - not all inputs have associated buttons
                pass
            
            # Check if required
            input_info['required'] = (
                element.get_attribute('required') is not None or
                element.get_attribute('aria-required') == 'true' or
                'ant-input-required' in classes
            )
            
            # Get placeholder
            input_info['placeholder'] = element.get_attribute('placeholder') or ''
            
            # Get label (try multiple methods)
            label_text = ''
            try:
                # Method 1: aria-label
                label_text = element.get_attribute('aria-label') or ''
                
                # Method 2: Associated label element
                if not label_text:
                    input_id = element.get_attribute('id')
                    if input_id:
                        label_elem = element.find_element(By.XPATH, f"//label[@for='{input_id}']")
                        if label_elem:
                            label_text = label_elem.text.strip()
                
                # Method 3: Parent label
                if not label_text:
                    try:
                        parent_label = element.find_element(By.XPATH, "./ancestor::label")
                        label_text = parent_label.text.strip()
                    except:
                        pass
                
                # Method 4: Nearby label (Ant Design Form.Item)
                if not label_text:
                    try:
                        form_item = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'ant-form-item')]")
                        label_elem = form_item.find_element(By.CSS_SELECTOR, '.ant-form-item-label label')
                        if label_elem:
                            label_text = label_elem.text.strip()
                    except:
                        pass
            except:
                pass
            
            input_info['label'] = label_text
            
            # Get current value
            try:
                value = element.get_attribute('value') or ''
                input_info['metadata']['value'] = value
            except:
                input_info['metadata']['value'] = ''
            
            # Get validation state (Ant Design form validation)
            validation_state = 'none'
            try:
                parent = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'ant-form-item')]")
                if 'ant-form-item-has-error' in parent.get_attribute('class') or '':
                    validation_state = 'error'
                elif 'ant-form-item-has-warning' in parent.get_attribute('class') or '':
                    validation_state = 'warning'
                elif 'ant-form-item-has-success' in parent.get_attribute('class') or '':
                    validation_state = 'success'
            except:
                pass
            
            input_info['metadata']['validation_state'] = validation_state
            
        except Exception as e:
            print(f"Error identifying input type: {str(e)}")
        
        return input_info
    
    @staticmethod
    def _find_associated_button(element: WebElement) -> Optional[WebElement]:
        """
        Find an associated action button (search, submit, etc.) for an input field
        Looks in ant-input-suffix and ant-input-prefix containers
        Excludes clear buttons which are handled separately
        
        Args:
            element: Input WebElement
            
        Returns:
            WebElement of associated button if found, None otherwise
        """
        try:
            # Find parent ant-input-affix-wrapper container
            parent = element.find_element(By.XPATH, "./ancestor::span[contains(@class, 'ant-input-affix-wrapper')]")
            
            # Strategy 1: Look for buttons in ant-input-suffix (most common for search buttons)
            try:
                suffix_container = parent.find_element(By.CSS_SELECTOR, '.ant-input-suffix')
                # Find buttons but exclude clear buttons
                buttons = suffix_container.find_elements(By.CSS_SELECTOR, 
                    'button:not(.ant-input-clear-icon):not(.anticon-close-circle), '
                    'a.ant-btn, button.ant-btn')
                
                for button in buttons:
                    # Skip disabled buttons and clear buttons
                    if button.get_attribute('disabled') is None:
                        clear_classes = button.get_attribute('class') or ''
                        if 'ant-input-clear-icon' not in clear_classes and 'anticon-close-circle' not in clear_classes:
                            return button
            except:
                pass
            
            # Strategy 2: Look for buttons in ant-input-prefix
            try:
                prefix_container = parent.find_element(By.CSS_SELECTOR, '.ant-input-prefix')
                buttons = prefix_container.find_elements(By.CSS_SELECTOR, 
                    'button:not(.ant-input-clear-icon), a.ant-btn, button.ant-btn')
                
                for button in buttons:
                    if button.get_attribute('disabled') is None:
                        return button
            except:
                pass
            
            # Strategy 3: Look for buttons as siblings within the affix wrapper
            try:
                # Find buttons that are direct children or siblings of the input within the wrapper
                buttons = parent.find_elements(By.CSS_SELECTOR, 
                    'button.ant-btn:not(.ant-input-clear-icon), a.ant-btn')
                
                for button in buttons:
                    if button.get_attribute('disabled') is None:
                        clear_classes = button.get_attribute('class') or ''
                        if 'ant-input-clear-icon' not in clear_classes:
                            return button
            except:
                pass
            
        except Exception:
            # Input may not be in an affix wrapper, or no button found
            pass
        
        return None

