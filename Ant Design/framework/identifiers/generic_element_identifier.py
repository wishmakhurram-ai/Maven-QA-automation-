"""
Generic Element Identifier - Reads custom attributes and identifies elements
Single Responsibility: Identify elements by reading custom attributes (data-attr-id, data-type)
"""
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Dict, Any, Optional


class GenericElementIdentifier:
    """
    Generic identifier that reads custom attributes and determines element properties
    Single Responsibility: Extract element metadata from custom attributes
    """
    
    @staticmethod
    def identify_element(element: WebElement) -> Dict[str, Any]:
        """
        Identify an element by reading custom attributes and properties
        
        Args:
            element: WebElement to identify
            
        Returns:
            Dictionary containing:
            {
                'element_type': 'button'|'input'|'dropdown'|'generic',
                'application_type': str|None,  # From data-type attribute
                'data_attr_id': str|None,      # From data-atr-id attribute
                'tag_name': str,
                'text': str,
                'classes': list,
                'attributes': dict,
                'metadata': dict  # Additional identifying info
            }
        """
        element_info = {
            'element_type': 'generic',
            'application_type': None,
            'data_attr_id': None,
            'tag_name': '',
            'text': '',
            'classes': [],
            'attributes': {},
            'metadata': {}
        }
        
        try:
            # Get tag name
            element_info['tag_name'] = element.tag_name.lower()
            
            # Determine element_type based on tag and classes
            element_info['element_type'] = GenericElementIdentifier._determine_element_type(
                element, element_info['tag_name']
            )
            
            # Read custom data attributes
            element_info['data_attr_id'] = element.get_attribute('data-atr-id')
            element_info['application_type'] = element.get_attribute('data-type')
            
            # Get text content
            try:
                element_info['text'] = element.text.strip()
            except:
                element_info['text'] = ''
            
            # Get classes
            class_attr = element.get_attribute('class') or ''
            element_info['classes'] = class_attr.split() if class_attr else []
            
            # Get all attributes
            try:
                # Get common attributes
                element_info['attributes'] = {
                    'id': element.get_attribute('id'),
                    'name': element.get_attribute('name'),
                    'type': element.get_attribute('type'),
                    'value': element.get_attribute('value'),
                    'href': element.get_attribute('href'),
                    'disabled': element.get_attribute('disabled'),
                    'placeholder': element.get_attribute('placeholder'),
                    'role': element.get_attribute('role'),
                    'aria-label': element.get_attribute('aria-label')
                }
            except:
                element_info['attributes'] = {}
            
            # Build metadata for element identification
            element_info['metadata'] = {
                'text': element_info['text'],
                'classes': element_info['classes'],
                'tag_name': element_info['tag_name'],
                'has_data_attr_id': element_info['data_attr_id'] is not None,
                'has_application_type': element_info['application_type'] is not None,
                'id': element_info['attributes'].get('id'),
                'name': element_info['attributes'].get('name')
            }
            
        except Exception as e:
            print(f"Error identifying element: {str(e)}")
        
        return element_info
    
    @staticmethod
    def _determine_element_type(element: WebElement, tag_name: str) -> str:
        """
        Determine the element type based on tag name and classes
        
        Args:
            element: WebElement to analyze
            tag_name: Tag name of the element
            
        Returns:
            Element type string ('button', 'input', 'dropdown', 'generic')
        """
        # Check for button
        if tag_name in ['button', 'a']:
            class_attr = element.get_attribute('class') or ''
            if 'ant-btn' in class_attr or 'btn' in class_attr.lower():
                return 'button'
            if tag_name == 'a' and 'ant-btn' not in class_attr:
                return 'link'
            return 'button' if tag_name == 'button' else 'link'
        
        # Check for input
        if tag_name == 'input':
            input_type = element.get_attribute('type') or ''
            if input_type in ['text', 'password', 'email', 'number', 'tel', 'url', 'search']:
                return 'input'
            elif input_type in ['checkbox', 'radio']:
                return 'checkbox' if input_type == 'checkbox' else 'radio'
            return 'input'
        
        # Check for select (dropdown)
        if tag_name == 'select':
            return 'dropdown'
        
        # Check for textarea
        if tag_name == 'textarea':
            return 'textarea'
        
        # Check for Ant Design Select component (div with ant-select class)
        class_attr = element.get_attribute('class') or ''
        if 'ant-select' in class_attr:
            return 'dropdown'
        
        # Default to generic
        return 'generic'



