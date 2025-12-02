"""
Configuration for Ant Design selectors
"""
from typing import Dict


class AntDesignSelectors:
    """Centralized selector configuration for Ant Design components"""
    
    # Button selectors
    BUTTON_BASE = "button.ant-btn, a.ant-btn"
    BUTTON_PRIMARY = "button.ant-btn-primary, a.ant-btn-primary"
    BUTTON_DEFAULT = "button.ant-btn-default, a.ant-btn-default"
    BUTTON_DASHED = "button.ant-btn-dashed, a.ant-btn-dashed"
    BUTTON_TEXT = "button.ant-btn-text, a.ant-btn-text"
    BUTTON_LINK = "button.ant-btn-link, a.ant-btn-link"
    BUTTON_DANGER = "button.ant-btn-dangerous, a.ant-btn-dangerous"
    
    # Button states
    BUTTON_DISABLED = ".ant-btn-disabled"
    BUTTON_LOADING = ".ant-btn-loading"
    
    # Button sizes
    BUTTON_LARGE = ".ant-btn-lg"
    BUTTON_SMALL = ".ant-btn-sm"
    
    # Button shapes
    BUTTON_ROUND = ".ant-btn-round"
    BUTTON_CIRCLE = ".ant-btn-circle"
    
    # Custom data attribute
    DATA_ATTR_ID = "[data-atr-id]"
    
    @staticmethod
    def get_button_selector_by_type(button_type: str) -> str:
        """
        Get CSS selector for button type
        
        Args:
            button_type: Type of button ('primary', 'default', 'dashed', 'text', 'link', 'danger')
            
        Returns:
            CSS selector string
        """
        selectors = {
            'primary': AntDesignSelectors.BUTTON_PRIMARY,
            'default': AntDesignSelectors.BUTTON_DEFAULT,
            'dashed': AntDesignSelectors.BUTTON_DASHED,
            'text': AntDesignSelectors.BUTTON_TEXT,
            'link': AntDesignSelectors.BUTTON_LINK,
            'danger': AntDesignSelectors.BUTTON_DANGER
        }
        return selectors.get(button_type, AntDesignSelectors.BUTTON_BASE)
    
    @staticmethod
    def get_button_by_data_attr(data_attr_id: str) -> str:
        """
        Get CSS selector for button by data-atr-id
        
        Args:
            data_attr_id: Value of data-atr-id attribute
            
        Returns:
            CSS selector string
        """
        return f'[data-atr-id="{data_attr_id}"]'




