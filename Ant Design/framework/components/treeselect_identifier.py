"""
TreeSelect Identifier - Handles analyzing and identifying TreeSelect properties
Single Responsibility: Analyze TreeSelect elements and extract their properties
"""
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Dict, Optional, List
from framework.identifiers.generic_element_identifier import GenericElementIdentifier


class TreeSelectIdentifier:
    """
    Handles identifying and analyzing Ant Design TreeSelect properties
    Single Responsibility: Extract TreeSelect type, state, tree structure, and other properties
    """
    
    # Ant Design TreeSelect class patterns
    TREESELECT_CLASSES = {
        'ant-select': 'ant-select',
        'ant-select-tree': 'ant-select-tree',
        'ant-select-tree-select': 'ant-select-tree-select',
        'ant-select-focused': 'ant-select-focused',
        'ant-select-disabled': 'ant-select-disabled',
        'ant-select-multiple': 'ant-select-multiple',
        'ant-select-show-search': 'ant-select-show-search'
    }
    
    # Tree node class patterns
    TREE_NODE_CLASSES = {
        'ant-tree': 'ant-tree',
        'ant-tree-node': 'ant-tree-node',
        'ant-tree-node-selected': 'ant-tree-node-selected',
        'ant-tree-node-disabled': 'ant-tree-node-disabled',
        'ant-tree-node-expanded': 'ant-tree-node-expanded',
        'ant-tree-node-leaf': 'ant-tree-node-leaf',
        'ant-tree-checkbox': 'ant-tree-checkbox',
        'ant-tree-checkbox-checked': 'ant-tree-checkbox-checked',
        'ant-tree-checkbox-indeterminate': 'ant-tree-checkbox-indeterminate'
    }
    
    @staticmethod
    def identify_treeselect_type(element: WebElement) -> Dict[str, any]:
        """
        Automatically identify the type and properties of an Ant Design TreeSelect
        Integrates with GenericElementIdentifier to read custom attributes
        
        Args:
            element: WebElement representing the TreeSelect
            
        Returns:
            Dictionary containing TreeSelect properties:
            {
                'type': 'basic'|'multiple'|'checkable'|'disabled'|'search'|'async'|'custom_icons'|'placement'|'size',
                'multiple': bool,
                'checkable': bool,
                'disabled': bool,
                'search_enabled': bool,
                'placeholder': str,
                'data_attr_id': str|None,
                'application_type': str|None,
                'size': 'large'|'default'|'small'|None,
                'placement': 'bottomLeft'|'bottomRight'|'topLeft'|'topRight'|None,
                'selected_values': List[str],
                'selected_labels': List[str],
                'expanded_nodes': List[str],
                'tree_structure': Dict,
                'metadata': dict
            }
        """
        # First, get generic element information
        generic_info = GenericElementIdentifier.identify_element(element)
        
        treeselect_info = {
            'type': 'basic',
            'multiple': False,
            'checkable': False,
            'disabled': False,
            'search_enabled': False,
            'placeholder': '',
            'data_attr_id': generic_info.get('data_attr_id'),
            'application_type': generic_info.get('application_type'),
            'size': None,
            'placement': None,
            'selected_values': [],
            'selected_labels': [],
            'expanded_nodes': [],
            'tree_structure': {},
            'metadata': generic_info.get('metadata', {})
        }
        
        try:
            # Get class attribute
            class_attr = element.get_attribute('class') or ''
            classes = class_attr.split()
            
            # Check for multiple selection
            if 'ant-select-multiple' in classes:
                treeselect_info['multiple'] = True
                treeselect_info['type'] = 'multiple'
            
            # Check for disabled state
            if 'ant-select-disabled' in classes or element.get_attribute('disabled') is not None:
                treeselect_info['disabled'] = True
                treeselect_info['type'] = 'disabled'
            
            # Check for search enabled
            if 'ant-select-show-search' in classes:
                treeselect_info['search_enabled'] = True
                if treeselect_info['type'] == 'basic':
                    treeselect_info['type'] = 'search'
            
            # Get placeholder
            try:
                placeholder_elem = element.find_element(By.CSS_SELECTOR, '.ant-select-selection-placeholder')
                treeselect_info['placeholder'] = placeholder_elem.text.strip()
            except:
                try:
                    treeselect_info['placeholder'] = element.get_attribute('placeholder') or ''
                except:
                    pass
            
            # Get size
            if 'ant-select-lg' in classes:
                treeselect_info['size'] = 'large'
            elif 'ant-select-sm' in classes:
                treeselect_info['size'] = 'small'
            else:
                treeselect_info['size'] = 'default'
            
            # Get selected values and labels
            try:
                selected_tags = element.find_elements(By.CSS_SELECTOR, '.ant-select-selection-item')
                for tag in selected_tags:
                    try:
                        label = tag.text.strip()
                        if label:
                            treeselect_info['selected_labels'].append(label)
                            # Try to get value from data attribute
                            value = tag.get_attribute('data-value') or label
                            treeselect_info['selected_values'].append(value)
                    except:
                        pass
            except:
                pass
            
            # Check for checkable mode (look for checkboxes in tree)
            try:
                # Check if dropdown is open or check tree structure
                checkboxes = element.find_elements(By.CSS_SELECTOR, '.ant-tree-checkbox')
                if checkboxes:
                    treeselect_info['checkable'] = True
                    if treeselect_info['type'] == 'basic':
                        treeselect_info['type'] = 'checkable'
            except:
                pass
            
            # Tree structure will be populated by handler if needed
            # (JavaScript execution requires driver access which handler has)
            treeselect_info['tree_structure'] = {}
            
            # Get placement from popup (if available)
            try:
                # Try to find popup element
                popup = element.find_element(By.CSS_SELECTOR, '.ant-select-dropdown')
                if popup:
                    popup_class = popup.get_attribute('class') or ''
                    if 'placement-topLeft' in popup_class:
                        treeselect_info['placement'] = 'topLeft'
                    elif 'placement-topRight' in popup_class:
                        treeselect_info['placement'] = 'topRight'
                    elif 'placement-bottomRight' in popup_class:
                        treeselect_info['placement'] = 'bottomRight'
                    else:
                        treeselect_info['placement'] = 'bottomLeft'  # Default
            except:
                pass
                
        except Exception as e:
            print(f"Error identifying TreeSelect type: {str(e)}")
        
        return treeselect_info
    
    @staticmethod
    def get_tree_structure_js(driver, element: WebElement) -> Dict:
        """
        Extract tree structure using JavaScript
        This method should be called from handler which has driver access
        
        Args:
            driver: WebDriver instance
            element: TreeSelect WebElement
            
        Returns:
            Dictionary with tree structure information
        """
        try:
            js_code = """
            (function(element) {
                var result = {
                    nodes: [],
                    expanded_keys: [],
                    selected_keys: [],
                    checked_keys: [],
                    async_loading: false,
                    has_custom_icons: false,
                    depth: 0,
                    total_nodes: 0
                };
                
                // Find the tree dropdown
                var dropdown = document.querySelector('.ant-select-dropdown:not([style*="display: none"])');
                if (!dropdown) {
                    // Try to find tree within the select element
                    var tree = element.querySelector('.ant-tree');
                    if (tree) {
                        dropdown = { querySelector: function(sel) { return tree.querySelector(sel); } };
                    }
                }
                
                if (!dropdown) {
                    return result;
                }
                
                // Find all tree nodes
                var treeNodes = dropdown.querySelectorAll ? dropdown.querySelectorAll('.ant-tree-node') : [];
                if (treeNodes.length === 0) {
                    treeNodes = element.querySelectorAll ? element.querySelectorAll('.ant-tree-node') : [];
                }
                
                result.total_nodes = treeNodes.length;
                
                // Extract node information
                function extractNodeInfo(node) {
                    var info = {
                        key: node.getAttribute('data-key') || node.getAttribute('key') || '',
                        title: '',
                        value: node.getAttribute('data-value') || node.getAttribute('value') || '',
                        expanded: node.classList.contains('ant-tree-node-expanded'),
                        selected: node.classList.contains('ant-tree-node-selected'),
                        checked: false,
                        disabled: node.classList.contains('ant-tree-node-disabled'),
                        isLeaf: node.classList.contains('ant-tree-node-leaf'),
                        children: []
                    };
                    
                    // Get title
                    var titleElem = node.querySelector('.ant-tree-title, .ant-tree-node-content-wrapper');
                    if (titleElem) {
                        info.title = titleElem.textContent.trim();
                    }
                    
                    // Check for checkbox
                    var checkbox = node.querySelector('.ant-tree-checkbox');
                    if (checkbox) {
                        info.checked = checkbox.classList.contains('ant-tree-checkbox-checked');
                        if (checkbox.classList.contains('ant-tree-checkbox-indeterminate')) {
                            info.checked = 'indeterminate';
                        }
                    }
                    
                    // Check for custom icons
                    var icon = node.querySelector('.anticon, .ant-tree-iconEle');
                    if (icon && icon.className.indexOf('anticon') !== -1) {
                        result.has_custom_icons = true;
                    }
                    
                    // Check for async loading
                    var loading = node.querySelector('.ant-tree-node-loading, .anticon-loading');
                    if (loading) {
                        result.async_loading = true;
                    }
                    
                    // Track expanded nodes
                    if (info.expanded) {
                        result.expanded_keys.push(info.key || info.value || info.title);
                    }
                    
                    // Track selected nodes
                    if (info.selected) {
                        result.selected_keys.push(info.key || info.value || info.title);
                    }
                    
                    // Track checked nodes
                    if (info.checked === true) {
                        result.checked_keys.push(info.key || info.value || info.title);
                    }
                    
                    // Get children
                    var childNodes = node.querySelectorAll(':scope > .ant-tree-child-tree > .ant-tree-node, :scope > ul > li.ant-tree-node');
                    for (var i = 0; i < childNodes.length; i++) {
                        var childInfo = extractNodeInfo(childNodes[i]);
                        info.children.push(childInfo);
                    }
                    
                    return info;
                }
                
                // Extract all root nodes
                var rootNodes = dropdown.querySelectorAll ? dropdown.querySelectorAll('.ant-tree > .ant-tree-node, .ant-tree > ul > li.ant-tree-node') : [];
                if (rootNodes.length === 0) {
                    rootNodes = treeNodes;
                }
                
                for (var i = 0; i < rootNodes.length; i++) {
                    var nodeInfo = extractNodeInfo(rootNodes[i]);
                    result.nodes.push(nodeInfo);
                    
                    // Calculate depth
                    function calculateDepth(node, currentDepth) {
                        var maxDepth = currentDepth;
                        for (var j = 0; j < node.children.length; j++) {
                            var childDepth = calculateDepth(node.children[j], currentDepth + 1);
                            if (childDepth > maxDepth) {
                                maxDepth = childDepth;
                            }
                        }
                        return maxDepth;
                    }
                    var nodeDepth = calculateDepth(nodeInfo, 1);
                    if (nodeDepth > result.depth) {
                        result.depth = nodeDepth;
                    }
                }
                
                return result;
            })(arguments[0]);
            """
            result = driver.execute_script(js_code, element)
            return result if result else {}
        except Exception as e:
            print(f"   >> Error extracting tree structure: {str(e)}")
            return {}
    
    @staticmethod
    def get_node_by_path(tree_structure: Dict, path: str) -> Optional[Dict]:
        """
        Find a tree node by path (e.g., "Parent > Child > Grandchild")
        
        Args:
            tree_structure: Tree structure dictionary
            path: Path string with '>' separator
            
        Returns:
            Node dictionary if found, None otherwise
        """
        path_parts = [p.strip() for p in path.split('>')]
        nodes = tree_structure.get('nodes', [])
        
        def find_in_nodes(node_list, remaining_path):
            if not remaining_path:
                return None
            
            current = remaining_path[0]
            for node in node_list:
                # Match by title, value, or key
                if (node.get('title', '').strip() == current or
                    node.get('value', '').strip() == current or
                    node.get('key', '').strip() == current):
                    if len(remaining_path) == 1:
                        return node
                    else:
                        return find_in_nodes(node.get('children', []), remaining_path[1:])
            return None
        
        return find_in_nodes(nodes, path_parts)
    
    @staticmethod
    def get_all_leaf_nodes(tree_structure: Dict) -> List[Dict]:
        """
        Get all leaf nodes from tree structure
        
        Args:
            tree_structure: Tree structure dictionary
            
        Returns:
            List of leaf node dictionaries
        """
        leaf_nodes = []
        
        def traverse(node):
            if node.get('isLeaf', False) or len(node.get('children', [])) == 0:
                leaf_nodes.append(node)
            else:
                for child in node.get('children', []):
                    traverse(child)
        
        for node in tree_structure.get('nodes', []):
            traverse(node)
        
        return leaf_nodes
