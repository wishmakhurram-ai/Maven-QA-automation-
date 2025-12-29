"""
Gherkin step definitions for Ant Design Upload component automation
Uses pytest-bdd for BDD-style testing
"""
from pytest_bdd import given, when, then, parsers
from framework.components.upload_handler import UploadHandler


@given(parsers.parse('I identify the upload component with label "{upload_label}"'))
def step_identify_upload_by_label(context, upload_label):
    """
    Identify an upload component by label and store in context
    """
    print(f"   >> Identifying upload component: '{upload_label}'")
    upload = context.upload_handler.locator.find_upload_by_label(upload_label)
    assert upload is not None, f"Upload component '{upload_label}' not found"
    
    # Store in context
    if not hasattr(context, 'upload_context'):
        context.upload_context = {}
    context.upload_context['current_upload'] = upload
    context.upload_context['current_label'] = upload_label
    
    print(f"   >> Upload component identified: '{upload_label}'")


@when(parsers.parse('I upload "{file_path}" using "{upload_label}"'))
def step_upload_file(context, file_path, upload_label):
    """
    Upload a single file to an upload component
    
    Examples:
        When I upload "document.pdf" using "Profile Photo Upload"
        When I upload "resume.docx" using "Resume Upload"
    """
    print(f"   >> Uploading file '{file_path}' to '{upload_label}'")
    success = context.upload_handler.upload_file(upload_label, file_path)
    assert success, f"Failed to upload file '{file_path}' to '{upload_label}'"
    print(f"   >> File uploaded successfully")


@when(parsers.parse('I upload file "{file_path}" to "{upload_label}"'))
def step_upload_file_alt(context, file_path, upload_label):
    """
    Alternative syntax for uploading a file
    """
    step_upload_file(context, file_path, upload_label)


@when(parsers.parse('I drag and drop file "{file_path}" into "{upload_label}"'))
def step_drag_drop_upload(context, file_path, upload_label):
    """
    Upload file using drag and drop to dragger zone
    
    Examples:
        When I drag and drop file "report.pdf" into "Supporting Documents"
        When I drag and drop file "image.png" into "Drop Zone"
    """
    print(f"   >> Drag and drop uploading file '{file_path}' to '{upload_label}'")
    success = context.upload_handler.drag_and_drop_upload(upload_label, file_path)
    assert success, f"Failed to drag and drop file '{file_path}' to '{upload_label}'"
    print(f"   >> File drag and drop uploaded successfully")


@when(parsers.parse('I upload multiple files into "{upload_label}"'))
def step_upload_multiple_files(context, upload_label):
    """
    Upload multiple files to an upload component
    Files should be provided in context.upload_files list
    
    Examples:
        Given I have files ["file1.pdf", "file2.pdf"]
        When I upload multiple files into "Attachments"
    """
    if not hasattr(context, 'upload_files') or not context.upload_files:
        raise ValueError("No files provided. Set context.upload_files = ['file1.pdf', 'file2.pdf']")
    
    print(f"   >> Uploading {len(context.upload_files)} files to '{upload_label}'")
    success = context.upload_handler.upload_multiple_files(upload_label, context.upload_files)
    assert success, f"Failed to upload multiple files to '{upload_label}'"
    print(f"   >> Multiple files uploaded successfully")


@when(parsers.parse('I upload files {file_list} to "{upload_label}"'))
def step_upload_files_list(context, file_list, upload_label):
    """
    Upload multiple files from a list in Gherkin
    
    Examples:
        When I upload files ["document.pdf", "image.png"] to "Documents"
    """
    # Parse file list from string
    import ast
    try:
        files = ast.literal_eval(file_list)
        if not isinstance(files, list):
            files = [files]
    except:
        # Fallback: split by comma
        files = [f.strip().strip('"\'') for f in file_list.strip('[]').split(',')]
    
    print(f"   >> Uploading {len(files)} files to '{upload_label}'")
    success = context.upload_handler.upload_multiple_files(upload_label, files)
    assert success, f"Failed to upload files to '{upload_label}'"
    print(f"   >> Files uploaded successfully")


@when(parsers.parse('I click the picture-card upload "{upload_label}"'))
def step_click_picture_card(context, upload_label):
    """
    Click a picture-card upload to open file selection
    
    Examples:
        When I click the picture-card upload "Profile Photo"
    """
    print(f"   >> Clicking picture-card upload '{upload_label}'")
    result = context.upload_handler.click_picture_card_upload(upload_label)
    assert result is not None, f"Failed to click picture-card upload '{upload_label}'"
    print(f"   >> Picture-card clicked successfully")


@when(parsers.parse('I delete file "{file_name}" from "{upload_label}"'))
def step_delete_uploaded_file(context, file_name, upload_label):
    """
    Delete an uploaded file from upload list
    
    Examples:
        When I delete file "document.pdf" from "Attachments"
    """
    print(f"   >> Deleting file '{file_name}' from '{upload_label}'")
    success = context.upload_handler.delete_uploaded_file(upload_label, file_name)
    assert success, f"Failed to delete file '{file_name}' from '{upload_label}'"
    print(f"   >> File deleted successfully")


@then(parsers.parse('the upload list for "{upload_label}" should show {count:d} file(s)'))
def step_verify_upload_count(context, upload_label, count):
    """
    Verify the number of uploaded files
    
    Examples:
        Then the upload list for "Attachments" should show 2 files
        Then the upload list for "Documents" should show 1 file
    """
    print(f"   >> Verifying upload count for '{upload_label}'")
    actual_count = context.upload_handler.get_upload_count(upload_label)
    assert actual_count == count, \
        f"Expected {count} file(s), but found {actual_count} in '{upload_label}'"
    print(f"   >> Upload count verified: {count} file(s)")


@then(parsers.parse('the upload list for "{upload_label}" should contain "{file_name}"'))
def step_verify_file_in_upload_list(context, upload_label, file_name):
    """
    Verify that a specific file is in the upload list
    
    Examples:
        Then the upload list for "Attachments" should contain "document.pdf"
    """
    print(f"   >> Verifying file '{file_name}' in '{upload_label}'")
    uploaded_files = context.upload_handler.get_uploaded_files(upload_label)
    
    # Check if file name matches (case-insensitive, partial match)
    found = any(file_name.lower() in f.lower() or f.lower() in file_name.lower() 
                for f in uploaded_files)
    assert found, \
        f"File '{file_name}' not found in upload list. Found: {uploaded_files}"
    print(f"   >> File '{file_name}' found in upload list")


@then(parsers.parse('the upload component "{upload_label}" should be disabled'))
def step_verify_upload_disabled(context, upload_label):
    """
    Verify that an upload component is disabled
    """
    print(f"   >> Verifying upload component '{upload_label}' is disabled")
    upload = context.upload_handler.locator.find_upload_by_label(upload_label)
    assert upload is not None, f"Upload component '{upload_label}' not found"
    
    upload_info = context.upload_handler.identifier.identify_upload(upload)
    assert upload_info['disabled'], \
        f"Upload component '{upload_label}' is not disabled"
    print(f"   >> Upload component is disabled as expected")


@then(parsers.parse('the upload component "{upload_label}" should support multiple files'))
def step_verify_multiple_upload(context, upload_label):
    """
    Verify that an upload component supports multiple files
    """
    print(f"   >> Verifying '{upload_label}' supports multiple files")
    upload = context.upload_handler.locator.find_upload_by_label(upload_label)
    assert upload is not None, f"Upload component '{upload_label}' not found"
    
    upload_info = context.upload_handler.identifier.identify_upload(upload)
    assert upload_info['multiple'], \
        f"Upload component '{upload_label}' does not support multiple files"
    print(f"   >> Upload component supports multiple files")


@then('I should see the upload component summary')
def step_show_upload_summary(context):
    """
    Print summary of all upload components on the page
    """
    print(f"   >> Generating upload component summary")
    context.upload_handler.print_upload_summary()


@then(parsers.parse('I should see the upload component summary for "{upload_label}"'))
def step_show_upload_summary_specific(context, upload_label):
    """
    Print summary of a specific upload component
    """
    print(f"   >> Generating upload component summary for '{upload_label}'")
    context.upload_handler.print_upload_summary(upload_label)


@given(parsers.parse('I have files {file_list}'))
def step_set_upload_files(context, file_list):
    """
    Set files to be uploaded in context
    
    Examples:
        Given I have files ["file1.pdf", "file2.pdf"]
    """
    import ast
    try:
        files = ast.literal_eval(file_list)
        if not isinstance(files, list):
            files = [files]
    except:
        files = [f.strip().strip('"\'') for f in file_list.strip('[]').split(',')]
    
    context.upload_files = files
    print(f"   >> Set {len(files)} file(s) for upload: {files}")



