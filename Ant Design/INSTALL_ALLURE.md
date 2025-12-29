# Installing Allure Framework on Windows

## Prerequisites

Allure requires Java to be installed. Check if Java is installed:
```powershell
java -version
```

If Java is not installed, download and install it from: https://www.oracle.com/java/technologies/downloads/

## Installation Methods

### Method 1: Manual Installation (Recommended)

1. **Download Allure:**
   - Go to: https://github.com/allure-framework/allure2/releases
   - Download the latest `allure-commandline-*.zip` file
   - Example: `allure-commandline-2.24.0.zip`

2. **Extract the ZIP file:**
   - Extract to a folder, e.g., `C:\allure` or `C:\Program Files\allure`

3. **Add to PATH:**
   - Open System Properties → Environment Variables
   - Edit the "Path" variable in System variables
   - Add the `bin` folder path, e.g., `C:\allure\bin`
   - Click OK to save

4. **Verify Installation:**
   ```powershell
   allure --version
   ```

### Method 2: Using Chocolatey (if installed)

```powershell
choco install allure
```

### Method 3: Using Winget (Windows Package Manager)

```powershell
winget install allure
```

## After Installation

Once Allure is installed, the test framework will automatically:
1. Generate Allure results during test execution
2. Generate and open the Allure report after tests complete

## Manual Report Generation

If you need to generate the report manually:

```powershell
# Generate report
allure generate reports/allure-results --clean -o reports/allure-report

# Open report in browser
allure open reports/allure-report
```

Or use the provided script:
```powershell
python generate_allure_report.py
```

