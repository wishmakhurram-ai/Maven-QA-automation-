Feature: Ant Design Radio Component Automation
  As a test automation engineer
  I want to automatically detect, read state, and select Ant Design Radio components
  So that I can test radio functionality without hardcoded locators

  Background:
    Given I am on a page with Ant Design Radio components

  Scenario: Detect and summarize all radios on the page
    When I navigate to a page with radios
    Then I should see a summary of all radios
  
  

  Scenario: Select radio by semantic label
    Given I am on a page with radios
    When I select "Apple" radio option
    Then "Apple" radio option should be selected

  Scenario: Select radio from group
    Given I am on a page with radios
    When I select "Visa" radio from "Payment Method" group
    Then "Payment Method" group should have "Visa" selected
    And only one radio option should be selected in "Payment Method" group

  Scenario: Select radio by data-attr-id
    Given I am on a page with radios
    When I identify the radio with data-atr-id "gender-male"
    And I select "gender-male" radio option
    Then "gender-male" radio option should be selected

  Scenario: Select radio by position
    Given I am on a page with radios
    When I select the radio at position 1
    Then I should see at least 1 radio(s) on the page
    And I should see a summary of all radios

  Scenario: Verify radio group behavior
    Given I am on a page with radios
    When I select "Option A" radio from "Options" group
    Then "Options" group should have "Option A" selected
    And only one radio option should be selected in "Options" group
    When I select "Option B" radio from "Options" group
    Then "Options" group should have "Option B" selected
    And "Option A" radio option should not be selected

  Scenario: Verify disabled radio cannot be selected
    Given I am on a page with radios
    When I identify the radio with label "Disabled Option"
    Then the radio "Disabled Option" should be disabled

  Scenario: Verify radio group options count
    Given I am on a page with radios
    When I identify the radio with label "Option 1"
    Then "Options" group should have 3 option(s)

  Scenario: Multiple radio groups on page
    Given I am on a page with radios
    When I select "Male" radio from "Gender" group
    And I select "Visa" radio from "Payment Method" group
    Then "Gender" group should have "Male" selected
    And "Payment Method" group should have "Visa" selected
    And only one radio option should be selected in "Gender" group
    And only one radio option should be selected in "Payment Method" group
    Then I should see a summary of all radios

