# Ant Design Upload Component Automation Framework

A complete, locator-less Python + Selenium framework for automatically detecting and automating Ant Design Upload components without manual selectors.

## 🎯 Key Features

✅ **Automatic Detection** - Detects all Ant Design Upload component variations  
✅ **No Hardcoded Selectors** - Uses data-attr-id, structural signals, and DOM traversal  
✅ **Gherkin-Friendly** - Intent-driven testing with natural language  
✅ **All Upload Types** - Supports button, drag-drop, picture-card, picture-list, directory upload  
✅ **Complete Automation** - Upload, delete, verify, and analyze upload components  

## 📁 Framework Structure

```
framework/components/
├── upload_locator.py      # Automatically finds upload components
├── upload_identifier.py   # Analyzes upload properties
└── upload_handler.py      # Handles upload interactions

steps/
└── upload_steps.py        # Gherkin step definitions

features/
└── upload_automation.feature  # Example feature file
```

## 🚀 Quick Start

### 1. Basic Upload

```gherkin
Feature: Upload Files
  Scenario: Upload a single file
    Given I am on the custom application
    When I upload "document.pdf" using "Profile Photo Upload"
    Then the upload list for "Profile Photo Upload" should show 1 file
```

### 2. Multiple Files

```gherkin
Scenario: Upload multiple files
  Given I have files ["file1.pdf", "file2.pdf", "file3.pdf"]
  When I upload multiple files into "Attachments"
  Then the upload list for "Attachments" should show 3 files
```

### 3. Drag and Drop

```gherkin
Scenario: Drag and drop upload
  When I drag and drop file "report.pdf" into "Supporting Documents"
  Then the upload list for "Supporting Documents" should show 1 file
```

## 📝 Available Step Definitions

### Upload Actions

| Step | Description | Example |
|------|-------------|---------|
| `When I upload "{file}" using "{upload_label}"` | Upload single file | `When I upload "resume.pdf" using "Resume Upload"` |
| `When I upload file "{file}" to "{upload_label}"` | Alternative syntax | `When I upload file "doc.pdf" to "Documents"` |
| `When I upload multiple files into "{upload_label}"` | Upload multiple (from context) | `When I upload multiple files into "Attachments"` |
| `When I upload files {list} to "{upload_label}"` | Upload from list | `When I upload files ["a.pdf", "b.pdf"] to "Files"` |
| `When I drag and drop file "{file}" into "{upload_label}"` | Drag and drop upload | `When I drag and drop file "image.png" into "Drop Zone"` |
| `When I click the picture-card upload "{upload_label}"` | Click picture-card | `When I click the picture-card upload "Profile Photo"` |
| `When I delete file "{file}" from "{upload_label}"` | Delete uploaded file | `When I delete file "temp.pdf" from "Attachments"` |

### Verification Steps

| Step | Description | Example |
|------|-------------|---------|
| `Then the upload list for "{upload_label}" should show {count} file(s)` | Verify file count | `Then the upload list for "Attachments" should show 2 files` |
| `Then the upload list for "{upload_label}" should contain "{file}"` | Verify file exists | `Then the upload list for "Files" should contain "document.pdf"` |
| `Then the upload component "{upload_label}" should be disabled` | Verify disabled state | `Then the upload component "Disabled Upload" should be disabled` |
| `Then the upload component "{upload_label}" should support multiple files` | Verify multiple support | `Then the upload component "Files" should support multiple files` |
| `Then I should see the upload component summary` | Show all uploads | `Then I should see the upload component summary` |
| `Then I should see the upload component summary for "{upload_label}"` | Show specific upload | `Then I should see the upload component summary for "Profile Photo"` |

### Setup Steps

| Step | Description | Example |
|------|-------------|---------|
| `Given I identify the upload component with label "{upload_label}"` | Identify and store | `Given I identify the upload component with label "Resume Upload"` |
| `Given I have files {list}` | Set files for upload | `Given I have files ["file1.pdf", "file2.pdf"]` |

## 🔍 How Detection Works

The framework automatically detects upload components using:

1. **data-attr-id** - Primary method when present
2. **Ant Design classes** - `.ant-upload`, `.ant-upload-drag`, etc.
3. **File input presence** - `input[type="file"]` and parent traversal
4. **Aria labels** - `aria-label` containing "upload"
5. **Visible text** - Text patterns like "Click to upload", "Drag file", etc.
6. **Nearby labels** - Label elements near upload components
7. **Fuzzy matching** - Semantic label matching

## 📊 Upload Component Summary

The framework can print a detailed summary of upload components:

```
================================================================================
UPLOAD COMPONENT SUMMARY
================================================================================
Found 3 upload component(s)

[1] Upload Component
  Type: dragger
  List Type: text
  Multiple: True
  Directory: False
  Disabled: False
  Max Count: 5
  Current Count: 2
  Custom Button: False
  Icon Only: False
  Upload Text: Click or drag file to this area to upload
  Data-attr-id: profile-photo-upload
  Aria-label: Profile Photo Upload
  Uploaded Files (2):
    - document1.pdf
    - image1.png
```

## 🎨 Supported Upload Types

### 1. Default Button Upload
- Standard upload button with text
- Icon-only button
- Custom button

### 2. Drag and Drop (Dragger)
- Drag zone with instructions
- "Click or drag file to this area to upload"

### 3. Picture Card
- Square card with "+" icon
- Click to open file selection

### 4. Picture List
- Thumbnail list of uploaded images
- Preview and delete actions

### 5. Directory Upload
- Folder upload support
- Multiple files from directory

## 🔧 Usage Examples

### Example 1: Complete Upload Flow

```gherkin
Feature: Document Upload
  Scenario: Upload and verify documents
    Given I am on the custom application
    When I upload "resume.pdf" using "Resume Upload"
    And I upload "cover_letter.pdf" using "Resume Upload"
    Then the upload list for "Resume Upload" should show 2 files
    And the upload list for "Resume Upload" should contain "resume.pdf"
    And the upload list for "Resume Upload" should contain "cover_letter.pdf"
```

### Example 2: Multiple Files at Once

```gherkin
Scenario: Upload multiple files
  Given I have files ["file1.pdf", "file2.pdf", "file3.pdf"]
  When I upload multiple files into "Attachments"
  Then the upload list for "Attachments" should show 3 files
```

### Example 3: Drag and Drop

```gherkin
Scenario: Drag and drop upload
  When I drag and drop file "report.pdf" into "Supporting Documents"
  Then the upload list for "Supporting Documents" should show 1 file
```

### Example 4: Delete File

```gherkin
Scenario: Delete uploaded file
  Given I upload "temp_file.pdf" using "Attachments"
  And the upload list for "Attachments" should show 1 file
  When I delete file "temp_file.pdf" from "Attachments"
  Then the upload list for "Attachments" should show 0 files
```

### Example 5: Verify Properties

```gherkin
Scenario: Check upload component properties
  Given I identify the upload component with label "Resume Upload"
  Then the upload component "Resume Upload" should support multiple files
  And I should see the upload component summary for "Resume Upload"
```

## 🛠️ Programmatic Usage

You can also use the framework programmatically:

```python
from framework.components.upload_handler import UploadHandler
from selenium import webdriver

driver = webdriver.Chrome()
upload_handler = UploadHandler(driver)

# Upload a file
upload_handler.upload_file("Profile Photo Upload", "photo.jpg")

# Upload multiple files
upload_handler.upload_multiple_files("Attachments", ["file1.pdf", "file2.pdf"])

# Drag and drop
upload_handler.drag_and_drop_upload("Drop Zone", "document.pdf")

# Get uploaded files
files = upload_handler.get_uploaded_files("Attachments")
print(f"Uploaded files: {files}")

# Get upload count
count = upload_handler.get_upload_count("Attachments")
print(f"Upload count: {count}")

# Print summary
upload_handler.print_upload_summary()
```

## ✅ Requirements Met

✅ **Automatic Detection** - Detects all upload variations  
✅ **No Hardcoded Selectors** - Uses structural signals and data-attr-id  
✅ **Gherkin-Friendly** - Natural language step definitions  
✅ **All Upload Types** - Button, drag-drop, picture-card, directory  
✅ **Complete Automation** - Upload, delete, verify, analyze  
✅ **Upload Summary** - Detailed component analysis  

## 📦 Files Created

1. `framework/components/upload_locator.py` - Finds upload components
2. `framework/components/upload_identifier.py` - Analyzes upload properties
3. `framework/components/upload_handler.py` - Handles upload interactions
4. `steps/upload_steps.py` - Gherkin step definitions
5. `features/upload_automation.feature` - Example feature file
6. `tests/test_upload_automation.py` - Test file linking feature

## 🚀 Running Tests

```bash
# Run all upload tests
pytest tests/test_upload_automation.py -v -s

# Run specific scenario
pytest tests/test_upload_automation.py::test_upload_a_single_file -v -s
```

## 📝 Notes

- File paths should be relative to the test execution directory or absolute paths
- The framework automatically handles file input visibility issues
- Upload components are matched by semantic labels (fuzzy matching)
- All upload types are automatically detected and handled appropriately
- The framework respects disabled states and max count limits



