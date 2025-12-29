Feature: Ant Design Table Automation
  As a test automation engineer
  I want to automatically detect and interact with Ant Design tables
  So that I can test table functionality without hardcoded selectors

  Background:
    Given I am on the table page

  @table @smoke
  Scenario: Detect and read Ant Design table
    Given I identify the first table
    When I print the table summary
    And I read all rows from the table
    Then the table should have at least 1 row
    And the table should have at least 1 column

  @table @smoke
  Scenario: Read table cell value by column name
    Given I identify the first table
    When I read the cell value from column "Name" at row 0
    Then the cell value should not be empty

  @table @smoke
  Scenario: Find row by column value
    Given I identify the first table
    When I read all rows from the table
    And I find the row with column "Name" equal to "John"
    Then the row should be found

  @table
  Scenario: Sort table by column
    Given I identify the first table
    When I sort the table by column "Name" in asc order
    Then the table should be sorted

  @table
  Scenario: Test table pagination
    Given I identify the first table
    When I print the table summary
    And the table has pagination
    When I go to the next page
    Then the table should load new data

  @table
  Scenario: Test table row selection
    Given I identify the first table
    When the table has row selection
    And I select the row with column "Name" equal to "John"
    Then the row should be selected

  @table
  Scenario: Test expandable rows
    Given I identify the first table
    When the table has expandable rows
    And I expand row at index 0
    And I read expanded content from row at index 0
    Then the expanded content should not be empty













