"""
Gherkin step definitions for DatePicker automation using pytest-bdd
pytest-bdd automatically discovers and loads these step definitions
PRIORITY: data-attr-id is used first to determine DatePicker type and location
"""
from pytest_bdd import given, when, then, parsers
from framework.components.datepicker_handler import DatePickerHandler

# Ant Design DatePicker page URL
DATEPICKER_PAGE_URL = "https://ant.design/components/date-picker"


@given(parsers.parse('I am on the date-picker page'))
def step_navigate_to_datepicker_page(context):
    """Navigate to Ant Design DatePicker page"""
    print(f"   >> Navigating to DatePicker page: {DATEPICKER_PAGE_URL}")
    context.driver.get(DATEPICKER_PAGE_URL)
    print(f"   >> Page loaded successfully")


@given(parsers.parse('I identify the datepicker with label "{label_text}"'))
@when(parsers.parse('I identify the datepicker with label "{label_text}"'))
@then(parsers.parse('I identify the datepicker with label "{label_text}"'))
def step_identify_datepicker_by_label(context, label_text):
    """
    Identify a DatePicker by label text (semantic matching)
    Can be used as Given, When, or Then (for use with And after other steps)
    
    Args:
        context: Context fixture from conftest.py
        label_text: Label text to search for
    """
    print(f"   >> Identifying DatePicker with label: '{label_text}'...")
    success = context.datepicker_handler.identify_and_store(
        label_text,
        identifier_type='label'
    )
    assert success, f"Failed to identify DatePicker with label '{label_text}'"
    print(f"   >> DatePicker identified and stored in context")


@when(parsers.parse('I select "{date_str}" in "{identifier}" datepicker'))
def step_select_date(context, date_str, identifier):
    """
    Select a date in a DatePicker
    
    Args:
        context: Context fixture from conftest.py
        date_str: Date string in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:mm:ss'
        identifier: DatePicker identifier (label, data-attr-id, etc.)
    """
    print(f"   >> Selecting date '{date_str}' in DatePicker '{identifier}'...")
    success = context.datepicker_handler.select_date(
        identifier,
        date_str,
        identifier_type='auto'
    )
    assert success, f"Failed to select date '{date_str}' in DatePicker '{identifier}'"
    print(f"   >> Date selected successfully")


@when(parsers.parse('I select date range from "{start_date}" to "{end_date}" in "{identifier}" datepicker'))
def step_select_date_range(context, start_date, end_date, identifier):
    """
    Select a date range in a RangePicker
    
    Args:
        context: Context fixture from conftest.py
        start_date: Start date string in format 'YYYY-MM-DD'
        end_date: End date string in format 'YYYY-MM-DD'
        identifier: RangePicker identifier
    """
    print(f"   >> Selecting date range '{start_date}' to '{end_date}' in DatePicker '{identifier}'...")
    success = context.datepicker_handler.select_date_range(
        identifier,
        start_date,
        end_date,
        identifier_type='auto'
    )
    assert success, f"Failed to select date range in DatePicker '{identifier}'"
    print(f"   >> Date range selected successfully")


@when(parsers.parse('I select multiple dates "{dates_str}" in "{identifier}" datepicker'))
def step_select_multiple_dates(context, dates_str, identifier):
    """
    Select multiple dates in a Multiple DatePicker
    
    Args:
        context: Context fixture from conftest.py
        dates_str: Comma-separated date strings
        identifier: DatePicker identifier
    """
    dates = [d.strip() for d in dates_str.split(',')]
    print(f"   >> Selecting multiple dates {dates} in DatePicker '{identifier}'...")
    success = context.datepicker_handler.select_multiple_dates(
        identifier,
        dates,
        identifier_type='auto'
    )
    assert success, f"Failed to select multiple dates in DatePicker '{identifier}'"
    print(f"   >> Multiple dates selected successfully")


@when(parsers.parse('I clear "{identifier}" datepicker'))
def step_clear_datepicker(context, identifier):
    """
    Clear selected value(s) from a DatePicker
    
    Args:
        context: Context fixture from conftest.py
        identifier: DatePicker identifier
    """
    print(f"   >> Clearing DatePicker '{identifier}'...")
    success = context.datepicker_handler.clear_datepicker(
        identifier,
        identifier_type='auto'
    )
    assert success, f"Failed to clear DatePicker '{identifier}'"
    print(f"   >> DatePicker cleared successfully")


@when(parsers.parse('I select preset "{preset_text}" in "{identifier}" datepicker'))
def step_select_preset(context, preset_text, identifier):
    """
    Select a preset/quick-select range
    
    Args:
        context: Context fixture from conftest.py
        preset_text: Text of the preset to select
        identifier: DatePicker identifier
    """
    print(f"   >> Selecting preset '{preset_text}' in DatePicker '{identifier}'...")
    success = context.datepicker_handler.select_preset(
        identifier,
        preset_text,
        identifier_type='auto'
    )
    assert success, f"Failed to select preset '{preset_text}' in DatePicker '{identifier}'"
    print(f"   >> Preset selected successfully")


@when(parsers.parse('I open "{identifier}" datepicker'))
def step_open_datepicker(context, identifier):
    """
    Open a DatePicker calendar popup
    
    Args:
        context: Context fixture from conftest.py
        identifier: DatePicker identifier
    """
    print(f"   >> Opening DatePicker '{identifier}'...")
    success = context.datepicker_handler.open_datepicker(
        identifier,
        identifier_type='auto'
    )
    assert success, f"Failed to open DatePicker '{identifier}'"
    print(f"   >> DatePicker opened successfully")


@when(parsers.parse('I close "{identifier}" datepicker'))
def step_close_datepicker(context, identifier):
    """
    Close a DatePicker calendar popup
    
    Args:
        context: Context fixture from conftest.py
        identifier: DatePicker identifier
    """
    print(f"   >> Closing DatePicker '{identifier}'...")
    success = context.datepicker_handler.close_datepicker(
        identifier,
        identifier_type='auto'
    )
    assert success, f"Failed to close DatePicker '{identifier}'"
    print(f"   >> DatePicker closed successfully")


@when(parsers.parse('I select "{date_str}" in first datepicker'))
def step_select_date_in_first_datepicker(context, date_str):
    """Select a date in the first DatePicker on the page"""
    print(f"   >> Selecting date '{date_str}' in first DatePicker...")
    success = context.datepicker_handler.select_date(
        "1",
        date_str,
        identifier_type='position'
    )
    assert success, f"Failed to select date '{date_str}' in first DatePicker"
    print(f"   >> Date selected successfully")


@when(parsers.parse('I select "{date_str}" in datepicker at position "{position}"'))
def step_select_date_by_position(context, date_str, position):
    """Select a date in a DatePicker by position"""
    print(f"   >> Selecting date '{date_str}' in DatePicker at position {position}...")
    success = context.datepicker_handler.select_date(
        position,
        date_str,
        identifier_type='position'
    )
    assert success, f"Failed to select date '{date_str}' in DatePicker at position {position}"
    print(f"   >> Date selected successfully")


@when(parsers.parse('I select week containing "{date_str}" in "{identifier}" datepicker'))
def step_select_week(context, date_str, identifier):
    """Select a week containing the given date"""
    print(f"   >> Selecting week containing '{date_str}' in DatePicker '{identifier}'...")
    success = context.datepicker_handler.select_date(
        identifier,
        date_str,
        identifier_type='auto'
    )
    assert success, f"Failed to select week in DatePicker '{identifier}'"
    print(f"   >> Week selected successfully")


@when(parsers.parse('I select month "{month_str}" in "{identifier}" datepicker'))
def step_select_month(context, month_str, identifier):
    """Select a month (format: YYYY-MM)"""
    # Convert YYYY-MM to YYYY-MM-01 for date selection
    date_str = f"{month_str}-01"
    print(f"   >> Selecting month '{month_str}' in DatePicker '{identifier}'...")
    success = context.datepicker_handler.select_date(
        identifier,
        date_str,
        identifier_type='auto'
    )
    assert success, f"Failed to select month '{month_str}' in DatePicker '{identifier}'"
    print(f"   >> Month selected successfully")


@when(parsers.parse('I select quarter "{quarter_str}" in "{identifier}" datepicker'))
def step_select_quarter(context, quarter_str, identifier):
    """Select a quarter (format: YYYY-Q1, YYYY-Q2, etc.)"""
    # Convert quarter to date (first day of quarter)
    year, quarter = quarter_str.split('-Q')
    month = (int(quarter) - 1) * 3 + 1
    date_str = f"{year}-{month:02d}-01"
    print(f"   >> Selecting quarter '{quarter_str}' in DatePicker '{identifier}'...")
    success = context.datepicker_handler.select_date(
        identifier,
        date_str,
        identifier_type='auto'
    )
    assert success, f"Failed to select quarter '{quarter_str}' in DatePicker '{identifier}'"
    print(f"   >> Quarter selected successfully")


@when(parsers.parse('I select year "{year_str}" in "{identifier}" datepicker'))
def step_select_year(context, year_str, identifier):
    """Select a year"""
    # Convert year to date (first day of year)
    date_str = f"{year_str}-01-01"
    print(f"   >> Selecting year '{year_str}' in DatePicker '{identifier}'...")
    success = context.datepicker_handler.select_date(
        identifier,
        date_str,
        identifier_type='auto'
    )
    assert success, f"Failed to select year '{year_str}' in DatePicker '{identifier}'"
    print(f"   >> Year selected successfully")


@when(parsers.parse('I select date "{date_str}" in the datepicker from context'))
def step_select_date_from_context(context, date_str):
    """Select a date in the DatePicker from context"""
    print(f"   >> Selecting date '{date_str}' in DatePicker from context...")
    # Get element from context and use its identifier
    element_info = context.context.get_current()
    if not element_info:
        assert False, "No DatePicker found in context"
    
    identifier = element_info.data_attr_id or element_info.metadata.get('label', '')
    success = context.datepicker_handler.select_date(
        identifier,
        date_str,
        identifier_type='auto'
    )
    assert success, f"Failed to select date '{date_str}' in DatePicker from context"
    print(f"   >> Date selected successfully")


@when(parsers.parse('I request a summary of all DatePickers'))
def step_request_datepicker_summary(context):
    """Request a summary of all DatePickers on the page"""
    print(f"   >> Requesting DatePicker summary...")
    context.datepicker_handler.print_datepickers_summary()


@then(parsers.parse('"{identifier}" datepicker should have value "{expected_value}"'))
def step_verify_datepicker_value(context, identifier, expected_value):
    """
    Verify DatePicker has the expected value
    
    Args:
        context: Context fixture from conftest.py
        identifier: DatePicker identifier
        expected_value: Expected value string
    """
    print(f"   >> Verifying DatePicker '{identifier}' has value '{expected_value}'...")
    actual_value = context.datepicker_handler.get_datepicker_value(
        identifier,
        identifier_type='auto'
    )
    
    # Normalize values for comparison
    if isinstance(actual_value, dict):
        # For range picker, check if expected value is in the range
        start = actual_value.get('start', '')
        end = actual_value.get('end', '')
        assert expected_value in start or expected_value in end, \
            f"Expected '{expected_value}' but got range '{start}' to '{end}'"
    elif isinstance(actual_value, list):
        # For multiple picker, check if expected value is in the list
        assert expected_value in str(actual_value), \
            f"Expected '{expected_value}' but got {actual_value}"
    else:
        assert expected_value in str(actual_value), \
            f"Expected '{expected_value}' but got '{actual_value}'"
    
    print(f"   >> Value verified successfully")


@then(parsers.parse('"{identifier}" datepicker should be empty'))
def step_verify_datepicker_empty(context, identifier):
    """Verify DatePicker is empty"""
    print(f"   >> Verifying DatePicker '{identifier}' is empty...")
    actual_value = context.datepicker_handler.get_datepicker_value(
        identifier,
        identifier_type='auto'
    )
    
    if isinstance(actual_value, dict):
        assert not actual_value.get('start') and not actual_value.get('end'), \
            f"DatePicker is not empty: {actual_value}"
    elif isinstance(actual_value, list):
        assert len(actual_value) == 0, \
            f"DatePicker is not empty: {actual_value}"
    else:
        assert not actual_value or actual_value == '', \
            f"DatePicker is not empty: '{actual_value}'"
    
    print(f"   >> DatePicker is empty")


@then(parsers.parse('"{identifier}" date range should be selected correctly'))
def step_verify_date_range(context, identifier):
    """Verify date range is selected correctly"""
    print(f"   >> Verifying date range in DatePicker '{identifier}'...")
    actual_value = context.datepicker_handler.get_datepicker_value(
        identifier,
        identifier_type='auto'
    )
    
    assert isinstance(actual_value, dict), \
        f"Expected date range but got {type(actual_value)}"
    assert actual_value.get('start') or actual_value.get('end'), \
        f"Date range is empty: {actual_value}"
    
    print(f"   >> Date range verified successfully")


@then(parsers.parse('"{identifier}" datepicker should have multiple values'))
def step_verify_multiple_values(context, identifier):
    """Verify DatePicker has multiple values"""
    print(f"   >> Verifying multiple values in DatePicker '{identifier}'...")
    actual_value = context.datepicker_handler.get_datepicker_value(
        identifier,
        identifier_type='auto'
    )
    
    assert isinstance(actual_value, list), \
        f"Expected list of values but got {type(actual_value)}"
    assert len(actual_value) > 0, \
        f"DatePicker has no values: {actual_value}"
    
    print(f"   >> Multiple values verified successfully")


@then(parsers.parse('"{identifier}" datepicker should have a value'))
def step_verify_datepicker_has_value(context, identifier):
    """Verify DatePicker has any value"""
    print(f"   >> Verifying DatePicker '{identifier}' has a value...")
    actual_value = context.datepicker_handler.get_datepicker_value(
        identifier,
        identifier_type='auto'
    )
    
    if isinstance(actual_value, dict):
        assert actual_value.get('start') or actual_value.get('end'), \
            f"DatePicker has no value: {actual_value}"
    elif isinstance(actual_value, list):
        assert len(actual_value) > 0, \
            f"DatePicker has no value: {actual_value}"
    else:
        assert actual_value and actual_value != '', \
            f"DatePicker has no value: '{actual_value}'"
    
    print(f"   >> DatePicker has a value")


@then(parsers.parse('"{identifier}" datepicker should be disabled'))
def step_verify_datepicker_disabled(context, identifier):
    """Verify DatePicker is disabled"""
    print(f"   >> Verifying DatePicker '{identifier}' is disabled...")
    element = context.datepicker_handler._find_datepicker(identifier, 'auto', timeout=10)
    assert element, f"DatePicker '{identifier}' not found"
    
    picker_info = context.datepicker_handler.identifier.identify_datepicker_type(element)
    assert picker_info.get('disabled', False), \
        f"DatePicker '{identifier}' is not disabled"
    
    print(f"   >> DatePicker is disabled")


@then(parsers.parse('"{identifier}" datepicker should be read-only'))
def step_verify_datepicker_readonly(context, identifier):
    """Verify DatePicker is read-only"""
    print(f"   >> Verifying DatePicker '{identifier}' is read-only...")
    element = context.datepicker_handler._find_datepicker(identifier, 'auto', timeout=10)
    assert element, f"DatePicker '{identifier}' not found"
    
    picker_info = context.datepicker_handler.identifier.identify_datepicker_type(element)
    assert picker_info.get('readonly', False), \
        f"DatePicker '{identifier}' is not read-only"
    
    print(f"   >> DatePicker is read-only")


@then(parsers.parse('"{identifier}" datepicker should be open'))
def step_verify_datepicker_open(context, identifier):
    """Verify DatePicker calendar is open"""
    print(f"   >> Verifying DatePicker '{identifier}' is open...")
    element = context.datepicker_handler._find_datepicker(identifier, 'auto', timeout=10)
    assert element, f"DatePicker '{identifier}' not found"
    
    picker_info = context.datepicker_handler.identifier.identify_datepicker_type(element)
    assert picker_info.get('open', False), \
        f"DatePicker '{identifier}' is not open"
    
    print(f"   >> DatePicker is open")


@then(parsers.parse('"{identifier}" datepicker should be closed'))
def step_verify_datepicker_closed(context, identifier):
    """Verify DatePicker calendar is closed"""
    print(f"   >> Verifying DatePicker '{identifier}' is closed...")
    element = context.datepicker_handler._find_datepicker(identifier, 'auto', timeout=10)
    assert element, f"DatePicker '{identifier}' not found"
    
    picker_info = context.datepicker_handler.identifier.identify_datepicker_type(element)
    assert not picker_info.get('open', False), \
        f"DatePicker '{identifier}' is not closed"
    
    print(f"   >> DatePicker is closed")


@then(parsers.parse('first datepicker should have value "{expected_value}"'))
def step_verify_first_datepicker_value(context, expected_value):
    """Verify first DatePicker has the expected value"""
    step_verify_datepicker_value(context, "1", expected_value)


@then(parsers.parse('datepicker at position "{position}" should have value "{expected_value}"'))
def step_verify_datepicker_by_position_value(context, position, expected_value):
    """Verify DatePicker at position has the expected value"""
    step_verify_datepicker_value(context, position, expected_value)


@then(parsers.parse('the datepicker from context should have value "{expected_value}"'))
def step_verify_datepicker_from_context_value(context, expected_value):
    """Verify DatePicker from context has the expected value"""
    element_info = context.context.get_current()
    assert element_info, "No DatePicker found in context"
    
    identifier = element_info.data_attr_id or element_info.metadata.get('label', '')
    step_verify_datepicker_value(context, identifier, expected_value)


@then(parsers.parse('I should see a summary of all DatePickers'))
def step_verify_datepicker_summary(context):
    """Verify DatePicker summary is displayed"""
    print(f"   >> Verifying DatePicker summary...")
    summary = context.datepicker_handler.get_all_datepickers_summary()
    assert summary['total'] > 0, "No DatePickers found on the page"
    print(f"   >> Summary verified: {summary['total']} DatePickers found")
