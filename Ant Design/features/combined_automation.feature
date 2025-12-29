Feature: Combined Ant Design Component Automation
  As a QA tester
  I want to automate interactions with buttons, inputs, and dropdowns in a single flow
  So that I can test the complete user journey across different Ant Design components

  Scenario: Complete workflow - Button, Input, and Dropdown
    Given I am on the button page
    When I pressed the primary button
    Then I go to the input page
    And I type Sample Text Value in the text field
    Then I go to the dropdown page
    And I select first option from dropdown

  Scenario: Simple button and password input workflow
    Given I am on the button page
    When I pressed the primary button
    Then I go to the input page
    And I type TestPassword123 in the password field
    Then I go to the dropdown page
    And I select first option from dropdown

  Scenario: Multiple button clicks and form filling
    Given I am on the button page
    When I pressed the default button
    And I pressed the dashed button
    Then I go to the input page
    When I type Test Input Value in the text field
    And I type TestPassword123 in the password field
    Then I go to the dropdown page
    When I select 2nd menu item from dropdown

  Scenario: Natural workflow with labels
    Given I am on the button page
    When I pressed the primary button
    Then I go to the input page
    And I type MyUsername in the username field
    And I type MyPassword123 in the password field
    Then I go to the dropdown page
    When I select Pakistan from country dropdown
