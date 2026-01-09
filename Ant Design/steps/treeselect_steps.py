"""
Gherkin step definitions for TreeSelect automation using pytest-bdd
pytest-bdd automatically discovers and loads these step definitions
"""
import time
from pytest_bdd import given, when, then, parsers

# Ant Design TreeSelect page URL
DEFAULT_URL = "https://ant.design/components/tree-select"


@given('I am on the TreeSelect page')
def step_navigate_to_treeselect_page(context):
    """
    Navigate to the default TreeSelect page
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Navigating to: {DEFAULT_URL}")
    context.driver.get(DEFAULT_URL)
    print(f"   >> Page loaded successfully")


@given(parsers.parse('I am on the "{page_url}" page'))
def step_navigate_to_page(context, page_url):
    """
    Navigate to a specific page
    
    Args:
        context: Context fixture from conftest.py
        page_url: URL of the page to navigate to
    """
    context.driver.get(page_url)


@when(parsers.parse('I select "{node_text}" from "{treeselect_label}" TreeSelect'))
def step_select_node_from_treeselect(context, node_text, treeselect_label):
    """
    Select a node from a TreeSelect by label
    
    Args:
        context: Context fixture from conftest.py
        node_text: Text of the node to select
        treeselect_label: Label or identifier of the TreeSelect
    """
    print(f"   >> Selecting '{node_text}' from TreeSelect '{treeselect_label}'...")
    success = context.treeselect_handler.select_node(
        node_text,
        treeselect_label,
        identifier_type='auto'
    )
    assert success, f"Failed to select '{node_text}' from TreeSelect '{treeselect_label}'"
    print(f"   >> Node selected successfully")


@when(parsers.parse('I select multiple options "{node_list}" from "{treeselect_label}" TreeSelect'))
def step_select_multiple_nodes(context, node_list, treeselect_label):
    """
    Select multiple nodes from a TreeSelect
    
    Args:
        context: Context fixture from conftest.py
        node_list: Comma-separated list of node texts
        treeselect_label: Label or identifier of the TreeSelect
    """
    nodes = [n.strip() for n in node_list.split(',')]
    print(f"   >> Selecting multiple nodes {nodes} from TreeSelect '{treeselect_label}'...")
    success = context.treeselect_handler.select_multiple_nodes(
        nodes,
        treeselect_label,
        identifier_type='auto'
    )
    assert success, f"Failed to select multiple nodes from TreeSelect '{treeselect_label}'"
    print(f"   >> Multiple nodes selected successfully")


@when(parsers.parse('I expand "{node_text}" node in "{treeselect_label}" TreeSelect'))
def step_expand_node(context, node_text, treeselect_label):
    """
    Expand a tree node
    
    Args:
        context: Context fixture from conftest.py
        node_text: Text of the node to expand
        treeselect_label: Label or identifier of the TreeSelect
    """
    print(f"   >> Expanding node '{node_text}' in TreeSelect '{treeselect_label}'...")
    success = context.treeselect_handler.expand_node(
        node_text,
        treeselect_label,
        identifier_type='auto'
    )
    assert success, f"Failed to expand node '{node_text}' in TreeSelect '{treeselect_label}'"
    print(f"   >> Node expanded successfully")


@when(parsers.parse('I collapse "{node_text}" node in "{treeselect_label}" TreeSelect'))
def step_collapse_node(context, node_text, treeselect_label):
    """
    Collapse a tree node
    
    Args:
        context: Context fixture from conftest.py
        node_text: Text of the node to collapse
        treeselect_label: Label or identifier of the TreeSelect
    """
    print(f"   >> Collapsing node '{node_text}' in TreeSelect '{treeselect_label}'...")
    success = context.treeselect_handler.collapse_node(
        node_text,
        treeselect_label,
        identifier_type='auto'
    )
    assert success, f"Failed to collapse node '{node_text}' in TreeSelect '{treeselect_label}'"
    print(f"   >> Node collapsed successfully")


@when(parsers.parse('I check "{node_text}" node in "{treeselect_label}" TreeSelect'))
def step_check_node(context, node_text, treeselect_label):
    """
    Check a node in checkable TreeSelect
    
    Args:
        context: Context fixture from conftest.py
        node_text: Text of the node to check
        treeselect_label: Label or identifier of the TreeSelect
    """
    print(f"   >> Checking node '{node_text}' in TreeSelect '{treeselect_label}'...")
    success = context.treeselect_handler.check_node(
        node_text,
        treeselect_label,
        identifier_type='auto'
    )
    assert success, f"Failed to check node '{node_text}' in TreeSelect '{treeselect_label}'"
    print(f"   >> Node checked successfully")


@when(parsers.parse('I uncheck "{node_text}" node in "{treeselect_label}" TreeSelect'))
def step_uncheck_node(context, node_text, treeselect_label):
    """
    Uncheck a node in checkable TreeSelect
    
    Args:
        context: Context fixture from conftest.py
        node_text: Text of the node to uncheck
        treeselect_label: Label or identifier of the TreeSelect
    """
    print(f"   >> Unchecking node '{node_text}' in TreeSelect '{treeselect_label}'...")
    success = context.treeselect_handler.uncheck_node(
        node_text,
        treeselect_label,
        identifier_type='auto'
    )
    assert success, f"Failed to uncheck node '{node_text}' in TreeSelect '{treeselect_label}'"
    print(f"   >> Node unchecked successfully")


@when(parsers.parse('I check all child nodes under "{parent_node}" in "{treeselect_label}" TreeSelect'))
def step_check_all_child_nodes(context, parent_node, treeselect_label):
    """
    Check all child nodes under a parent in checkable TreeSelect
    
    Args:
        context: Context fixture from conftest.py
        parent_node: Text of the parent node
        treeselect_label: Label or identifier of the TreeSelect
    """
    print(f"   >> Checking all child nodes under '{parent_node}' in TreeSelect '{treeselect_label}'...")
    # First expand the parent if needed
    context.treeselect_handler.expand_node(parent_node, treeselect_label, identifier_type='auto')
    
    # Get tree structure to find all child nodes
    info = context.treeselect_handler.get_treeselect_info(treeselect_label, identifier_type='auto')
    if not info:
        assert False, f"TreeSelect '{treeselect_label}' not found"
    
    tree_structure = info.get('tree_structure', {})
    parent_node_info = context.treeselect_handler.identifier.get_node_by_path(tree_structure, parent_node)
    
    if not parent_node_info:
        # Try to find by title
        def find_node(nodes, target):
            for node in nodes:
                if (node.get('title', '').strip() == target or
                    node.get('value', '').strip() == target):
                    return node
                found = find_node(node.get('children', []), target)
                if found:
                    return found
            return None
        parent_node_info = find_node(tree_structure.get('nodes', []), parent_node)
    
    if not parent_node_info:
        assert False, f"Parent node '{parent_node}' not found"
    
    # Get all child nodes
    child_nodes = []
    for child in parent_node_info.get('children', []):
        child_title = child.get('title') or child.get('value') or child.get('key')
        if child_title:
            child_nodes.append(child_title)
    
    if not child_nodes:
        print(f"   >> No child nodes found under '{parent_node}'")
        return
    
    # Check each child node
    for child in child_nodes:
        context.treeselect_handler.check_node(child, treeselect_label, identifier_type='auto')
        time.sleep(0.1)
    
    print(f"   >> All {len(child_nodes)} child nodes checked successfully")


@when(parsers.parse('I search for "{search_text}" in "{treeselect_label}" TreeSelect'))
def step_search_in_treeselect(context, search_text, treeselect_label):
    """
    Search within TreeSelect
    
    Args:
        context: Context fixture from conftest.py
        search_text: Text to search for
        treeselect_label: Label or identifier of the TreeSelect
    """
    print(f"   >> Searching for '{search_text}' in TreeSelect '{treeselect_label}'...")
    success = context.treeselect_handler.search_in_treeselect(
        search_text,
        treeselect_label,
        identifier_type='auto'
    )
    assert success, f"Failed to search in TreeSelect '{treeselect_label}'"
    print(f"   >> Search performed successfully")


@when(parsers.parse('I clear selection in "{treeselect_label}" TreeSelect'))
def step_clear_selection(context, treeselect_label):
    """
    Clear all selections in TreeSelect
    
    Args:
        context: Context fixture from conftest.py
        treeselect_label: Label or identifier of the TreeSelect
    """
    print(f"   >> Clearing selection in TreeSelect '{treeselect_label}'...")
    success = context.treeselect_handler.clear_selection(
        treeselect_label,
        identifier_type='auto'
    )
    assert success, f"Failed to clear selection in TreeSelect '{treeselect_label}'"
    print(f"   >> Selection cleared successfully")


@when(parsers.parse('I select all leaf nodes under "{parent_node}" in "{treeselect_label}" TreeSelect'))
def step_select_all_leaf_nodes(context, parent_node, treeselect_label):
    """
    Select all leaf nodes under a parent node
    
    Args:
        context: Context fixture from conftest.py
        parent_node: Text of the parent node
        treeselect_label: Label or identifier of the TreeSelect
    """
    print(f"   >> Selecting all leaf nodes under '{parent_node}' in TreeSelect '{treeselect_label}'...")
    success = context.treeselect_handler.select_all_leaf_nodes(
        parent_node,
        treeselect_label,
        identifier_type='auto'
    )
    assert success, f"Failed to select all leaf nodes in TreeSelect '{treeselect_label}'"
    print(f"   >> All leaf nodes selected successfully")


@then(parsers.parse('"{treeselect_label}" TreeSelect should contain "{expected_text}"'))
def step_verify_treeselect_contains(context, treeselect_label, expected_text):
    """
    Verify that TreeSelect contains expected text in selected values
    
    Args:
        context: Context fixture from conftest.py
        treeselect_label: Label or identifier of the TreeSelect
        expected_text: Expected text to be present
    """
    print(f"   >> Verifying TreeSelect '{treeselect_label}' contains '{expected_text}'...")
    info = context.treeselect_handler.get_treeselect_info(treeselect_label, identifier_type='auto')
    assert info is not None, f"TreeSelect '{treeselect_label}' not found"
    
    selected_labels = info.get('selected_labels', [])
    selected_values = info.get('selected_values', [])
    
    found = False
    for label in selected_labels:
        if expected_text in label or label in expected_text:
            found = True
            break
    
    if not found:
        for value in selected_values:
            if expected_text in value or value in expected_text:
                found = True
                break
    
    assert found, f"TreeSelect '{treeselect_label}' does not contain '{expected_text}'. Selected: {selected_labels}"
    print(f"   >> Verification passed: TreeSelect contains '{expected_text}'")


@then(parsers.parse('"{treeselect_label}" TreeSelect should show {count:d} selected items'))
def step_verify_treeselect_selection_count(context, treeselect_label, count):
    """
    Verify the number of selected items in TreeSelect
    
    Args:
        context: Context fixture from conftest.py
        treeselect_label: Label or identifier of the TreeSelect
        count: Expected number of selected items
    """
    print(f"   >> Verifying TreeSelect '{treeselect_label}' has {count} selected items...")
    info = context.treeselect_handler.get_treeselect_info(treeselect_label, identifier_type='auto')
    assert info is not None, f"TreeSelect '{treeselect_label}' not found"
    
    selected_count = len(info.get('selected_labels', []))
    assert selected_count == count, f"Expected {count} selected items but found {selected_count}"
    print(f"   >> Verification passed: TreeSelect has {count} selected items")


@then(parsers.parse('I print summary of "{treeselect_label}" TreeSelect'))
def step_print_treeselect_summary(context, treeselect_label):
    """
    Print a summary of TreeSelect properties
    
    Args:
        context: Context fixture from conftest.py
        treeselect_label: Label or identifier of the TreeSelect
    """
    print(f"   >> Printing summary of TreeSelect '{treeselect_label}'...")
    context.treeselect_handler.print_treeselect_summary(treeselect_label, identifier_type='auto')


# Context-driven steps
@given(parsers.parse('I identify the TreeSelect with data-attr-id "{data_attr_id}"'))
def step_identify_treeselect_by_data_attr(context, data_attr_id):
    """
    Identify a TreeSelect by data-attr-id and store it in context
    
    Args:
        context: Context fixture from conftest.py
        data_attr_id: Value of data-attr-id attribute
    """
    print(f"   >> Identifying TreeSelect with data-attr-id: '{data_attr_id}'...")
    success = context.treeselect_handler.identify_and_store(
        data_attr_id,
        identifier_type='data_attr_id'
    )
    assert success, f"Failed to identify TreeSelect with data-attr-id '{data_attr_id}'"
    print(f"   >> TreeSelect identified and stored in context")


@given(parsers.parse('I identify the TreeSelect with label "{label}"'))
def step_identify_treeselect_by_label(context, label):
    """
    Identify a TreeSelect by label and store it in context
    
    Args:
        context: Context fixture from conftest.py
        label: Label text of the TreeSelect
    """
    print(f"   >> Identifying TreeSelect with label: '{label}'...")
    success = context.treeselect_handler.identify_and_store(
        label,
        identifier_type='label'
    )
    assert success, f"Failed to identify TreeSelect with label '{label}'"
    print(f"   >> TreeSelect identified and stored in context")
