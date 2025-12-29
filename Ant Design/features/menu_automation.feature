Feature: Ant Design Menu Automation
  As a user
  I want to click on menu items
  So that I can navigate through the website

  Background:
    Given I am on the menu page

  Scenario: Click on Navigation One
    When I click Navigation One
    Then Navigation One should be visible

  Scenario: Open Navigation One and click Option 1
    When I open Navigation One
    And I click Option 1
    Then Option 1 should be visible

  Scenario: Open Navigation Two and click Option 5
    When I open Navigation Two
    And I click Option 5
    Then Option 5 should be visible

  Scenario: Click Option 7
    When I click Option 7
    Then Option 7 should be visible

  Scenario: Click Option 8
    When I click Option 8
    Then Option 8 should be visible

  Scenario: Open Navigation Two and click Option 1 inside it
    When I open Navigation Two
    And I remember Option 1 inside Navigation Two
    And I click the remembered Option 1
    Then Option 1 should be visible

  Scenario: Click the first menu item
    When I remember the first menu item
    And I click the remembered first menu item
    Then the menu should be visible

  Scenario: Click Option 1 from Navigation One
    When I open Navigation One
    And I remember Option 1 from Navigation One
    And I click the remembered Option 1
    Then Option 1 should be visible

