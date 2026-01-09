"""
Generic Ant Design TreeSelect Handler
Handles TreeSelect interactions (selecting nodes, expanding, searching, etc.)
Uses TreeSelectLocator for finding TreeSelects and TreeSelectIdentifier for analyzing them
Uses ElementContext for context-driven interactions
"""
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, NoSuchElementException
from typing import Optional, Dict, List
from framework.base.base_page import BasePage
from framework.components.treeselect_locator import TreeSelectLocator
from framework.components.treeselect_identifier import TreeSelectIdentifier
from framework.context.element_context import ElementContext, ElementInfo
import time


class TreeSelectHandler(BasePage):
    """
    Generic handler for Ant Design TreeSelect interactions
    Single Responsibility: Handle TreeSelect interactions (selecting, expanding, searching, etc.)
    Uses TreeSelectLocator to find TreeSelects and TreeSelectIdentifier to analyze them
    """
    
    def __init__(self, driver: webdriver, context: Optional[ElementContext] = None):
        """
        Initialize TreeSelect Handler
        
        Args:
            driver: Selenium WebDriver instance
            context: Optional ElementContext for context-driven interactions
        """
        super().__init__(driver)
        self.locator = TreeSelectLocator(driver)
        self.identifier = TreeSelectIdentifier()
        self.context = context
    
    def identify_and_store(self, identifier: str, identifier_type: str = 'data_attr_id',
                          timeout: int = 10, context_key: Optional[str] = None) -> bool:
        """
        Identify a TreeSelect and store it in context
        
        Args:
            identifier: Value to identify the TreeSelect (data-attr-id, label, or position)
            identifier_type: Type of identifier ('data_attr_id', 'label', 'position', 'auto')
            timeout: Maximum wait time in seconds
            context_key: Optional key to use in context
            
        Returns:
            True if TreeSelect was identified and stored, False otherwise
        """
        if not self.context:
            print("Context not available. Cannot store element.")
            return False
        
        element = None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_treeselect_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'label':
                element = self.locator.find_treeselect_by_label(identifier, exact_match=False, timeout=timeout, context=self.context)
            elif identifier_type == 'position':
                position = int(identifier) if identifier.isdigit() else 1
                element = self.locator.find_treeselect_by_position(position, timeout=timeout, context=self.context)
            elif identifier_type == 'auto':
                # PRIORITY ORDER: data-attr-id -> label -> position
                element = self.locator.find_treeselect_by_data_attr(identifier, timeout=3, context=self.context)
                if not element:
                    element = self.locator.find_treeselect_by_label(identifier, exact_match=False, timeout=5, context=self.context)
                if not element:
                    if identifier.isdigit():
                        position = int(identifier)
                        element = self.locator.find_treeselect_by_position(position, timeout=5, context=self.context)
            
            if element:
                if context_key and context_key != identifier:
                    element_info = self.context.get_element(identifier) or self.context.get_current()
                    if element_info:
                        self.context.store_element(context_key, element_info)
                print(f"TreeSelect identified and stored in context: {identifier}")
                return True
            else:
                print(f"TreeSelect not found with identifier: {identifier} (type: {identifier_type})")
                return False
                
        except Exception as e:
            print(f"Error identifying TreeSelect: {str(e)}")
            return False
    
    def open_dropdown(self, identifier: str, identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Open TreeSelect dropdown
        
        Args:
            identifier: Value to identify the TreeSelect
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            True if dropdown was opened, False otherwise
        """
        element = self._find_treeselect(identifier, identifier_type, timeout)
        if not element:
            return False
        
        try:
            # Check if already open
            if self._is_dropdown_open(element):
                return True
            
            # Click on the TreeSelect to open dropdown
            selector = element.find_element(By.CSS_SELECTOR, '.ant-select-selector, .ant-select-selection')
            selector.click()
            
            # Wait for dropdown to appear
            wait = WebDriverWait(self.driver, timeout)
            wait.until(lambda d: self._is_dropdown_open(element))
            
            # Small wait for animation
            time.sleep(0.2)
            
            print(f"TreeSelect dropdown opened successfully")
            return True
        except Exception as e:
            print(f"Error opening TreeSelect dropdown: {str(e)}")
            return False
    
    def close_dropdown(self, identifier: str, identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Close TreeSelect dropdown
        
        Args:
            identifier: Value to identify the TreeSelect
            identifier_type: Type of identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            True if dropdown was closed, False otherwise
        """
        element = self._find_treeselect(identifier, identifier_type, timeout)
        if not element:
            return False
        
        try:
            # Check if already closed
            if not self._is_dropdown_open(element):
                return True
            
            # Press Escape key or click outside
            element.send_keys(Keys.ESCAPE)
            time.sleep(0.2)
            
            # Verify closed
            if not self._is_dropdown_open(element):
                print(f"TreeSelect dropdown closed successfully")
                return True
            else:
                # Try clicking outside
                self.execute_js("document.body.click();")
                time.sleep(0.2)
                return not self._is_dropdown_open(element)
        except Exception as e:
            print(f"Error closing TreeSelect dropdown: {str(e)}")
            return False
    
    def select_node(self, node_identifier: str, treeselect_identifier: str,
                   treeselect_identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Select a tree node by title, value, or path
        
        Args:
            node_identifier: Node title, value, or path (e.g., "Fruits" or "Parent > Child")
            treeselect_identifier: Value to identify the TreeSelect
            treeselect_identifier_type: Type of identifier for TreeSelect
            timeout: Maximum wait time in seconds
            
        Returns:
            True if node was selected, False otherwise
        """
        element = self._find_treeselect(treeselect_identifier, treeselect_identifier_type, timeout)
        if not element:
            return False
        
        try:
            # Open dropdown if not open
            if not self._is_dropdown_open(element):
                self.open_dropdown(treeselect_identifier, treeselect_identifier_type, timeout)
            
            # Wait for tree to be visible
            wait = WebDriverWait(self.driver, timeout)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-select-dropdown:not([style*="display: none"])')))
            
            # Find and click the node
            node_found = False
            
            # Try path-based selection (e.g., "Parent > Child > Grandchild")
            if '>' in node_identifier:
                node_found = self._select_node_by_path(dropdown, node_identifier, timeout)
            else:
                # Try exact title match
                node_found = self._select_node_by_title(dropdown, node_identifier, exact_match=True, timeout=timeout)
                
                # Try partial match if exact failed
                if not node_found:
                    node_found = self._select_node_by_title(dropdown, node_identifier, exact_match=False, timeout=timeout)
            
            if node_found:
                # Wait for selection to complete
                time.sleep(0.3)
                print(f"Node '{node_identifier}' selected successfully")
                return True
            else:
                print(f"Node '{node_identifier}' not found in TreeSelect")
                return False
                
        except Exception as e:
            print(f"Error selecting node: {str(e)}")
            return False
    
    def select_multiple_nodes(self, node_identifiers: List[str], treeselect_identifier: str,
                             treeselect_identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Select multiple tree nodes
        
        Args:
            node_identifiers: List of node titles, values, or paths
            treeselect_identifier: Value to identify the TreeSelect
            treeselect_identifier_type: Type of identifier for TreeSelect
            timeout: Maximum wait time in seconds
            
        Returns:
            True if all nodes were selected, False otherwise
        """
        element = self._find_treeselect(treeselect_identifier, treeselect_identifier_type, timeout)
        if not element:
            return False
        
        # Check if TreeSelect supports multiple selection
        treeselect_info = self.identifier.identify_treeselect_type(element)
        if not treeselect_info.get('multiple', False):
            print("TreeSelect does not support multiple selection")
            return False
        
        try:
            # Open dropdown if not open
            if not self._is_dropdown_open(element):
                self.open_dropdown(treeselect_identifier, treeselect_identifier_type, timeout)
            
            # Wait for tree to be visible
            wait = WebDriverWait(self.driver, timeout)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-select-dropdown:not([style*="display: none"])')))
            
            # Select each node
            all_selected = True
            for node_id in node_identifiers:
                if '>' in node_id:
                    selected = self._select_node_by_path(dropdown, node_id, timeout)
                else:
                    selected = self._select_node_by_title(dropdown, node_id, exact_match=False, timeout=timeout)
                
                if not selected:
                    print(f"Failed to select node: {node_id}")
                    all_selected = False
                else:
                    time.sleep(0.2)  # Small delay between selections
            
            if all_selected:
                print(f"All {len(node_identifiers)} nodes selected successfully")
            return all_selected
                
        except Exception as e:
            print(f"Error selecting multiple nodes: {str(e)}")
            return False
    
    def expand_node(self, node_identifier: str, treeselect_identifier: str,
                   treeselect_identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Expand a tree node
        
        Args:
            node_identifier: Node title, value, or path
            treeselect_identifier: Value to identify the TreeSelect
            treeselect_identifier_type: Type of identifier for TreeSelect
            timeout: Maximum wait time in seconds
            
        Returns:
            True if node was expanded, False otherwise
        """
        element = self._find_treeselect(treeselect_identifier, treeselect_identifier_type, timeout)
        if not element:
            return False
        
        try:
            # Open dropdown if not open
            if not self._is_dropdown_open(element):
                self.open_dropdown(treeselect_identifier, treeselect_identifier_type, timeout)
            
            # Wait for tree to be visible
            wait = WebDriverWait(self.driver, timeout)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-select-dropdown:not([style*="display: none"])')))
            
            # Find the node
            node = self._find_node_element(dropdown, node_identifier)
            if not node:
                print(f"Node '{node_identifier}' not found")
                return False
            
            # Check if already expanded
            if 'ant-tree-node-expanded' in (node.get_attribute('class') or ''):
                print(f"Node '{node_identifier}' is already expanded")
                return True
            
            # Find and click the expand icon
            try:
                expand_icon = node.find_element(By.CSS_SELECTOR, '.ant-tree-switcher, .ant-tree-node-switcher')
                expand_icon.click()
                time.sleep(0.2)
                
                # Wait for expansion
                wait.until(lambda d: 'ant-tree-node-expanded' in (node.get_attribute('class') or ''))
                print(f"Node '{node_identifier}' expanded successfully")
                return True
            except NoSuchElementException:
                print(f"Node '{node_identifier}' is a leaf node and cannot be expanded")
                return False
                
        except Exception as e:
            print(f"Error expanding node: {str(e)}")
            return False
    
    def collapse_node(self, node_identifier: str, treeselect_identifier: str,
                     treeselect_identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Collapse a tree node
        
        Args:
            node_identifier: Node title, value, or path
            treeselect_identifier: Value to identify the TreeSelect
            treeselect_identifier_type: Type of identifier for TreeSelect
            timeout: Maximum wait time in seconds
            
        Returns:
            True if node was collapsed, False otherwise
        """
        element = self._find_treeselect(treeselect_identifier, treeselect_identifier_type, timeout)
        if not element:
            return False
        
        try:
            # Open dropdown if not open
            if not self._is_dropdown_open(element):
                self.open_dropdown(treeselect_identifier, treeselect_identifier_type, timeout)
            
            # Wait for tree to be visible
            wait = WebDriverWait(self.driver, timeout)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-select-dropdown:not([style*="display: none"])')))
            
            # Find the node
            node = self._find_node_element(dropdown, node_identifier)
            if not node:
                print(f"Node '{node_identifier}' not found")
                return False
            
            # Check if already collapsed
            if 'ant-tree-node-expanded' not in (node.get_attribute('class') or ''):
                print(f"Node '{node_identifier}' is already collapsed")
                return True
            
            # Find and click the collapse icon
            expand_icon = node.find_element(By.CSS_SELECTOR, '.ant-tree-switcher, .ant-tree-node-switcher')
            expand_icon.click()
            time.sleep(0.2)
            
            # Wait for collapse
            wait.until(lambda d: 'ant-tree-node-expanded' not in (node.get_attribute('class') or ''))
            print(f"Node '{node_identifier}' collapsed successfully")
            return True
                
        except Exception as e:
            print(f"Error collapsing node: {str(e)}")
            return False
    
    def check_node(self, node_identifier: str, treeselect_identifier: str,
                  treeselect_identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Check a node in checkable TreeSelect
        
        Args:
            node_identifier: Node title, value, or path
            treeselect_identifier: Value to identify the TreeSelect
            treeselect_identifier_type: Type of identifier for TreeSelect
            timeout: Maximum wait time in seconds
            
        Returns:
            True if node was checked, False otherwise
        """
        element = self._find_treeselect(treeselect_identifier, treeselect_identifier_type, timeout)
        if not element:
            return False
        
        # Check if TreeSelect is checkable
        treeselect_info = self.identifier.identify_treeselect_type(element)
        if not treeselect_info.get('checkable', False):
            print("TreeSelect is not checkable")
            return False
        
        try:
            # Open dropdown if not open
            if not self._is_dropdown_open(element):
                self.open_dropdown(treeselect_identifier, treeselect_identifier_type, timeout)
            
            # Wait for tree to be visible
            wait = WebDriverWait(self.driver, timeout)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-select-dropdown:not([style*="display: none"])')))
            
            # Find the node
            node = self._find_node_element(dropdown, node_identifier)
            if not node:
                print(f"Node '{node_identifier}' not found")
                return False
            
            # Find and click the checkbox
            checkbox = node.find_element(By.CSS_SELECTOR, '.ant-tree-checkbox')
            checkbox.click()
            time.sleep(0.2)
            
            # Verify checked
            if 'ant-tree-checkbox-checked' in (checkbox.get_attribute('class') or ''):
                print(f"Node '{node_identifier}' checked successfully")
                return True
            else:
                print(f"Node '{node_identifier}' checkbox click did not result in checked state")
                return False
                
        except Exception as e:
            print(f"Error checking node: {str(e)}")
            return False
    
    def uncheck_node(self, node_identifier: str, treeselect_identifier: str,
                    treeselect_identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Uncheck a node in checkable TreeSelect
        
        Args:
            node_identifier: Node title, value, or path
            treeselect_identifier: Value to identify the TreeSelect
            treeselect_identifier_type: Type of identifier for TreeSelect
            timeout: Maximum wait time in seconds
            
        Returns:
            True if node was unchecked, False otherwise
        """
        element = self._find_treeselect(treeselect_identifier, treeselect_identifier_type, timeout)
        if not element:
            return False
        
        # Check if TreeSelect is checkable
        treeselect_info = self.identifier.identify_treeselect_type(element)
        if not treeselect_info.get('checkable', False):
            print("TreeSelect is not checkable")
            return False
        
        try:
            # Open dropdown if not open
            if not self._is_dropdown_open(element):
                self.open_dropdown(treeselect_identifier, treeselect_identifier_type, timeout)
            
            # Wait for tree to be visible
            wait = WebDriverWait(self.driver, timeout)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-select-dropdown:not([style*="display: none"])')))
            
            # Find the node
            node = self._find_node_element(dropdown, node_identifier)
            if not node:
                print(f"Node '{node_identifier}' not found")
                return False
            
            # Find and click the checkbox
            checkbox = node.find_element(By.CSS_SELECTOR, '.ant-tree-checkbox')
            
            # Check if already unchecked
            if 'ant-tree-checkbox-checked' not in (checkbox.get_attribute('class') or ''):
                print(f"Node '{node_identifier}' is already unchecked")
                return True
            
            checkbox.click()
            time.sleep(0.2)
            
            # Verify unchecked
            if 'ant-tree-checkbox-checked' not in (checkbox.get_attribute('class') or ''):
                print(f"Node '{node_identifier}' unchecked successfully")
                return True
            else:
                print(f"Node '{node_identifier}' checkbox click did not result in unchecked state")
                return False
                
        except Exception as e:
            print(f"Error unchecking node: {str(e)}")
            return False
    
    def search_in_treeselect(self, search_text: str, treeselect_identifier: str,
                            treeselect_identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Search within TreeSelect (when search is enabled)
        
        Args:
            search_text: Text to search for
            treeselect_identifier: Value to identify the TreeSelect
            treeselect_identifier_type: Type of identifier for TreeSelect
            timeout: Maximum wait time in seconds
            
        Returns:
            True if search was performed, False otherwise
        """
        element = self._find_treeselect(treeselect_identifier, treeselect_identifier_type, timeout)
        if not element:
            return False
        
        # Check if search is enabled
        treeselect_info = self.identifier.identify_treeselect_type(element)
        if not treeselect_info.get('search_enabled', False):
            print("TreeSelect does not have search enabled")
            return False
        
        try:
            # Open dropdown if not open
            if not self._is_dropdown_open(element):
                self.open_dropdown(treeselect_identifier, treeselect_identifier_type, timeout)
            
            # Wait for search input to be visible
            wait = WebDriverWait(self.driver, timeout)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-select-dropdown:not([style*="display: none"])')))
            search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-select-tree-select-search__field, input.ant-select-search__field')))
            
            # Clear and type search text
            search_input.clear()
            search_input.send_keys(search_text)
            time.sleep(0.3)  # Wait for filtering
            
            print(f"Search performed with text: '{search_text}'")
            return True
                
        except Exception as e:
            print(f"Error searching in TreeSelect: {str(e)}")
            return False
    
    def clear_selection(self, treeselect_identifier: str, treeselect_identifier_type: str = 'auto',
                       timeout: int = 10) -> bool:
        """
        Clear all selections in TreeSelect
        
        Args:
            treeselect_identifier: Value to identify the TreeSelect
            treeselect_identifier_type: Type of identifier for TreeSelect
            timeout: Maximum wait time in seconds
            
        Returns:
            True if selection was cleared, False otherwise
        """
        element = self._find_treeselect(treeselect_identifier, treeselect_identifier_type, timeout)
        if not element:
            return False
        
        try:
            # Find clear button
            try:
                clear_button = element.find_element(By.CSS_SELECTOR, '.ant-select-clear')
                clear_button.click()
                time.sleep(0.2)
                print("Selection cleared successfully")
                return True
            except NoSuchElementException:
                # For multiple select, remove each tag
                tags = element.find_elements(By.CSS_SELECTOR, '.ant-select-selection-item-remove')
                for tag in tags:
                    tag.click()
                    time.sleep(0.1)
                print("All selections cleared successfully")
                return True
                
        except Exception as e:
            print(f"Error clearing selection: {str(e)}")
            return False
    
    def select_all_leaf_nodes(self, parent_node: str, treeselect_identifier: str,
                              treeselect_identifier_type: str = 'auto', timeout: int = 10) -> bool:
        """
        Select all leaf nodes under a parent node
        
        Args:
            parent_node: Parent node title, value, or path
            treeselect_identifier: Value to identify the TreeSelect
            treeselect_identifier_type: Type of identifier for TreeSelect
            timeout: Maximum wait time in seconds
            
        Returns:
            True if all leaf nodes were selected, False otherwise
        """
        element = self._find_treeselect(treeselect_identifier, treeselect_identifier_type, timeout)
        if not element:
            return False
        
        try:
            # Get tree structure
            treeselect_info = self.identifier.identify_treeselect_type(element)
            tree_structure = treeselect_info.get('tree_structure', {})
            
            # Find parent node
            parent_node_info = None
            if '>' in parent_node:
                parent_node_info = self.identifier.get_node_by_path(tree_structure, parent_node)
            else:
                # Search for parent in tree structure
                def find_node(nodes, target):
                    for node in nodes:
                        if (node.get('title', '').strip() == target or
                            node.get('value', '').strip() == target or
                            node.get('key', '').strip() == target):
                            return node
                        found = find_node(node.get('children', []), target)
                        if found:
                            return found
                    return None
                
                parent_node_info = find_node(tree_structure.get('nodes', []), parent_node)
            
            if not parent_node_info:
                print(f"Parent node '{parent_node}' not found")
                return False
            
            # Get all leaf nodes under parent
            leaf_nodes = []
            def collect_leafs(node):
                if node.get('isLeaf', False) or len(node.get('children', [])) == 0:
                    leaf_nodes.append(node.get('title') or node.get('value') or node.get('key'))
                else:
                    for child in node.get('children', []):
                        collect_leafs(child)
            
            collect_leafs(parent_node_info)
            
            if not leaf_nodes:
                print(f"No leaf nodes found under '{parent_node}'")
                return False
            
            # Select all leaf nodes
            return self.select_multiple_nodes(leaf_nodes, treeselect_identifier, treeselect_identifier_type, timeout)
                
        except Exception as e:
            print(f"Error selecting all leaf nodes: {str(e)}")
            return False
    
    def get_treeselect_info(self, identifier: str, identifier_type: str = 'auto') -> Optional[Dict]:
        """
        Get information about a TreeSelect without interacting with it
        
        Args:
            identifier: Value to identify the TreeSelect
            identifier_type: Type of identifier
            
        Returns:
            Dictionary with TreeSelect information or None if not found
        """
        element = self._find_treeselect(identifier, identifier_type)
        if element:
            info = self.identifier.identify_treeselect_type(element)
            # Populate tree structure using JavaScript if dropdown is open or can be opened
            try:
                # Try to get tree structure if dropdown is open
                if self._is_dropdown_open(element):
                    tree_structure = self.identifier.get_tree_structure_js(self.driver, element)
                    if tree_structure:
                        info['tree_structure'] = tree_structure
                        # Update type based on tree structure
                        if tree_structure.get('async_loading', False) and info.get('type') == 'basic':
                            info['type'] = 'async'
                        if tree_structure.get('has_custom_icons', False) and info.get('type') == 'basic':
                            info['type'] = 'custom_icons'
            except:
                pass
            return info
        return None
    
    def print_treeselect_summary(self, identifier: str, identifier_type: str = 'auto') -> bool:
        """
        Print a readable summary of detected TreeSelect components
        
        Args:
            identifier: Value to identify the TreeSelect
            identifier_type: Type of identifier
            
        Returns:
            True if summary was printed, False otherwise
        """
        info = self.get_treeselect_info(identifier, identifier_type)
        if not info:
            print(f"TreeSelect not found: {identifier}")
            return False
        
        print(f"\n{'='*80}")
        print(f"TreeSelect Summary: {identifier}")
        print(f"{'='*80}")
        print(f"Type: {info.get('type', 'unknown')}")
        print(f"Multiple Selection: {info.get('multiple', False)}")
        print(f"Checkable: {info.get('checkable', False)}")
        print(f"Disabled: {info.get('disabled', False)}")
        print(f"Search Enabled: {info.get('search_enabled', False)}")
        print(f"Placeholder: {info.get('placeholder', 'N/A')}")
        print(f"Size: {info.get('size', 'default')}")
        print(f"Placement: {info.get('placement', 'N/A')}")
        print(f"Selected Values: {info.get('selected_values', [])}")
        print(f"Selected Labels: {info.get('selected_labels', [])}")
        
        tree_structure = info.get('tree_structure', {})
        if tree_structure:
            print(f"Tree Depth: {tree_structure.get('depth', 0)}")
            print(f"Total Nodes: {tree_structure.get('total_nodes', 0)}")
            print(f"Expanded Nodes: {tree_structure.get('expanded_keys', [])}")
            print(f"Selected Nodes: {tree_structure.get('selected_keys', [])}")
            if info.get('checkable', False):
                print(f"Checked Nodes: {tree_structure.get('checked_keys', [])}")
        
        print(f"{'='*80}\n")
        return True
    
    # Helper methods
    def _find_treeselect(self, identifier: str, identifier_type: str = 'auto', timeout: int = 10) -> Optional[WebElement]:
        """Find TreeSelect element"""
        if identifier_type == 'data_attr_id':
            return self.locator.find_treeselect_by_data_attr(identifier, timeout)
        elif identifier_type == 'label':
            return self.locator.find_treeselect_by_label(identifier, exact_match=False, timeout=timeout)
        elif identifier_type == 'position':
            position = int(identifier) if identifier.isdigit() else 1
            return self.locator.find_treeselect_by_position(position, timeout=timeout)
        elif identifier_type == 'auto':
            element = self.locator.find_treeselect_by_data_attr(identifier, timeout=3)
            if not element:
                element = self.locator.find_treeselect_by_label(identifier, exact_match=False, timeout=5)
            if not element and identifier.isdigit():
                position = int(identifier)
                element = self.locator.find_treeselect_by_position(position, timeout=5)
            return element
        return None
    
    def _is_dropdown_open(self, element: WebElement) -> bool:
        """Check if TreeSelect dropdown is open"""
        try:
            dropdown = self.driver.find_element(By.CSS_SELECTOR, '.ant-select-dropdown:not([style*="display: none"])')
            # Check if dropdown is associated with this TreeSelect
            return True
        except:
            return False
    
    def _select_node_by_title(self, dropdown: WebElement, title: str, exact_match: bool = False, timeout: int = 10) -> bool:
        """Select a node by its title"""
        try:
            if exact_match:
                xpath = f".//*[contains(@class, 'ant-tree-node')]//*[contains(@class, 'ant-tree-title') and normalize-space(text())='{title}']"
            else:
                xpath = f".//*[contains(@class, 'ant-tree-node')]//*[contains(@class, 'ant-tree-title') and contains(text(), '{title}')]"
            
            node = dropdown.find_element(By.XPATH, xpath)
            # Scroll into view
            self.execute_js("arguments[0].scrollIntoView({block: 'center'});", node)
            time.sleep(0.1)
            node.click()
            return True
        except:
            return False
    
    def _select_node_by_path(self, dropdown: WebElement, path: str, timeout: int = 10) -> bool:
        """Select a node by path (e.g., "Parent > Child > Grandchild")"""
        path_parts = [p.strip() for p in path.split('>')]
        
        try:
            current_xpath = ".//*[contains(@class, 'ant-tree')]"
            
            for i, part in enumerate(path_parts):
                # Expand parent if needed
                if i > 0:
                    parent_xpath = current_xpath + f"//*[contains(@class, 'ant-tree-node')]//*[contains(@class, 'ant-tree-title') and contains(text(), '{path_parts[i-1]}')]"
                    try:
                        parent_node = dropdown.find_element(By.XPATH, parent_xpath)
                        # Check if expanded, if not expand
                        parent_tree_node = parent_node.find_element(By.XPATH, "./ancestor::*[contains(@class, 'ant-tree-node')][1]")
                        if 'ant-tree-node-expanded' not in (parent_tree_node.get_attribute('class') or ''):
                            expand_icon = parent_tree_node.find_element(By.CSS_SELECTOR, '.ant-tree-switcher')
                            expand_icon.click()
                            time.sleep(0.2)
                    except:
                        pass
                
                # Build xpath for current part
                if i == len(path_parts) - 1:
                    # Last part - select it
                    node_xpath = current_xpath + f"//*[contains(@class, 'ant-tree-node')]//*[contains(@class, 'ant-tree-title') and contains(text(), '{part}')]"
                    node = dropdown.find_element(By.XPATH, node_xpath)
                    self.execute_js("arguments[0].scrollIntoView({block: 'center'});", node)
                    time.sleep(0.1)
                    node.click()
                    return True
                else:
                    # Not last part - continue building path
                    current_xpath += f"//*[contains(@class, 'ant-tree-node')]//*[contains(@class, 'ant-tree-title') and contains(text(), '{part}')]/ancestor::*[contains(@class, 'ant-tree-node')][1]"
            
            return False
        except Exception as e:
            print(f"Error selecting node by path: {str(e)}")
            return False
    
    def _find_node_element(self, dropdown: WebElement, node_identifier: str) -> Optional[WebElement]:
        """Find a node element by identifier"""
        try:
            # Try exact match first
            xpath = f".//*[contains(@class, 'ant-tree-node')]//*[contains(@class, 'ant-tree-title') and normalize-space(text())='{node_identifier}']"
            node = dropdown.find_element(By.XPATH, xpath)
            return node.find_element(By.XPATH, "./ancestor::*[contains(@class, 'ant-tree-node')][1]")
        except:
            # Try partial match
            try:
                xpath = f".//*[contains(@class, 'ant-tree-node')]//*[contains(@class, 'ant-tree-title') and contains(text(), '{node_identifier}')]"
                node = dropdown.find_element(By.XPATH, xpath)
                return node.find_element(By.XPATH, "./ancestor::*[contains(@class, 'ant-tree-node')][1]")
            except:
                return None
