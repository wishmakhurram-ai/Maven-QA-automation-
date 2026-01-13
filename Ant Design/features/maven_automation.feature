Feature: MavenAI Admin Portal Login Automation
  As an admin user
  I want to access the Admin Portal
  So that I can manage the MavenAI system

  Background:
    Given I am on the Admin Portal Login Page

  # ==================== ACCEPTANCE CRITERIA ====================

  @LOGIN-004 @smoke @required @admin
  Scenario: Admin can successfully log in
    Given I am on the Admin Portal Login Page
    And an admin user ammarah.yousaf@rolustech.net exists with password Lorem@1234
    When I enter email wishma.khurram@rolustech.com
    And I enter password Lorem@123
    And I click the "Log In" button
    And I should be redirected to the Admin Dashboard Home
    And I should see the Admin Dashboard


 @ADMIN-005 @required @admin
  Scenario: Admin can create a new firm with owner
    Given I am on the Firms list page
    When I click "Add Firm" button
    Then I should be redirected to the "Create New Firm" page
    When I enter "my fir m " in the "Firm Name" field
    And I enter "contact@firm.com" in the "Email" field
    And I enter "(555) 123-7" in the "Phone" field
    And I enter "Main " in the "Street Address" field
    And I enter "Salmiya " in the "City" field
    And I enter "SA" in the "State" field
    And I enter "12345" in the "Zip Code" field
    And I enter "Canada" in the "Country" field
    And I create a new owner with email "owner@firm.com" and first name " Doe" and last name "bro"
    And I click the "Create" button on owner page
    And then i click "Create Firm" button
    Then the firm should be created successfully
    And I should see a success message "Firm created successfully"
    And I should be redirected to the Firms list page
 