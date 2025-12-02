"""
Gherkin step definitions for pagination automation using pytest-bdd
pytest-bdd automatically discovers and loads these step definitions
"""
from pytest_bdd import given, when, then, parsers
from framework.components.pagination_handler import PaginationHandler

# Ant Design Pagination page URL
PAGINATION_PAGE_URL = "https://ant.design/components/pagination"


@given('I am on the pagination page')
@given(parsers.parse('I am on the "{page_url}" page'))
def step_navigate_to_pagination_page(context, page_url=None):
    """
    Navigate to a page with pagination
    Can be used as Given or with custom URL
    
    Args:
        context: Context fixture from conftest.py
        page_url: Optional custom URL (defaults to Ant Design Table page)
    """
    url = page_url if page_url else PAGINATION_PAGE_URL
    print(f"   >> Navigating to: {url}")
    context.driver.get(url)
    print(f"   >> Page loaded successfully")


@given(parsers.parse('I identify the pagination with data-atr-id "{data_attr_id}"'))
@when(parsers.parse('I identify the pagination with data-atr-id "{data_attr_id}"'))
@then(parsers.parse('I identify the pagination with data-atr-id "{data_attr_id}"'))
def step_identify_pagination_by_data_attr(context, data_attr_id):
    """
    Identify a pagination by data-atr-id and store it in context
    Can be used as Given, When, or Then
    
    Args:
        context: Context fixture from conftest.py
        data_attr_id: Value of data-atr-id attribute
    """
    print(f"   >> Identifying pagination with data-atr-id: '{data_attr_id}'...")
    success = context.pagination_handler.identify_and_store(
        data_attr_id,
        identifier_type='data_attr'
    )
    assert success, f"Failed to identify pagination with data-atr-id '{data_attr_id}'"
    print(f"   >> Pagination identified and stored in context")


@given(parsers.parse('I identify the pagination at position {position:d}'))
@when(parsers.parse('I identify the pagination at position {position:d}'))
@then(parsers.parse('I identify the pagination at position {position:d}'))
def step_identify_pagination_by_position(context, position):
    """
    Identify a pagination by position and store it in context
    Can be used as Given, When, or Then
    
    Args:
        context: Context fixture from conftest.py
        position: Position number (1 = first pagination, 2 = second, etc.)
    """
    print(f"   >> Identifying pagination at position: {position}...")
    success = context.pagination_handler.identify_and_store(
        str(position),
        identifier_type='position'
    )
    assert success, f"Failed to identify pagination at position {position}"
    print(f"   >> Pagination identified and stored in context")


@given('I identify a pagination with all features')
@when('I identify a pagination with all features')
@then('I identify a pagination with all features')
def step_identify_pagination_with_all_features(context):
    """Identify a pagination with all features"""
    print(f"   >> Identifying pagination with features: all...")
    success = context.pagination_handler.identify_and_store(
        'all',
        identifier_type='features'
    )
    assert success, "Failed to identify pagination with all features"
    print(f"   >> Pagination identified and stored in context")


@given(parsers.re(r'I identify a pagination with (?P<features>\w+)'))
@when(parsers.re(r'I identify a pagination with (?P<features>\w+)'))
@then(parsers.re(r'I identify a pagination with (?P<features>\w+)'))
def step_identify_pagination_with_features(context, features):
    """
    Identify a pagination that has specific features (size_changer, jump_to, etc.)
    Can be used as Given, When, or Then
    
    Args:
        context: Context fixture from conftest.py
        features: Feature name like "size_changer", "jump_to"
    """
    print(f"   >> Identifying pagination with features: {features}...")
    success = context.pagination_handler.identify_and_store(
        features,
        identifier_type='features'
    )
    assert success, f"Failed to identify pagination with features: {features}"
    print(f"   >> Pagination identified and stored in context")


@when(parsers.parse('I go to page {page_number:d}'))
@then(parsers.parse('I go to page {page_number:d}'))
def step_go_to_page(context, page_number):
    """
    Navigate to a specific page number
    Can be used as When or Then
    
    Args:
        context: Context fixture from conftest.py
        page_number: Page number to navigate to
    """
    print(f"   >> Navigating to page {page_number}...")
    success = context.pagination_handler.go_to_page(page_number, use_context=True)
    assert success, f"Failed to navigate to page {page_number}"
    print(f"   >> Successfully navigated to page {page_number}")


@when('I go to the next page')
@then('I go to the next page')
def step_go_to_next_page(context):
    """
    Navigate to the next page
    Can be used as When or Then
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Navigating to next page...")
    success = context.pagination_handler.next_page(use_context=True)
    assert success, "Failed to navigate to next page"
    print(f"   >> Successfully navigated to next page")


@when('I go to the previous page')
@then('I go to the previous page')
def step_go_to_previous_page(context):
    """
    Navigate to the previous page
    Can be used as When or Then
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Navigating to previous page...")
    success = context.pagination_handler.previous_page(use_context=True)
    assert success, "Failed to navigate to previous page"
    print(f"   >> Successfully navigated to previous page")


@when(parsers.parse('I change page size to {page_size:d}'))
@then(parsers.parse('I change page size to {page_size:d}'))
def step_change_page_size(context, page_size):
    """
    Change the page size (items per page)
    Can be used as When or Then
    
    Args:
        context: Context fixture from conftest.py
        page_size: New page size (e.g., 10, 20, 50, 100)
    """
    print(f"   >> Changing page size to {page_size}...")
    success = context.pagination_handler.select_page_size(page_size, use_context=True)
    assert success, f"Failed to change page size to {page_size}"
    print(f"   >> Successfully changed page size to {page_size}")


@when(parsers.parse('I jump to page {page_number:d}'))
@then(parsers.parse('I jump to page {page_number:d}'))
def step_jump_to_page(context, page_number):
    """
    Jump to a specific page using jump-to input
    Can be used as When or Then
    
    Args:
        context: Context fixture from conftest.py
        page_number: Page number to jump to
    """
    print(f"   >> Jumping to page {page_number}...")
    success = context.pagination_handler.jump_to_page(page_number, use_context=True)
    assert success, f"Failed to jump to page {page_number}"
    print(f"   >> Successfully jumped to page {page_number}")


@then(parsers.parse('I should be on page {page_number:d}'))
def step_verify_current_page(context, page_number):
    """
    Verify the current active page number
    
    Args:
        context: Context fixture from conftest.py
        page_number: Expected page number
    """
    print(f"   >> Verifying current page is {page_number}...")
    current_page = context.pagination_handler.get_current_page(use_context=True)
    assert current_page is not None, "Could not determine current page"
    assert current_page == page_number, f"Expected page {page_number}, but current page is {current_page}"
    print(f"   >> Verification passed: Current page is {current_page}")


@then(parsers.parse('I should see {count:d} total pages'))
def step_verify_total_pages(context, count):
    """
    Verify the total number of pages
    
    Args:
        context: Context fixture from conftest.py
        count: Expected total pages
    """
    print(f"   >> Verifying total pages is {count}...")
    total_pages = context.pagination_handler.get_total_pages(use_context=True)
    assert total_pages is not None, "Could not determine total pages"
    assert total_pages == count, f"Expected {count} total pages, but found {total_pages}"
    print(f"   >> Verification passed: Total pages is {total_pages}")


@then(parsers.parse('the page size should be {page_size:d}'))
def step_verify_page_size(context, page_size):
    """
    Verify the current page size
    
    Args:
        context: Context fixture from conftest.py
        page_size: Expected page size
    """
    print(f"   >> Verifying page size is {page_size}...")
    current_size = context.pagination_handler.get_current_page_size(use_context=True)
    assert current_size is not None, "Could not determine page size"
    assert current_size == page_size, f"Expected page size {page_size}, but current size is {current_size}"
    print(f"   >> Verification passed: Page size is {current_size}")


@then('I should see a summary of the pagination')
def step_show_pagination_summary(context):
    """
    Print a summary of pagination state
    
    Args:
        context: Context fixture from conftest.py
    """
    print(f"   >> Generating pagination summary...")
    context.pagination_handler.print_pagination_summary(use_context=True)


@then(parsers.parse('the context should contain pagination with key "{context_key}"'))
def step_verify_pagination_in_context(context, context_key):
    """
    Verify that pagination is stored in context with the specified key
    
    Args:
        context: Context fixture from conftest.py
        context_key: Expected context key
    """
    print(f"   >> Verifying pagination in context with key '{context_key}'...")
    element_info = context.element_context.get_element(context_key)
    assert element_info is not None, f"Pagination not found in context with key '{context_key}'"
    assert element_info.element_type == 'pagination', f"Element in context is not a pagination (type: {element_info.element_type})"
    print(f"   >> Verification passed: Pagination found in context with key '{context_key}'")

