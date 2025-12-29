Feature: Ant Design Upload Component Automation
  As a QA engineer
  I want to automate file uploads in Ant Design applications
  So that I can test upload functionality without manual selectors

  Background:
    Given I am on the custom application

  @UPLOAD-001 @smoke
  Scenario: Upload a single file to an upload component
    Given I identify the upload component with label "Profile Photo Upload"
    When I upload "test_document.pdf" using "Profile Photo Upload"
    Then the upload list for "Profile Photo Upload" should show 1 file
    And the upload list for "Profile Photo Upload" should contain "test_document.pdf"

  @UPLOAD-002 @smoke
  Scenario: Upload multiple files to an upload component
    Given I have files ["file1.pdf", "file2.pdf", "file3.pdf"]
    When I upload multiple files into "Attachments"
    Then the upload list for "Attachments" should show 3 files

  @UPLOAD-003
  Scenario: Upload files using list syntax
    When I upload files ["document.pdf", "image.png"] to "Documents"
    Then the upload list for "Documents" should show 2 files
    And the upload list for "Documents" should contain "document.pdf"
    And the upload list for "Documents" should contain "image.png"

  @UPLOAD-004
  Scenario: Drag and drop file upload
    When I drag and drop file "report.pdf" into "Supporting Documents"
    Then the upload list for "Supporting Documents" should show 1 file
    And the upload list for "Supporting Documents" should contain "report.pdf"

  @UPLOAD-005
  Scenario: Click picture-card upload
    When I click the picture-card upload "Profile Photo"
    # File selection dialog opens - user can select file manually or via automation
    Then I should see the upload component summary for "Profile Photo"

  @UPLOAD-006
  Scenario: Delete uploaded file
    Given I upload "temp_file.pdf" using "Attachments"
    And the upload list for "Attachments" should show 1 file
    When I delete file "temp_file.pdf" from "Attachments"
    Then the upload list for "Attachments" should show 0 files

  @UPLOAD-007
  Scenario: Verify upload component properties
    Given I identify the upload component with label "Resume Upload"
    Then the upload component "Resume Upload" should support multiple files
    And I should see the upload component summary for "Resume Upload"

  @UPLOAD-008
  Scenario: Verify disabled upload component
    Then the upload component "Disabled Upload" should be disabled

  @UPLOAD-009
  Scenario: View all upload components on page
    Then I should see the upload component summary



