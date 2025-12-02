Feature: Ant Design Dropdown Menu Automation
  As a QA tester
  I want to interact with different Ant Design dropdown menus
  So that I can verify each dropdown works correctly and select menu items from specific dropdowns

  Background:
    Given I am on the dropdown page

  # Story 1: Position-Based Selection (Guarantees Different Dropdowns)
  # Each position number targets a DIFFERENT dropdown element
  # Context is cleared at the start of each "identify" step to ensure fresh start
  Scenario: Select from dropdown at position 2
    Given I am on the dropdown page
    And I identify the dropdown at position "2"
    When I select the option from context with "1st menu item"
    Then the context should contain dropdown with key "2"
    And I verify this is a different dropdown from previous scenarios

  Scenario: Select from dropdown at position 3
    Given I am on the dropdown page
    And I identify the dropdown at position "3"
    When I select the option from context with "1st menu item"
    Then the context should contain dropdown with key "3"
    And I verify this is a different dropdown from previous scenarios

  Scenario: Select from dropdown at position 4
    Given I am on the dropdown page
    And I identify the dropdown at position "4"
    When I select the option from context with "1st menu item"
    Then the context should contain dropdown with key "4"
    And I verify this is a different dropdown from previous scenarios

  # Story 2: Unique Label-Based Selection (Only Unique Labels)
  Scenario: Select from "Click me" dropdown by label
    Given I am on the dropdown page
    And I identify the dropdown with label "Click me"
    When I select the option from context with "2nd menu item"
    Then the context should contain dropdown with key "Click me"

  Scenario: Select from "Cascading menu" dropdown by label
    Given I am on the dropdown page
    And I identify the dropdown with label "Cascading menu"
    When I select the option from context with "1st menu item"
    Then the context should contain dropdown with key "Cascading menu"

  Scenario: Select from "Button" dropdown by label
    Given I am on the dropdown page
    And I identify the dropdown with label "Button"
    When I select the option from context with "1st menu item"
    Then the context should contain dropdown with key "Button"

  Scenario: Select from "Selectable" dropdown by label
    Given I am on the dropdown page
    And I identify the dropdown with label "Selectable"
    When I select the option from context with "1st menu item"
    Then the context should contain dropdown with key "Selectable"

  # Story 3: Multiple Different Dropdowns in Sequence (Using Positions)
  Scenario: Select from three different dropdowns using positions
    Given I am on the dropdown page
    And I identify the dropdown at position "2"
    When I select the option from context with "1st menu item"
    And I identify the dropdown at position "3"
    And I select the option from context with "1st menu item"
    And I identify the dropdown at position "4"
    And I select the option from context with "1st menu item"
    Then I should see a summary of all dropdowns

  Scenario: Select from five different dropdowns using positions
    Given I am on the dropdown page
    And I identify the dropdown at position "5"
    When I select the option from context with "1st menu item"
    And I identify the dropdown at position "6"
    And I select the option from context with "1st menu item"
    And I identify the dropdown at position "7"
    And I select the option from context with "1st menu item"
    And I identify the dropdown at position "8"
    And I select the option from context with "1st menu item"
    And I identify the dropdown at position "9"
    And I select the option from context with "1st menu item"
    Then I should see a summary of all dropdowns

  # Story 4: Verification
  Scenario: View all dropdowns summary
    Given I am on the dropdown page
    Then I should see a summary of all dropdowns

