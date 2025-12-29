Feature: MavenAI Admin Dashboard Automation
  As an admin user
  I want to manage firms and users in the Admin Dashboard
  So that I can effectively administer the MavenAI system

  Background:
    Given I am on the Admin Portal Login Page
    And an admin user ammarah.yousaf@rolustech.net exists with password Lorem@123
    When I enter email ammarah.yousaf@rolustech.net
    And I enter password "Lorem123"
    And I click the "Log In" button
    And I should be redirected to the Admin Dashboard Home
    And I should see the Admin Dashboard

  # ==================== ACCEPTANCE CRITERIA ====================

  @ADMIN-005 @required @admin
  Scenario: Firm Name is clickable and opens detailed firm profile
    Given I am on the Firms list page
    And a firm "Smith & Associates Law" exists with status "Active"
    When I click on the firm name "Smith & Associates Law" or the firm row
    Then I should be redirected to the firm details page
    And I should see the firm name "Smith & Associates Law" prominently displayed

  @ADMIN-006 @required @admin
  Scenario: Status is displayed as colored badges (Active / Pending / Suspended)
    Given I am on the Firms list page
    And firms exist with different statuses
    Then I should see status displayed as colored badges:
      | Status |
      | Active |
      | Pending |
      | Suspended |

  @ADMIN-007 @required @admin
  Scenario: Actions column displays Edit, Suspend / Active, Delete, Resend Invite if firm is in pending state
    Given I am on the Firms list page
    And a firm exists
    Then I should see action buttons/icons in the Actions column:
      | Action | Display |
      | Edit | Edit icon (pencil) |
      | Suspend/Mark Active | Status change icon |
      | Delete | Delete icon (trash can) |
      | Resend Invite | Envelope icon |

  @ADMIN-008 @required @admin
  Scenario: Admin can search firms by Firm Name
    Given I am on the Firms list page
    And multiple firms exist
    When I type "Smith" in the search field "Search Firm"
    Then I should see filtered results showing only firms with "Smith" in the name
    When I clear the search text
    Then I should see all firms again
    When no firms match the search criteria
    Then I should see an empty state message "No firms found"

  @ADMIN-009 @admin
  Scenario: Firms list pagination works correctly
    Given I am on the Firms list page
    And more than 10 firms exist
    Then I should see pagination controls at the bottom of the table
    And I should see page navigation arrows (left and right)
    And I should see page numbers displayed (e.g., "1", "2", "3")
    And the current page number should be highlighted
    And I should see "10 / page" dropdown
    When I click on the right arrow to go to the next page
    Then I should see the next page of firms
    And the page number should update to "2"
    When I click on the left arrow to go to the previous page
    Then I should see the previous page of firms
    And the page number should update to "1"
    When I click on the "10 / page" dropdown
    Then I should see options: "10", "20", "50", "100"
    When I select "20" from the dropdown
    Then the table should display 20 firms per page
    And the pagination should update accordingly
    And the dropdown should show "20 / page"

  @ADMIN-010 @smoke @required @admin
  Scenario: Admin User sees "Add Firm" button
    Given I am on the Firms list page
    Then I should see an "Add Firm" button
    When I click the "Add Firm" button
    Then I should be redirected to the "Create New Firm" page

  @ADMIN-011 @required @admin
  Scenario: Users list displays all required columns
    Given I am on the Users list page
    Then I should see a table with the following columns:
      | Column Name |
      | User Name |
      | Email |
      | Firm |
      | Status |
      | Role |
    And each user row should display these details

  @ADMIN-012 @required @admin
  Scenario: Admin can search users by name, email, or firm
    Given I am on the Users list page
    And multiple users exist
    When I type search text in the search field "Search users..."
    Then I should see filtered results matching the search text
    And I can see users whose name, email, or firm name matches the search
    When I clear the search text
    Then I should see all users again
    When no users match the search criteria
    Then I should see an empty state message "No users found"

  @ADMIN-013 @required @admin
  Scenario: Admin can filter users by firm using Choose Firm dropdown
    Given I am on the Users list page
    And multiple users exist from different firms
    When I click on the "Choose Firm" dropdown
    Then I should see a list of all firms
    When I select "Smith & Associates Law" from the firm dropdown
    Then I should see only users from "Smith & Associates Law"
    And the firm filter should show "Smith & Associates Law" as selected
    When I clear the firm filter or select "All Firms"
    Then I should see all users from all firms

  @ADMIN-014 @required @admin
  Scenario: Users list displays all required columns (duplicate)
    Given I am on the Users list page
    Then I should see a table with the following columns:
      | Column Name |
      | User Name |
      | Email |
      | Firm |
      | Status |
      | Role |
    And each user row should display these details

  @ADMIN-015 @required @admin
  Scenario: Admin can search users by name, email, or firm (duplicate)
    Given I am on the Users list page
    And multiple users exist
    When I type search text in the search field "Search users..."
    Then I should see filtered results matching the search text
    And I can see users whose name, email, or firm name matches the search
    When I clear the search text
    Then I should see all users again
    When no users match the search criteria
    Then I should see an empty state message "No users found"

  @ADMIN-016 @required @admin
  Scenario: Admin can filter users by firm using Choose Firm dropdown (duplicate)
    Given I am on the Users list page
    And multiple users exist from different firms
    When I click on the "Choose Firm" dropdown
    Then I should see a list of all firms
    When I select "Smith & Associates Law" from the firm dropdown
    Then I should see only users from "Smith & Associates Law"
    And the firm filter should show "Smith & Associates Law" as selected
    When I clear the firm filter or select "All Firms"
    Then I should see all users from all firms

  @ADMIN-017 @smoke @required @admin
  Scenario: Admin can open and view firm details page
    Given I am on the Firms list page
    And a firm "Smith & Associates Law" exists with status "Active"
    When I click on the firm name "Smith & Associates Law" or the firm row
    Then I should be redirected to the firm details page
    And I should see a "Back to Firms" link with left arrow icon (← Back to Firms)
    And I should see the firm name "Smith & Associates Law" prominently displayed
    And I should see a building icon next to the firm name
    And I should see the firm status "Active" displayed as a green button with dropdown arrow
    And I should see an "Edit Firm" button in red color on the right side

  @ADMIN-018 @required @admin
  Scenario: Firm details page displays Firm Information section correctly
    Given I am on the firm details page for "Smith & Associates Law"
    Then I should see the "Firm Information" section as a white card
    And I should see the following firm details:
      | Field | Value |
      | Email | contact@smithlaw.com |
      | Phone | (555) 123-4567 |
      | Website | https://smithlaw.com |
      | Address | 123 Main Street, New York, NY 10001, United States |

  @ADMIN-019 @required @admin
  Scenario: Firm details page displays Associated Users section correctly
    Given I am on the firm details page for "Smith & Associates Law"
    Then I should see the "Associated Users" section as a white card
    And I should see a table with columns: "Name", "Email", "Role", "Status"
    And I should see users listed in the table with:
      | Name | Email | Role | Status |
      | John Smith | john@smithlaw.com | Owner | Active |
      | Sarah Johnson | sarah@smithlaw.com | Admin | Active |

  @ADMIN-020 @admin
  Scenario: Admin can navigate back to Firms list from firm details page
    Given I am on the firm details page for "Smith & Associates Law"
    When I click on the "Back to Firms" link
    Then I should be redirected back to the Firms list page
    And I should see the firms list

  # ==================== TEST CASES ====================

  @ADMIN-01-DTC @admin
  Scenario: Admin can search firms by name with various search patterns
    Given I am on the Firms list page
    And multiple firms exist: "Smith & Associates Law", "Johnson Legal Group", "Davis & Partners"
    When I type "Smith" in the search field "Search Firm"
    Then I should see filtered results showing only firms with "Smith" in the name
    And I should see "Smith & Associates Law" in the results
    And I should not see "Johnson Legal Group" in the results
    And I should not see "Davis & Partners" in the results
    When I type "Law" in the search field
    Then I should see all firms containing "Law" in the name
    When I clear the search text
    Then I should see all firms again
    When no firms match the search criteria "XYZ123"
    Then I should see an empty state message "No firms found"

  @ADMIN-002-DTC @admin
  Scenario: Firms list pagination works correctly (Test Case)
    Given I am on the Firms list page
    And more than 10 firms exist
    Then I should see pagination controls at the bottom of the table
    And I should see page navigation arrows (left and right)
    And I should see page numbers displayed (e.g., "1", "2", "3")
    And the current page number should be highlighted
    And I should see "10 / page" dropdown
    When I click on the right arrow to go to the next page
    Then I should see the next page of firms
    And the page number should update to "2"
    When I click on the left arrow to go to the previous page
    Then I should see the previous page of firms
    And the page number should update to "1"
    When I click on the "10 / page" dropdown
    Then I should see options: "10", "20", "50", "100"
    When I select "20" from the dropdown
    Then the table should display 20 firms per page
    And the pagination should update accordingly
    And the dropdown should show "20 / page"

  @ADMIN-003-DTC @admin
  Scenario: Pagination controls are disabled appropriately
    Given I am on the Firms list page
    And exactly 5 firms exist (less than one page)
    Then I should see "Total 5 firms" summary
    And the left arrow should be disabled
    And the right arrow should be disabled
    And only page "1" should be visible
    When more than 10 firms exist
    Then the right arrow should be enabled on the first page
    And the left arrow should be disabled on the first page
    When I navigate to the last page
    Then the right arrow should be disabled
    And the left arrow should be enabled

  @ADMIN-004-DTC @admin
  Scenario: Admin can click on specific page number to navigate
    Given I am on the Firms list page
    And more than 20 firms exist (requiring multiple pages)
    Then I should see page numbers displayed (e.g., "1", "2", "3")
    When I click on page number "2"
    Then I should see the second page of firms
    And page number "2" should be highlighted
    And the URL or page state should reflect the current page

  @ADMIN-005-DTC @admin
  Scenario: Admin can select multiple firms using checkboxes
    Given I am on the Firms list page
    And multiple firms exist
    When I click on the checkbox for "Smith & Associates Law"
    Then the firm "Smith & Associates Law" should be selected
    And I should see a selection bar showing "1 firm(s) selected"
    When I click on the checkbox for "Johnson Legal Group"
    Then the firm "Johnson Legal Group" should be selected
    And I should see the selection bar showing "2 firm(s) selected"
    And I should see bulk action buttons: "Change Status", "Delete Selected", "Clear Selection"

  @ADMIN-006-DTC @admin
  Scenario: Admin can clear firm selection
    Given I am on the Firms list page
    And I have selected "Smith & Associates Law" and "Johnson Legal Group"
    And the selection bar is visible showing "2 firm(s) selected"
    When I click on the "Clear Selection" button
    Then all firm selections should be cleared
    And the selection bar should disappear
    And no checkboxes should be checked

  @ADMIN-007-DTC @admin
  Scenario: Admin can select all firms using header checkbox
    Given I am on the Firms list page
    And multiple firms exist
    When I click on the header checkbox to select all firms
    Then all firms on the current page should be selected
    And I should see the selection bar showing the total count of selected firms
    When I click on the header checkbox again
    Then all firm selections should be cleared
    And the selection bar should disappear

  @ADMIN-008-DTC @admin
  Scenario: Status badges display correctly for all status types
    Given I am on the Firms list page
    And firms exist with different statuses:
      | Firm Name | Status |
      | Active Firm | Active |
      | Pending Firm | Pending |
      | Suspended Firm | Suspended |

  @ADMIN-009-DTC @admin
  Scenario: Admin can search users with various search patterns
    Given I am on the Users list page
    And multiple users exist:
      | Name | Email | Firm |
      | John Smith | john@smithlaw.com | Smith & Associates Law |
      | Jane Doe | jane@johnsonlaw.com | Johnson Legal Group |
    When I type "John" in the search field
    Then I should see users matching "John" in name or email
    And I should see "John Smith" in the results
    When I type "smithlaw.com" in the search field
    Then I should see users with matching email domain
    When I type "Smith & Associates" in the search field
    Then I should see users from that firm
    When I clear the search text
    Then I should see all users again

  @ADMIN-010-DTC @admin
  Scenario: Navigation between firms list and firm details works correctly
    Given I am on the Firms list page
    And multiple firms exist
    When I click on firm name "Smith & Associates Law"
    Then I should be redirected to firm details page
    And I should see "Back to Firms" link
    When I click on "Back to Firms" link
    Then I should be redirected back to Firms list page
    And I should see all firms displayed
    And the search and filter state should be preserved

  @ADMIN-011-DTC @admin
  Scenario: Admin can access logout from User Profile Icon
    Given I am on the Admin Panel dashboard
    When I click on the User Profile Icon in the header
    Then I should see a dropdown menu
    And the dropdown should contain logout option
    When I click on the logout option
    Then I should be logged out successfully
    And I should be redirected to the login page
    And I should not be able to access admin panel without logging in again

  @ADMIN-012-DTC @admin
  Scenario: Admin can click delete icon (dustbin) and see confirmation popup
    Given I am on the Firms list page
    And a firm "Smith & Associates Law" exists with status "Active"
    When I click on the delete icon (dustbin/trash can) for the firm "Smith & Associates Law"
    Then I should see a confirmation popup/dialog
    And the popup should display a message asking to confirm deletion
    And the popup should have "Cancel" and "Confirm" or "Delete" buttons
    When I click "Cancel" in the popup
    Then the popup should close
    And the firm "Smith & Associates Law" should still exist
    When I click on the delete icon (dustbin/trash can) for the firm "Smith & Associates Law" again
    And I click "Confirm" or "Delete" in the popup
    Then the firm "Smith & Associates Law" should be deleted
    And I should see a success message "Firm deleted successfully"
    And the firm should no longer appear in the Firms list

  @ADMIN-013-DTC @admin
  Scenario: Admin can click suspend icon and see confirmation popup
    Given I am on the Firms list page
    And a firm "Smith & Associates Law" exists with status "Active"
    When I click on the suspend icon (circle with slash) for the firm "Smith & Associates Law"
    Then I should see a confirmation popup/dialog
    And the popup should display a message asking to confirm suspension
    And the popup should have "Cancel" and "Confirm" or "Suspend" buttons
    When I click "Cancel" in the popup
    Then the popup should close
    And the firm status should remain "Active"
    When I click on the suspend icon (circle with slash) for the firm "Smith & Associates Law" again
    And I click "Confirm" or "Suspend" in the popup
    Then the firm status should change to "Suspended"
    And I should see a success message "Firm status updated successfully"
    And the firm status should be displayed as "Suspended" with circle with slash icon

  @ADMIN-014-DTC @admin
  Scenario: Admin can click edit icon and navigate to edit firm page
    Given I am on the Firms list page
    And a firm "Smith & Associates Law" exists with status "Active"
    When I click on the edit icon (pencil) for the firm "Smith & Associates Law"
    Then I should be redirected to the "Edit Firm" page
    And I should see the heading "Edit Firm" or "Edit Firm Details"
    And I should see all firm details pre-filled with existing data:
      | Field | Value |
      | Firm Name | Smith & Associates Law |
      | Email | contact@smithlaw.com |
      | Phone | (555) 123-4567 |
    And I should see a "Back to Firms" link
    And I should see "Update Firm" button

  @ADMIN-015-DTC @admin
  Scenario: Admin can change firm status from firm details page by clicking status dropdown
    Given I am on the firm details page for "Smith & Associates Law"
    And the firm "Smith & Associates Law" has status "Active"
    When I click on the status dropdown button showing "Active"
    Then I should see a dropdown menu with status options
    And I should see available status options: "Active", "Suspend"
    When I select "Suspend" from the status dropdown
    Then I should see a confirmation popup/dialog
    And the popup should display a message asking to confirm suspension
    When I click "Confirm" in the popup
    Then the firm status should change to "Suspended"
    And I should see the status displayed as "Suspended" with circle with slash icon
    And I should see a success message "Firm status updated successfully"
    When I click on the status dropdown button again
    And I select "Active" from the status dropdown
    Then the firm status should change back to "Active"
    And I should see the status displayed as "Active" with green indicator










Test Cases

  @LOGIN-001-DTC @admin
  Scenario: Admin Portal Login Page displays all required elements
    Given I am on the Admin Portal Login Page
    Then I should see the page title or heading Admin Portal or MavenAI Admin Portal
    And I should see the MavenAI logo or branding
    And I should see an email input field
    And I should see a password input field
    And I should see a Log In or Sign In button
    And I should see a Forgot Password link
    And the Forgot Password link should be positioned below the password field or near the login form

  @LOGIN-002-DTC @admin
  Scenario: Email and Password fields have proper labels and placeholders
    Given I am on the Admin Portal Login Page
    Then I should see an email input field
    And the email field should have a label Email or Email Address
    And the email field should have a placeholder Enter your email or similar
    And I should see a password input field
    And the password field should have a label Password
    And the password field should have a placeholder Enter your password or similar
    And the password field should be of type password masked input

  @LOGIN-003-DTC @smoke @required @admin
  Scenario: Forgot Password link navigation works correctly
    Given I am on the Admin Portal Login Page
    Then I should see a Forgot Password link
    And the link should be visible and clickable
    When I click on the Forgot Password link
    Then I should be redirected to the Password Reset Request screen
    And I should see the password reset form
    And I should see a Back to Login link

  @LOGIN-004-DTC @smoke @required @admin
  Scenario: Successful login with valid admin credentials
    Given I am on the Admin Portal Login Page
    And an admin user John Smith with email ammarah.yousaf@rolustech.net and password Lorem@123 exists
    When I enter email ammarah.yousaf@rolustech.net
    And I enter password Lorem@123
    And I click the Log In button
    Then the system should verify the credentials against the MavenAI user database
    And authentication should succeed
    And I should be redirected to the Admin Dashboard Home
    And I should see the Admin Dashboard
    And I should see a welcome message Welcome back John Smith

  @LOGIN-005-DTC @required @admin
  Scenario: System correctly identifies admin vs non-admin users
    Given I am on the Admin Portal Login Page
    And a regular user user@example.com exists with role Member not admin
    When I enter email user@example.com
    And I enter password UserPass123!
    And I click the Log In button
    Then the system should check the user role
    And the system should determine the user is not an admin
    And I should see an error message Access denied Admin privileges required
    And I should not be redirected to the Admin Dashboard
    And I should remain on the Admin Portal Login Page

  @LOGIN-006-DTC @required @admin
  Scenario: System handles non-existent email addresses
    Given I am on the Admin Portal Login Page
    When I enter email nonexistent@example.com
    And I enter password SomePassword123!
    And I click the Log In button
    Then I should see an error message Incorrect email or password Please try again
    And the error message should not reveal whether the email exists or not
    And I should remain on the Admin Portal Login Page

  @LOGIN-007-DTC @smoke @required @admin
  Scenario: Complete successful login flow with welcome message
    Given I am on the Admin Portal Login Page
    And an admin user John Smith with email ammarah.yousaf@rolustech.net exists
    When I enter email ammarah.yousaf@rolustech.net
    And I enter password Lorem@123
    And I click the Log In button
    Then I should see a brief success message Login successful Redirecting to Admin Dashboard
    And I should be redirected to the Admin Dashboard Home
    And I should see the Admin Dashboard with navigation menu
    And I should see a welcome message Welcome back John Smith
    And the welcome message should be displayed prominently at the top of the dashboard
    And I should see the Firms section selected by default in the navigation

  @LOGIN-008-DTC @admin
  Scenario: User session is created upon successful login
    Given I am on the Admin Portal Login Page
    And an admin user ammarah.yousaf@rolustech.net exists
    When I successfully log in
    Then a user session should be created
    And the session should be active
    And I should be able to navigate between pages without re-authentication
    And I should see my user profile icon in the header

  @LOGIN-009-DTC @smoke @required @admin
  Scenario: Invalid password shows appropriate error message
    Given I am on the Admin Portal Login Page
    And an admin user ammarah.yousaf@rolustech.net exists with password Lorem@123
    When I enter email ammarah.yousaf@rolustech.net
    And I enter password WrongPassword123!
    And I click the Log In button
    Then I should see an error message Incorrect email or password Please try again
    And the error message should be displayed in red or error styling
    And the error message should be visible below the login form or near the password field
    And I should remain on the Admin Portal Login Page
  @LOGIN-010-DTC @required @admin
  Scenario: Field validation for empty email
    Given I am on the Admin Portal Login Page
    When I leave the email field empty
    And I enter password SomePassword123!
    And I click the Log In button
    Then I should see an error message Email is required
    And the error message should appear near the email field
    And the email field should be highlighted or bordered in red
    And the form should not be submitted
    And I should remain on the Admin Portal Login Page

  @LOGIN-011-DTC @required @admin
  Scenario: Email format validation
    Given I am on the Admin Portal Login Page
    When I enter email invalid-email-format
    And I enter password SomePassword123!
    And I click the Log In button
    Then I should see an error message Please enter a valid email address
    And the error message should appear near the email field
    And the form should not be submitted
    When I enter email missing@domain
    And I click the Log In button
    Then I should see an error message Please enter a valid email address
    When I enter email @domain.com
    And I click the Log In button
    Then I should see an error message Please enter a valid email address

  @LOGIN-012-DTC @required @admin
  Scenario: Error messages clear when user starts typing
    Given I am on the Admin Portal Login Page
    When I leave the email field empty
    And I click the Log In button
    Then I should see an error message Email is required
    When I start typing in the email field
    Then the error message should disappear or clear
    And the email field should no longer be highlighted in red

  @LOGIN-013-DTC @required @admin
  Scenario: Auto-logout after 30 minutes of inactivity
    Given I am logged in as an admin user
    And I am on the Admin Dashboard
    And I can see my active session
    When I remain inactive no mouse movement keyboard input or page interaction for 30 minutes
    Then I should be automatically logged out
    And I should be redirected to the Admin Portal Login Page
    And I should see a message Your session has expired due to inactivity Please log in again
    And the message should be displayed prominently as a notification or banner
    And I should not be able to access the Admin Dashboard
    When I try to navigate to the Admin Dashboard URL directly
    Then I should be redirected back to the Admin Portal Login Page
    And I should need to log in again to access the dashboard

  @LOGIN-014-DTC @admin
  Scenario: Activity resets inactivity timer
    Given I am logged in as an admin user
    And I am on the Admin Dashboard
    When I interact with the page click type scroll within 30 minutes
    Then the inactivity timer should reset
    And I should not be logged out
    And my session should remain active
    When I remain inactive for another 30 minutes from the last activity
    Then I should be automatically logged out

  @LOGIN-015-DTC @required @admin
  Scenario: Failed login attempts are tracked and counted
    Given I am on the Admin Portal Login Page
    And an admin user ammarah.yousaf@rolustech.net exists with password Lorem@123
    When I attempt to log in with incorrect password WrongPass1
    Then the failed attempts counter should be 1
    And I should see an error message Incorrect email or password Please try again
    When I attempt to log in with incorrect password WrongPass2
    Then the failed attempts counter should be 2
    When I attempt to log in with incorrect password WrongPass3
    Then the failed attempts counter should be 3
    When I attempt to log in with incorrect password WrongPass4
    Then the failed attempts counter should be 4
    When I attempt to log in with incorrect password WrongPass5
    Then the failed attempts counter should be 5
    And I should see an error message Account temporarily locked due to multiple failed login attempts

  @LOGIN-016-DTC @required @admin
  Scenario: Account lockout after 5 failed attempts
    Given I am on the Admin Portal Login Page
    And an admin user ammarah.yousaf@rolustech.net exists
    When I attempt to log in with incorrect password 5 times
    Then I should see an error message Account temporarily locked due to multiple failed login attempts
    And the account should be locked for 15 minutes
    And the login button should be disabled or the form should not accept submissions
    When I try to log in with correct credentials during the lockout period
    Then I should see an error message Account temporarily locked Please try again after 15 minutes
    And I should not be able to log in

  @LOGIN-017-DTC @required @admin
  Scenario: Account unlock after lockout period expires
    Given I am on the Admin Portal Login Page
    And an admin user ammarah.yousaf@rolustech.net exists with password Lorem@123
    And the account has been locked due to 5 failed login attempts
    When I wait for 15 minutes
    Then the account lockout should expire
    And the failed attempts counter should be reset
    When I attempt to log in with correct credentials ammarah.yousaf@rolustech.net and Lorem@123
    Then I should be able to log in successfully
    And I should be redirected to the Admin Dashboard

  @LOGIN-018-DTC @required @admin
  Scenario: Failed attempts counter resets after successful login
    Given I am on the Admin Portal Login Page
    And an admin user ammarah.yousaf@rolustech.net exists with password Lorem@123
    When I attempt to log in with incorrect password 3 times
    Then the failed attempts counter should be at 3
    When I successfully log in with correct credentials ammarah.yousaf@rolustech.net and Lorem@123
    Then the failed attempts counter should be reset to 0
    And I should be redirected to the Admin Dashboard
    When I log out and attempt to log in with incorrect password again
    Then the failed attempts counter should start at 1 not continue from previous count

  @LOGIN-019-DTC @smoke @required @admin
  Scenario: Complete successful login flow from start to finish
    Given I am on the Admin Portal Login Page
    And an admin user John Smith with email ammarah.yousaf@rolustech.net and password Lorem@123 exists
    When I enter email ammarah.yousaf@rolustech.net
    And I enter password Lorem@123
    And I click the Log In button
    Then I should see a brief loading indicator
    And I should see Login successful Redirecting to Admin Dashboard
    And I should be redirected to the Admin Dashboard Home
    And I should see the Admin Dashboard with all navigation options
    And I should see a welcome message Welcome back John Smith
    And I should see the Firms section selected by default
    And I should see my user profile icon in the header
    And I should be able to access all admin features




