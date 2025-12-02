Feature: Ant Design Pagination Automation
  As a QA tester
  I want to automate interactions with Ant Design Pagination components
  So that I can test pagination functionality without hardcoded selectors

  Background:
    Given I am on the pagination page

  Scenario: Navigate to specific page
    Given I identify the pagination at position 2
    When I go to page 2
    Then I should be on page 2
    And I should see a summary of the pagination

  Scenario: Navigate using next and previous buttons
    Given I identify the pagination at position 2
    When I go to page 1
    And I go to the next page
    Then I should be on page 2
    When I go to the previous page
    Then I should be on page 1
    And I should see a summary of the pagination

  Scenario: Change page size
    Given I identify a pagination with size_changer
    When I change page size to 20
    Then the page size should be 20
    And I should see a summary of the pagination

  Scenario: Jump to page using jump-to input
    Given I identify a pagination with jump_to
    When I jump to page 3
    Then I should be on page 3
    And I should see a summary of the pagination

  Scenario: Complete pagination workflow
    Given I identify a pagination with all features
    When I go to page 1
    Then I should be on page 1
    When I change page size to 20
    Then the page size should be 20
    When I go to the next page
    Then I should be on page 2
    And I should see a summary of the pagination

