"""
Button Identifier - Handles analyzing and identifying button properties
Single Responsibility: Analyze button elements and extract their properties
"""
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Dict, Optional
from framework.identifiers.generic_element_identifier import GenericElementIdentifier


class ButtonIdentifier:
    """
    Handles identifying and analyzing Ant Design button properties
    Single Responsibility: Extract button type, size, state, and other properties
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
    
    # Button size classes
    SIZE_CLASSES = {
        'large': 'ant-btn-lg',
        'small': 'ant-btn-sm'
    }
    
    @staticmethod
    def identify_button_type(element: WebElement) -> Dict[str, any]:
        """
        Automatically identify the type and properties of an Ant Design button
        Integrates with GenericElementIdentifier to read custom attributes
        
        Args:
            element: WebElement representing the button
            
        Returns:
            Dictionary containing button properties:
            {
                'type': 'primary'|'default'|'dashed'|'text'|'link'|'danger',
                'size': 'large'|'middle'|'small'|None,
                'disabled': bool,
                'loading': bool,
                'text': str,
                'data_attr_id': str|None,
                'application_type': str|None,  # From data-type attribute
                'icon': bool,
                'shape': 'default'|'round'|'circle'|None,
                'metadata': dict  # Additional info from generic identifier
            }
        """
        # First, get generic element information
        generic_info = GenericElementIdentifier.identify_element(element)
        
        button_info = {
            'type': 'default',
            'size': None,
            'disabled': False,
            'loading': False,
            'text': '',
            'data_attr_id': generic_info.get('data_attr_id'),
            'application_type': generic_info.get('application_type'),
            'icon': False,
            'shape': None,
            'metadata': generic_info.get('metadata', {})
        }
        
        try:
            # Get class attribute
            class_attr = element.get_attribute('class') or ''
            classes = class_attr.split()
            
            # Identify button type
            for btn_type, btn_class in ButtonIdentifier.BUTTON_CLASSES.items():
                if btn_class in classes:
                    button_info['type'] = btn_type
                    break
            
            # Identify size
            for size, size_class in ButtonIdentifier.SIZE_CLASSES.items():
                if size_class in classes:
                    button_info['size'] = size
                    break
            if not button_info['size']:
                button_info['size'] = 'middle'  # Default size
            
            # Check if disabled
            button_info['disabled'] = 'ant-btn-disabled' in classes or element.get_attribute('disabled') is not None
            
            # Check if loading
            button_info['loading'] = 'ant-btn-loading' in classes
            
            # Get button text (use from generic_info if available, otherwise get directly)
            button_info['text'] = generic_info.get('text', '')
            if not button_info['text']:
                try:
                    button_info['text'] = element.text.strip()
                except:
                    button_info['text'] = ''
            
            # Check for icon
            button_info['icon'] = 'anticon' in class_attr or len(element.find_elements(By.CLASS_NAME, 'anticon')) > 0
            
            # Check shape
            if 'ant-btn-round' in classes:
                button_info['shape'] = 'round'
            elif 'ant-btn-circle' in classes:
                button_info['shape'] = 'circle'
            else:
                button_info['shape'] = 'default'
                
        except Exception as e:
            print(f"Error identifying button type: {str(e)}")
        
        return button_info


