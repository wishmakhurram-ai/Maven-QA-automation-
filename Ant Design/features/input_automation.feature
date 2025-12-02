
    
Feature: Ant Design Input Field Automation
  As a user
  I want to fill input fields on the Ant Design input page
  So that I can interact with all input types automatically

  # Direct Type-Based Scenarios (No Context)
  Scenario: Fill text input by type
    Given I am on the input page
    When I fill first text input with Sample Text Value
    Then I should see a summary of all inputs

  Scenario: Fill password input by type
    Given I am on the input page
    When I fill first password input with TestPassword123
    Then the password field should be filled

  Scenario: Fill search input by type
    Given I am on the input page
    When I fill first search input with test search query
    Then I should see a summary of all inputs

  Scenario: Fill textarea by type
    Given I am on the input page
    When I fill first textarea input with This is a sample textarea content for testing
    Then I should see a summary of all inputs

  Scenario: Fill multiple inputs by type
    Given I am on the input page
    When I fill first text input with First Text Input
    And I fill first password input with Password123
    And I fill first search input with search query
    Then I should see a summary of all inputs

  Scenario: Fill inputs using simplified format
    Given I am on the input page
    When I fill Password with SecurePass123
    And I fill Email with test@example.com
    And I fill text with Sample Text
    Then all input fields should be filled correctly

  # Context-Driven Scenarios (Using Context)
  Scenario: Identify and fill input using context by type
    Given I am on the input page
    And I identify the "text" type input
    When I fill the input from context with "Context Text Value"
    Then the context should contain input with key "text"

  Scenario: Identify and fill input using context by label
    Given I am on the input page
    And I identify the input with label "Username"
    When I fill the input from context with "john.doe"
    Then the context should contain input with key "Username"

  Scenario: Store multiple inputs in context and fill them
    Given I am on the input page
    And I identify the "text" type input
    And I identify the "password" type input
    When I fill the input with context key "text" with "First Input Value"
    And I fill the input with context key "password" with "SecretPassword123"
    Then the context should contain input with key "text"
    And the context should contain input with key "password"

  Scenario: Identify input by position and fill from context
    Given I am on the input page
    And I identify the input at position "1"
    When I fill the input from context with "Position 1 Value"
    Then I should see a summary of all inputs

  Scenario: Identify input by data-attr-id and fill from context
    Given I am on the input page
    And I identify the input with data-atr-id "username-input"
    When I fill the input from context with "testuser"
    Then the context should contain input with key "username-input"
    
  # Auto-Click Associated Button Scenarios
  # Note: Associated buttons are automatically clicked after filling inputs
  Scenario: Fill search input with auto-click button
    Given I am on the input page
    When I fill first search input with test search query
    Then I should see a summary of all inputs

  Scenario: Fill input with associated button using context
    Given I am on the input page
    And I identify the "search" type input
    When I fill the input from context with "search query"
    Then the context should contain input with key "search"

  Scenario: Fill multiple search inputs with buttons
    Given I am on the input page
    When I fill first search input with first query
    And I fill first search input with second query
    Then I should see a summary of all inputs

  Scenario: Fill search input and verify button is clicked
    Given I am on the input page
    And I identify the "search" type input
    When I fill the input from context with "test search query"
    Then the context should contain input with key "search"
    And the input should have an associated button

  Scenario: Fill all inputs automatically with random values
    Given I am on the input page
    When I fill all inputs with random values
    Then I should see a summary of all inputs

  Scenario: Fill all inputs automatically with generic values
    Given I am on the input page
    When I fill all inputs with generic values
    Then I should see a summary of all inputs

