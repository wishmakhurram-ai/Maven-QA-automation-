
Feature: Ant Design DatePicker Automation
  As a user
  I want to interact with DatePicker components on the Ant Design date-picker page
  So that I can test all DatePicker types automatically

  # Basic DatePicker Scenarios
  Scenario: Select date in basic DatePicker
    Given I am on the date-picker page
    When I select "2026-01-15" in "Start Date" datepicker
    Then "Start Date" datepicker should have value "2026-01-15"

  Scenario: Select date with time selection
    Given I am on the date-picker page
    When I select "2026-01-15 14:30:00" in "Delivery Date" datepicker
    Then "Delivery Date" datepicker should have value "2026-01-15 14:30:00"

  Scenario: Select date range in RangePicker
    Given I am on the date-picker page
    When I select date range from "2026-01-01" to "2026-01-31" in "Booking Period" datepicker
    Then "Booking Period" date range should be selected correctly

  Scenario: Clear DatePicker value
    Given I am on the date-picker page
    And I select "2026-01-15" in "Start Date" datepicker
    When I clear "Start Date" datepicker
    Then "Start Date" datepicker should be empty

  Scenario: Select week in WeekPicker
    Given I am on the date-picker page
    When I select week containing "2026-01-15" in "Week" datepicker
    Then "Week" datepicker should have a value

  Scenario: Select month in MonthPicker
    Given I am on the date-picker page
    When I select month "2026-01" in "Month" datepicker
    Then "Month" datepicker should have value "2026-01"

  Scenario: Select quarter in QuarterPicker
    Given I am on the date-picker page
    When I select quarter "2026-Q1" in "Quarter" datepicker
    Then "Quarter" datepicker should have a value

  Scenario: Select year in YearPicker
    Given I am on the date-picker page
    When I select year "2026" in "Year" datepicker
    Then "Year" datepicker should have value "2026"

  Scenario: Select multiple dates
    Given I am on the date-picker page
    When I select multiple dates "2026-01-15,2026-01-20,2026-01-25" in "Multiple Dates" datepicker
    Then "Multiple Dates" datepicker should have multiple values

  Scenario: Select preset range
    Given I am on the date-picker page
    When I select preset "Today" in "Booking Period" datepicker
    Then "Booking Period" date range should be selected correctly

  Scenario: Verify DatePicker is disabled
    Given I am on the date-picker page
    Then "Disabled Date" datepicker should be disabled

  Scenario: Verify DatePicker is read-only
    Given I am on the date-picker page
    Then "Read-only Date" datepicker should be read-only

  Scenario: Get DatePicker summary
    Given I am on the date-picker page
    When I request a summary of all DatePickers
    Then I should see a summary of all DatePickers

  # Position-based scenarios
  Scenario: Select date in first DatePicker
    Given I am on the date-picker page
    When I select "2026-01-15" in first datepicker
    Then first datepicker should have value "2026-01-15"

  Scenario: Select date in DatePicker by position
    Given I am on the date-picker page
    When I select "2026-01-15" in datepicker at position "2"
    Then datepicker at position "2" should have value "2026-01-15"

  # Context-driven scenarios
  Scenario: Identify and select date using context
    Given I am on the date-picker page
    And I identify the datepicker with label "Start Date"
    When I select date "2026-01-15" in the datepicker from context
    Then the datepicker from context should have value "2026-01-15"

  Scenario: Open and close DatePicker
    Given I am on the date-picker page
    When I open "Start Date" datepicker
    Then "Start Date" datepicker should be open
    When I close "Start Date" datepicker
    Then "Start Date" datepicker should be closed
