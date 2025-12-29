Feature: MavenAI Admin Portal Login Automation
  As an admin user
  I want to access the Admin Portal
  So that I can manage the MavenAI system

  Background:
    Given I am on the Admin Portal Login Page

  # ==================== ACCEPTANCE CRITERIA ====================

  @LOGIN-001 @smoke @required @admin
  Scenario: Admin users can navigate to dedicated Admin Portal Login Page
    Given I am on the Admin Portal Login Page
    Then I should see the Admin Portal Login Page
    And I should see an email input field
    And I should see a password input field
    And I should see a "Log In" or "Sign In" button
    And I should see a "Forgot password" link

  @LOGIN-002 @smoke @required @admin
  Scenario: Login page displays Email and Password fields
    Given I am on the Admin Portal Login Page
    Then I should see an email input field with label "Email" or "Email Address"
    And I should see a password input field with label "Password"
    And the password field is visible
    And I should see a "Log In" or "Sign In" button
    And the button should be enabled

  @LOGIN-003 @smoke @required @admin
  Scenario: "Forgot password" link redirects to password reset flow
    Given I am on the Admin Portal Login Page
    When I click on the "Forgot password" link
    Then I should be redirected to the password reset flow
    And I should see the Password Reset Request screen

 @LOGIN-004 @required @admin
  Scenario: Empty email field shows validation error
    Given I am on the Admin Portal Login Page
    When I leave the email field empty
    And I enter password Lorem@1234
    And I click the "Log In" button
    Then I should see an error message "Email is required"
    And the form should not be submitted

@LOGIN-005 @required @admin
  Scenario: Invalid email format shows validation error
    Given I am on the Admin Portal Login Page
    When I enter email invalid-email-format
    And I enter password Lorem@1234
    And I click the "Log In" button
    Then I should see an error message "Please enter a valid email address"
    And the form should not be submitted


  @LOGIN-004 @smoke @required @admin
  Scenario: Admin can successfully log in
    Given I am on the Admin Portal Login Page
    And an admin user ammarah.yousaf@rolustech.net exists with password Lorem@1234
    When I enter email wishma.khurram@rolustech.com
    And I enter password Lorem@123
    And I click the "Log In" button
    And I should be redirected to the Admin Dashboard Home
    And I should see the Admin Dashboard


  @ADMIN-001 @smoke @required @admin
  Scenario: Admin lands on Admin Panel Dashboard - Firms View by default
    Given I am on the Admin Panel dashboard
    Then I should be on the Firms list page by default
    And the "Firms" section should be selected in the navigation menu

  @ADMIN-002 @smoke @required @admin
  Scenario: Admin can access Firms section and view firms list
    Given I am on the Admin Panel dashboard
    When I click on the "Firms" section in the navigation
    Then I should be redirected to the Firms list page
    And if firms exist, I should see a list of all existing firms
    And if no firms exist, I should see an empty state message

  @ADMIN-003 @smoke @required @admin
  Scenario: Admin can access Users section and view users list (read-only)
    Given I am on the Admin Panel dashboard
    When I click on the "Users" section in the navigation
    Then I should be redirected to the Users list page
    And if users exist, I should see a list of all existing users
    And if no users exist, I should see an empty state message
    And I should NOT see any option to create, edit, or delete users
    And the page should be read-only

  @ADMIN-004 @required @admin
  Scenario: Firms list displays all required columns
    Given I am on the Firms list page
    Then I should see a table with the following columns:
      | Column Name |
      | Firm Name |
      | Status |
      | Email |
      | Phone |
      | Website |
      | Date Created |
      | Action |
    And each firm row should display these details

@ADMIN-005 @required @admin
Scenario: Admin can create a new firm with owner
  Given I am on the Firms list page
  When i click Add Firm button
  When I fill in all mandatory fields:
    | Field | Value |
    | Firm Name | New Legal Firm LLC |
    | Email | contact@newlegalfirm.com |
    | Phone | (555) 123-4567 |
    | Street Address | 123 Main Street |
    | City | New York |
    | State | NY |
    | Postal Code | 10001 |
    | Country | Canada |
  And I create a new owner with email "owner@newlegalfirm.com" and name "John Doe"
  And I click the "Create Firm" button
  Then the firm should be created successfully
  And I should see a success message "Firm created successfully"
  And I should be redirected to the Firms list page
  And the new firm "New Legal Firm LLC" should appear in the Firms list
  And the firm status should be "Pending"
  And the newly created owner "John Doe (owner@newlegalfirm.com)" should be associated with the firm
