"""
Pattern Discovery Utility - Automatically discovers data-attr-id patterns from the page
Single Responsibility: Discover and extract patterns like {component-name}--{element-role}--{short-content-hash}
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from typing import Dict, List, Optional, Set
import re


class PatternDiscovery:
    """
    Discovers data-attr-id patterns from the page automatically
    Extracts pattern structure: {component-name}--{element-role}--{short-content-hash}
    """
    
    def __init__(self, driver: webdriver):
        """
        Initialize Pattern Discovery
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self._cached_patterns: Optional[Dict[str, List[str]]] = None
    
    def clear_cache(self):
        """
        Clear the cached patterns
        Should be called when navigating to a new page
        """
        self._cached_patterns = None
    
    def discover_all_data_attr_ids(self, timeout: int = 1) -> Dict[str, List[str]]:
        """
        Discover all data-attr-id and data-atr-id values from the page
        Groups them by component type (input, button, dropdown, etc.)
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            Dictionary mapping component types to lists of data-attr-id values
            {
                'input': ['login-page--input--email', 'login-page--input--password'],
                'button': ['login-page--button--submit', 'login-page--button--cancel'],
                'dropdown': ['login-page--select--role'],
                ...
            }
        """
        if self._cached_patterns is not None:
            # Skip verbose output when using cached patterns (faster)
            return self._cached_patterns
        
        patterns = {
            'input': [],
            'button': [],
            'dropdown': [],
            'textarea': [],
            'switch': [],
            'generic': []
        }
        
        try:
            # Find all elements with data-attr-id or data-atr-id
            elements_with_attr = []
            
            # Try data-attr-id first
            try:
                elements_with_attr.extend(
                    self.driver.find_elements(By.CSS_SELECTOR, '[data-attr-id]')
                )
            except:
                pass
            
            # Try data-atr-id as fallback
            try:
                elements_with_attr.extend(
                    self.driver.find_elements(By.CSS_SELECTOR, '[data-atr-id]')
                )
            except:
                pass
            
            # Deduplicate by element
            seen_elements = set()
            unique_elements = []
            for elem in elements_with_attr:
                elem_id = id(elem)
                if elem_id not in seen_elements:
                    seen_elements.add(elem_id)
                    unique_elements.append(elem)
            
            # Extract data-attr-id values and categorize by element type
            for element in unique_elements:
                try:
                    # Get data-attr-id value
                    data_attr_id = element.get_attribute('data-attr-id')
                    if not data_attr_id:
                        data_attr_id = element.get_attribute('data-atr-id')
                    
                    if not data_attr_id:
                        continue
                    
                    # Determine element type
                    tag_name = element.tag_name.lower()
                    class_attr = element.get_attribute('class') or ''
                    
                    element_type = self._determine_element_type(tag_name, class_attr)
                    
                    # Add to patterns
                    if element_type in patterns:
                        if data_attr_id not in patterns[element_type]:
                            patterns[element_type].append(data_attr_id)
                    else:
                        if data_attr_id not in patterns['generic']:
                            patterns['generic'].append(data_attr_id)
                            
                except Exception as e:
                    continue
            
            self._cached_patterns = patterns

            # Skip verbose output for speed - only show when data-attr-id is actually used
            return patterns
            
        except Exception as e:
            print(f"Error discovering patterns: {str(e)}")
            return patterns
    
    def discover_pattern_structure(self) -> Dict[str, Dict[str, str]]:
        """
        Discover the pattern structure from existing data-attr-id values
        Extracts: {component-name}--{element-role}--{short-content-hash}
        
        Returns:
            Dictionary with pattern information:
            {
                'pattern': '{component-name}--{element-role}--{short-content-hash}',
                'component_name': 'login-page',
                'element_roles': ['input', 'button', 'select'],
                'examples': {
                    'input': 'login-page--input--email',
                    'button': 'login-page--button--submit'
                }
            }
        """
        all_patterns = self.discover_all_data_attr_ids()
        
        # Analyze patterns to extract structure
        pattern_structure = {
            'pattern': '{component-name}--{element-role}--{short-content-hash}',
            'component_name': None,
            'element_roles': set(),
            'examples': {}
        }
        
        # Find common component name prefix
        all_values = []
        for component_type, values in all_patterns.items():
            all_values.extend(values)
        
        if not all_values:
            return pattern_structure
        
        # Extract component name from first pattern
        # Example: "login-page--input--email" -> component_name = "login-page"
        first_pattern = all_values[0]
        parts = first_pattern.split('--')
        if len(parts) >= 2:
            pattern_structure['component_name'] = parts[0]
        
        # Extract element roles
        for value in all_values:
            parts = value.split('--')
            if len(parts) >= 2:
                pattern_structure['element_roles'].add(parts[1])
                # Store example
                if parts[1] not in pattern_structure['examples']:
                    pattern_structure['examples'][parts[1]] = value
        
        # Convert set to list
        pattern_structure['element_roles'] = list(pattern_structure['element_roles'])
        
        return pattern_structure
    
    def find_matching_data_attr_id(self, field_name: str, element_type: str = 'input') -> Optional[str]:
        """
        Find a matching data-attr-id for a given field name by analyzing discovered patterns
        For buttons, also checks the button's text content
        
        Args:
            field_name: Name of the field (e.g., "email", "password", "Log In")
            element_type: Type of element ('input', 'button', 'dropdown', etc.)
            
        Returns:
            Matching data-attr-id value if found, None otherwise
        """
        # Reduced verbosity for speed - only show when found
        all_patterns = self.discover_all_data_attr_ids()
        
        if element_type not in all_patterns:
            element_type = 'generic'
        
        candidates = all_patterns.get(element_type, [])
        
        # Normalize field name for matching
        normalized_field = field_name.lower().replace('_', '-').replace(' ', '-')
        normalized_text = field_name.lower().strip()
        
        # Try exact match first
        for candidate in candidates:
            # Check if candidate ends with the field name
            if candidate.endswith(f"--{normalized_field}") or candidate.endswith(f"-{normalized_field}"):
                # Get current step name from conftest
                try:
                    import sys
                    if 'conftest' in sys.modules:
                        from conftest import _current_step_name
                        step_name = _current_step_name or "Unknown Step"
                        print(f"   >> STEP: {step_name[:45]:<45} | data-attr-id: '{candidate}'")
                    else:
                        print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{candidate}'")
                except:
                    print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{candidate}'")
                return candidate
            
            # Check if candidate contains the field name
            if normalized_field in candidate.lower():
                try:
                    import sys
                    if 'conftest' in sys.modules:
                        from conftest import _current_step_name
                        step_name = _current_step_name or "Unknown Step"
                        print(f"   >> STEP: {step_name[:45]:<45} | data-attr-id: '{candidate}'")
                    else:
                        print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{candidate}'")
                except:
                    print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{candidate}'")
                return candidate
        
        # Try fuzzy matching - check if any part of the pattern matches
        for candidate in candidates:
            parts = candidate.split('--')
            if len(parts) >= 3:
                # Check the last part (short-content-hash) which might contain field name
                if normalized_field in parts[-1].lower():
                    try:
                        import sys
                        if 'conftest' in sys.modules:
                            from conftest import _current_step_name
                            step_name = _current_step_name or "Unknown Step"
                            print(f"   >> STEP: {step_name[:45]:<45} | data-attr-id: '{candidate}'")
                        else:
                            print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{candidate}'")
                    except:
                        print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{candidate}'")
                    return candidate
        
        # For buttons and links, also check the element's text content
        if element_type in ['button', 'link']:
            try:
                from selenium.webdriver.common.by import By
                for candidate in candidates:
                    try:
                        # Find element by data-attr-id (try both attribute names)
                        element = None
                        try:
                            element = self.driver.find_element(By.CSS_SELECTOR, f'[data-attr-id="{candidate}"]')
                        except:
                            try:
                                element = self.driver.find_element(By.CSS_SELECTOR, f'[data-atr-id="{candidate}"]')
                            except:
                                pass
                        
                        if element:
                            # Check if element text matches
                            element_text = element.text.strip().lower()
                            if normalized_text in element_text or element_text in normalized_text:
                                try:
                                    import sys
                                    if 'conftest' in sys.modules:
                                        from conftest import _current_step_name
                                        step_name = _current_step_name or "Unknown Step"
                                        print(f"   >> STEP: {step_name[:45]:<45} | data-attr-id: '{candidate}'")
                                    else:
                                        print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{candidate}'")
                                except:
                                    print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{candidate}'")
                                return candidate
                            
                            # Also check for partial matches (e.g., "forgot password" matches "forgot-password")
                            element_words = element_text.split()
                            field_words = normalized_text.split()
                            if any(fw in element_text for fw in field_words) or any(ew in normalized_text for ew in element_words):
                                try:
                                    import sys
                                    if 'conftest' in sys.modules:
                                        from conftest import _current_step_name
                                        step_name = _current_step_name or "Unknown Step"
                                        print(f"   >> STEP: {step_name[:45]:<45} | data-attr-id: '{candidate}'")
                                    else:
                                        print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{candidate}'")
                                except:
                                    print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{candidate}'")
                                return candidate
                            
                            # For links, also check href attribute
                            if element_type == 'link':
                                try:
                                    href = element.get_attribute('href') or ''
                                    if normalized_text.replace('-', ' ') in href.lower() or 'forgot' in href.lower() or 'password' in href.lower():
                                        try:
                                            import sys
                                            if 'conftest' in sys.modules:
                                                from conftest import _current_step_name
                                                step_name = _current_step_name or "Unknown Step"
                                                print(f"   >> STEP: {step_name[:45]:<45} | data-attr-id: '{candidate}'")
                                            else:
                                                print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{candidate}'")
                                        except:
                                            print(f"   >> STEP: {'Unknown':<45} | data-attr-id: '{candidate}'")
                                        return candidate
                                except:
                                    pass
                    except:
                        continue
            except:
                pass
        
        # Only print if no match found (reduced verbosity for speed)
        return None
    
    def generate_candidates(self, field_name: str, element_type: str = 'input') -> List[str]:
        """
        Generate candidate data-attr-id values based on discovered pattern structure
        
        Args:
            field_name: Name of the field (e.g., "email", "password")
            element_type: Type of element ('input', 'button', 'dropdown', etc.)
            
        Returns:
            List of candidate data-attr-id values to try
        """
        pattern_structure = self.discover_pattern_structure()
        candidates = []
        
        normalized_field = field_name.lower().replace('_', '-').replace(' ', '-')
        component_name = pattern_structure.get('component_name')
        element_role = element_type  # Use element_type as role
        
        # If we discovered a pattern structure, use it
        if component_name:
            # Pattern: {component-name}--{element-role}--{short-content-hash}
            candidates.append(f"{component_name}--{element_role}--{normalized_field}")
            candidates.append(f"{component_name}--{element_role}-{normalized_field}")
        
        # Also try with discovered examples
        examples = pattern_structure.get('examples', {})
        if element_role in examples:
            example = examples[element_role]
            parts = example.split('--')
            if len(parts) >= 2:
                # Replace the last part with field name
                base_pattern = '--'.join(parts[:-1])
                candidates.append(f"{base_pattern}--{normalized_field}")
        
        # Add generic candidates
        candidates.extend([
            f"{normalized_field}-{element_role}",
            f"{element_role}-{normalized_field}",
            normalized_field,
            field_name.lower()
        ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)
        
        return unique_candidates
    
    @staticmethod
    def _determine_element_type(tag_name: str, class_attr: str) -> str:
        """
        Determine element type from tag name and classes
        
        Args:
            tag_name: HTML tag name
            class_attr: Class attribute value
            
        Returns:
            Element type string
        """
        # Check for input
        if tag_name == 'input':
            return 'input'
        
        # Check for textarea
        if tag_name == 'textarea':
            return 'textarea'
        
        # Check for button
        if tag_name in ['button', 'a']:
            if 'ant-btn' in class_attr or 'btn' in class_attr.lower():
                return 'button'
        
        # Check for select/dropdown
        if tag_name == 'select' or 'ant-select' in class_attr:
            return 'dropdown'
        
        # Check for switch
        if 'ant-switch' in class_attr or 'role="switch"' in class_attr:
            return 'switch'
        
        return 'generic'


