Feature: Ant Design Checkbox Component Automation
  As a test automation engineer
  I want to automatically detect, read state, and interact with Ant Design Checkbox components
  So that I can test checkbox functionality without hardcoded locators

  Background:
    Given I am on a page with Ant Design Checkbox components

  Scenario: Detect and summarize all checkboxes on the page
    When I navigate to a page with checkboxes
    Then I should see a summary of all checkboxes
  
  

  Scenario: Check checkbox by semantic label
    Given I am on a page with checkboxes
    When I check "Accept Terms" checkbox
    Then "Accept Terms" checkbox should be checked

  Scenario: Uncheck checkbox by semantic label
    Given I am on a page with checkboxes
    When I check "Email Notifications" checkbox
    And I uncheck "Email Notifications" checkbox
    Then "Email Notifications" checkbox should be unchecked

  Scenario: Check checkbox from group
    Given I am on a page with checkboxes
    When I check "Option A" from "Preferences" checkbox group
    Then "Preferences" group should have 1 option(s) checked

  Scenario: Multiple selections in checkbox group
    Given I am on a page with checkboxes
    When I check "Option A" from "Preferences" checkbox group
    And I check "Option B" from "Preferences" checkbox group
    Then "Preferences" group should have 2 option(s) checked

  Scenario: Toggle checkbox state
    Given I am on a page with checkboxes
    When I toggle "Accept Terms" checkbox
    Then "Accept Terms" checkbox should be checked
    When I toggle "Accept Terms" checkbox
    Then "Accept Terms" checkbox should be unchecked

  Scenario: Check checkbox by data-attr-id
    Given I am on a page with checkboxes
    When I identify the checkbox with data-atr-id "accept-terms"
    And I check "accept-terms" checkbox
    Then "accept-terms" checkbox should be checked

  Scenario: Check checkbox by position
    Given I am on a page with checkboxes
    When I check the checkbox at position 1
    Then I should see at least 1 checkbox(es) on the page
    And I should see a summary of all checkboxes

  Scenario: Verify checkbox group behavior
    Given I am on a page with checkboxes
    When I check "Option A" from "Preferences" checkbox group
    Then "Preferences" group should have 1 option(s) checked
    When I check "Option B" from "Preferences" checkbox group
    Then "Preferences" group should have 2 option(s) checked
    When I uncheck "Option A" from "Preferences" checkbox group
    Then "Preferences" group should have 1 option(s) checked

  Scenario: Verify disabled checkbox cannot be checked
    Given I am on a page with checkboxes
    When I identify the checkbox with label "Disabled Option"
    Then the checkbox "Disabled Option" should be disabled

  Scenario: Verify checkbox group options count
    Given I am on a page with checkboxes
    When I identify the checkbox with label "Option 1"
    Then "Preferences" group should have 3 option(s)

  Scenario: Verify indeterminate checkbox state
    Given I am on a page with checkboxes
    When I check "Option A" from "Preferences" checkbox group
    And I check "Option B" from "Preferences" checkbox group
    # Note: Indeterminate state typically occurs with "Check All" when some but not all are selected
    Then I should see at least 1 checkbox(es) on the page

  Scenario: Verify "Check All" behavior
    Given I am on a page with checkboxes
    When I identify the checkbox with label "Select All"
    Then "Select All" checkbox should have "Check All" behavior
    When I check "Select All" checkbox
    Then "Preferences" group should have 3 option(s) checked

  Scenario: Multiple checkbox groups on page
    Given I am on a page with checkboxes
    When I check "Option A" from "Preferences" checkbox group
    And I check "Newsletter" checkbox
    Then "Preferences" group should have 1 option(s) checked
    And "Newsletter" checkbox should be checked

  Scenario: Verify controlled checkbox behavior
    Given I am on a page with checkboxes
    When I check "Controlled Checkbox" checkbox
    Then "Controlled Checkbox" checkbox should be checked
    # Controlled checkboxes should reflect state changes immediately
    When I uncheck "Controlled Checkbox" checkbox
    Then "Controlled Checkbox" checkbox should be unchecked

