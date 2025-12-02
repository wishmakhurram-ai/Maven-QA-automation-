"""
Element Context Manager - Stores and manages element information
Single Responsibility: Manage element context storage and retrieval
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from selenium.webdriver.remote.webelement import WebElement


@dataclass
class ElementInfo:
    """
    Data class to store element information
    """
    element: WebElement
    element_type: str  # 'button', 'input', 'dropdown', etc.
    application_type: Optional[str] = None  # Custom type from data-type attribute
    data_attr_id: Optional[str] = None  # Value from data-atr-id
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional identifying info


class ElementContext:
    """
    Class-based context manager for storing multiple elements
    Single Responsibility: Store and retrieve element information
    """
    
    def __init__(self):
        """
        Initialize the element context
        """
        self.elements: Dict[str, ElementInfo] = {}  # Dict[key, ElementInfo]
        self.current_element_key: Optional[str] = None
    
    def store_element(self, key: str, element_info: ElementInfo) -> None:
        """
        Store an element in the context
        
        Args:
            key: Unique key to identify the element (typically data-attr-id)
            element_info: ElementInfo object containing element details
        """
        self.elements[key] = element_info
        # Automatically set as current if no current element is set
        if self.current_element_key is None:
            self.current_element_key = key
        print(f"   >> Stored element in context with key: '{key}'")
        print(f"      Element type: {element_info.element_type}, "
              f"Application type: {element_info.application_type}, "
              f"Data-attr-id: {element_info.data_attr_id}")
    
    def get_element(self, key: str) -> Optional[ElementInfo]:
        """
        Retrieve an element from the context by key
        
        Args:
            key: Key of the element to retrieve
            
        Returns:
            ElementInfo if found, None otherwise
        """
        return self.elements.get(key)
    
    def set_current(self, key: str) -> bool:
        """
        Set the current element by key
        
        Args:
            key: Key of the element to set as current
            
        Returns:
            True if key exists and was set, False otherwise
        """
        if key in self.elements:
            self.current_element_key = key
            print(f"   >> Set current element to key: '{key}'")
            return True
        print(f"   >> Warning: Key '{key}' not found in context")
        return False
    
    def get_current(self) -> Optional[ElementInfo]:
        """
        Get the current element
        
        Returns:
            ElementInfo of current element, None if no current element set
        """
        if self.current_element_key:
            return self.elements.get(self.current_element_key)
        return None
    
    def clear(self) -> None:
        """
        Clear all stored elements and reset current element
        """
        self.elements.clear()
        self.current_element_key = None
        print(f"   >> Context cleared")
    
    def has_element(self, key: str) -> bool:
        """
        Check if an element exists in context
        
        Args:
            key: Key to check
            
        Returns:
            True if element exists, False otherwise
        """
        return key in self.elements
    
    def get_all_keys(self) -> list:
        """
        Get all keys stored in context
        
        Returns:
            List of all keys
        """
        return list(self.elements.keys())
    
    def get_element_count(self) -> int:
        """
        Get the number of elements stored in context
        
        Returns:
            Number of elements
        """
        return len(self.elements)



