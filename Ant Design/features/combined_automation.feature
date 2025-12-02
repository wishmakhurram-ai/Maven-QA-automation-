Feature: Combined Ant Design Component Automation
  As a QA tester
  I want to automate interactions with buttons, inputs, and dropdowns in a single flow
  So that I can test the complete user journey across different Ant Design components

  Scenario: Complete workflow - Button, Input, and Dropdown
    # Step 1: Navigate to button page and click a button
    Given I am on the button page
    When I click the primary button
    Then the button should be clicked successfully
    
    # Step 2: Navigate to input page and fill an input
    And I am on the input page
    When I fill first text input with Sample Text Value
    Then I should see a summary of all inputs
    
    # Step 3: Navigate to dropdown page and select from dropdown
    And I am on the dropdown page
    And I identify the dropdown at position "2"
    When I select the option from context with "1st menu item"
    Then the context should contain dropdown with key "2"

  Scenario: Multiple interactions workflow
    # Button interactions
    Given I am on the button page
    When I click the default button
    Then the button should be clicked successfully
    And I click the dashed button
    Then the button should be clicked successfully
    
    # Input interactions
    And I am on the input page
    When I fill first text input with Test Input Value
    Then I should see a summary of all inputs
    And I fill first password input with TestPassword123
    Then the password field should be filled
    
    # Dropdown interactions
    And I am on the dropdown page
    And I identify the dropdown at position "3"
    When I select the option from context with "2nd menu item"
    Then the context should contain dropdown with key "3"

  Scenario: Context-driven workflow
    # Button with context
    Given I am on the button page
    And I identify the "primary" type button
    When I click the button from context
    Then the button should be clicked successfully
    
    # Input with context
    And I am on the input page
    And I identify the input with label "Basic usage"
    When I fill the input from context with "Context Input Value"
    Then I should see a summary of all inputs
    
    # Dropdown with context
    And I am on the dropdown page
    And I identify the dropdown at position "4"
    When I select the option from context with "3rd menu item"
    Then the context should contain dropdown with key "4"

  Scenario: Semantic identification workflow
    # Button by type (more reliable than text)
    Given I am on the button page
    When I click the primary button
    Then the button should be clicked successfully
    
    # Input by label
    And I am on the input page
    When I fill the input with label "Basic usage" with "Semantic Input Value"
    Then I should see a summary of all inputs
    
    # Dropdown by label
    And I am on the dropdown page
    When I select 1st menu item in dropdown "Basic"
    Then I should see a summary of all dropdowns

