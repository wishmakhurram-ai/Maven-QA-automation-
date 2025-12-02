Feature: Button Automation
  As a user
  I want to click buttons on a webpage
  So that I can interact with the page easily

  Scenario: Click a primary button
    Given I am on the button page
    When I click the primary button
    Then the button should be clicked successfully
    And I should see the button type is "primary"

  Scenario: Click a default button
    Given I am on the button page
    When I click the default button
    Then the button should be clicked successfully
    And I should see the button type is "default"

  Scenario: Click a dashed button
    Given I am on the button page
    When I click the dashed button
    Then the button should be clicked successfully
    And I should see the button type is "dashed"

  Scenario: Click a text button
    Given I am on the button page
    When I click the text button
    Then the button should be clicked successfully
    And I should see the button type is "text"

  Scenario: Click a link button
    Given I am on the button page
    When I click the link button
    Then the button should be clicked successfully
    And I should see the button type is "link"

  Scenario: Click a danger button
    Given I am on the button page
    When I click the danger button
    Then the button should be clicked successfully
    And I should see the button type is "danger"

  # Context-Driven Scenarios
  Scenario: Identify and click button using context
    Given I am on the button page
    And I identify the primary button
    When I click the button from context
    Then the button should be clicked successfully
    And the context should contain element with key "primary_button"

  Scenario: Identify button by data-attr-id and use context
    Given I am on the button page
    And I identify the button with data-atr-id "save-btn"
    When I click the button from context
    Then the button should be clicked successfully
    And the context should contain element with key "save-btn"

  Scenario: Store multiple buttons in context
    Given I am on the button page
    And I identify the primary button
    And I identify the default button
    When I click the button with context key "primary_button"
    Then the button should be clicked successfully
    And the context should contain element with key "default_button"

