Feature: TreeSelect Automation
  As a user
  I want to interact with Ant Design TreeSelect components
  So that I can select tree nodes and navigate hierarchical data

  Scenario: Select a single node from basic TreeSelect
    Given I am on the TreeSelect page
    When I select "Node1" from "Basic TreeSelect" TreeSelect
    Then "Basic TreeSelect" TreeSelect should contain "Node1"

  Scenario: Select multiple nodes from multiple selection TreeSelect
    Given I am on the TreeSelect page
    When I select multiple options "Node1", "Node2" from "Multiple Selection" TreeSelect
    Then "Multiple Selection" TreeSelect should show 2 selected items

  Scenario: Expand and collapse tree nodes
    Given I am on the TreeSelect page
    When I expand "Parent Node" node in "Basic TreeSelect" TreeSelect
    And I collapse "Parent Node" node in "Basic TreeSelect" TreeSelect
    Then I print summary of "Basic TreeSelect" TreeSelect

  Scenario: Check nodes in checkable TreeSelect
    Given I am on the TreeSelect page
    When I check "Node1" node in "Checkable TreeSelect" TreeSelect
    And I check "Node2" node in "Checkable TreeSelect" TreeSelect
    Then "Checkable TreeSelect" TreeSelect should show 2 selected items

  Scenario: Search within TreeSelect
    Given I am on the TreeSelect page
    When I search for "pine" in "Search TreeSelect" TreeSelect
    Then I print summary of "Search TreeSelect" TreeSelect

  Scenario: Select node by path
    Given I am on the TreeSelect page
    When I select "Parent > Child > Grandchild" from "Basic TreeSelect" TreeSelect
    Then "Basic TreeSelect" TreeSelect should contain "Grandchild"

  Scenario: Select all leaf nodes under parent
    Given I am on the TreeSelect page
    When I select all leaf nodes under "Region" in "Location TreeSelect" TreeSelect
    Then "Location TreeSelect" TreeSelect should show at least 1 selected items

  Scenario: Clear selection
    Given I am on the TreeSelect page
    When I select "Node1" from "Basic TreeSelect" TreeSelect
    And I clear selection in "Basic TreeSelect" TreeSelect
    Then "Basic TreeSelect" TreeSelect should show 0 selected items

  # Context-Driven Scenarios
  Scenario: Identify and use TreeSelect from context
    Given I am on the TreeSelect page
    And I identify the TreeSelect with label "Basic TreeSelect"
    When I select "Node1" from "Basic TreeSelect" TreeSelect
    Then "Basic TreeSelect" TreeSelect should contain "Node1"

  Scenario: Identify TreeSelect by data-attr-id and use context
    Given I am on the TreeSelect page
    And I identify the TreeSelect with data-attr-id "basic-treeselect"
    When I select "Node1" from "basic-treeselect" TreeSelect
    Then "basic-treeselect" TreeSelect should contain "Node1"
