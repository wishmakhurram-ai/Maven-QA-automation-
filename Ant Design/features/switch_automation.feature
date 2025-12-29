Feature: Ant Design Switch Component Automation
  As a test automation engineer
  I want to automatically detect, read state, and toggle Ant Design Switch components
  So that I can test switch functionality without hardcoded locators

  Background:
    Given I am on a page with Ant Design Switch components

  Scenario: Detect and summarize all switches on the page
    When I navigate to a page with switches
    Then I should see a summary of all switches

  Scenario: Toggle switch by semantic label
    Given I am on a page with switches
    When I turn on the switch "Notifications"
    Then the switch "Notifications" should be ON
    When I turn off the switch "Notifications"
    Then the switch "Notifications" should be OFF

  Scenario: Toggle switch by data-attr-id
    Given I am on a page with switches
    When I identify the switch with data-atr-id "notifications-switch"
    And I toggle the switch "notifications-switch"
    Then the switch "notifications-switch" should be ON

  Scenario: Toggle switch by position
    Given I am on a page with switches
    When I toggle the switch at position 1
    Then I should see 1 switch(es) on the page

  Scenario: Toggle first switch
    Given I am on a page with switches
    When I toggle the first switch
    Then I should see a summary of all switches

  Scenario: Verify switch state assertions
    Given I am on a page with switches
    When I turn on the switch "Dark Mode"
    Then the switch "Dark Mode" should be ON
    And the switch "Dark Mode" should be enabled
    When I turn off the switch "Dark Mode"
    Then the switch "Dark Mode" should be OFF

  Scenario: Verify disabled switch cannot be toggled
    Given I am on a page with switches
    When I identify the switch with label "Disabled Switch"
    Then the switch "Disabled Switch" should be disabled

  Scenario: Verify switch size
    Given I am on a page with switches
    When I identify the switch with label "Small Switch"
    Then the switch "Small Switch" should have size "small"

  Scenario: Verify switch loading state
    Given I am on a page with switches
    When I identify the switch with label "Loading Switch"
    Then the switch "Loading Switch" should be in loading state

  Scenario: Multiple switches on page
    Given I am on a page with switches
    When I turn on the switch "Notifications"
    And I turn on the switch "Email Alerts"
    And I turn off the switch "SMS Alerts"
    Then the switch "Notifications" should be ON
    And the switch "Email Alerts" should be ON
    And the switch "SMS Alerts" should be OFF
    Then I should see a summary of all switches




