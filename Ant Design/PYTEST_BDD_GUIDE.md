# Complete pytest-bdd Integration Guide

## 📁 Required Folder Structure

```
Ant Design/
├── conftest.py                    # ✅ Pytest fixtures (driver, button_handler, context)
├── pytest.ini                     # ✅ Pytest configuration
├── requirements.txt               # ✅ Updated with pytest-bdd
│
├── features/                      # ✅ Gherkin feature files
│   └── button_automation.feature
│
├── steps/                         # ✅ Step definitions (auto-discovered)
│   └── button_steps.py
│
├── tests/                         # ✅ Test files that link to features
│   └── test_button_automation.py
│
└── framework/                     # ✅ Your existing Selenium framework
    ├── base/
    │   └── base_page.py
    ├── components/
    │   └── button_handler.py
    └── utils/
        └── driver_setup.py
```

---

## 🔧 Key Files Explained

### 1. `conftest.py` - Pytest Fixtures

**Location:** Root directory  
**Purpose:** Provides fixtures (driver, button_handler, context) to all tests

```python
# Automatically discovered by pytest
# Provides: driver, button_handler, context fixtures
```

**Key Points:**
- ✅ Automatically discovered by pytest (no import needed)
- ✅ Fixtures are injected into step definitions
- ✅ `scope="function"` means fresh driver for each test
- ✅ Automatic cleanup (driver.quit() after each test)

---

### 2. `pytest.ini` - Configuration

**Location:** Root directory  
**Purpose:** Configures pytest and pytest-bdd behavior

**Key Settings:**
- `testpaths = tests features` - Where to look for tests
- `bdd_features_base_dir = features` - Where feature files are
- `bdd_steps_base_dir = steps` - Where step definitions are

---

### 3. `tests/test_button_automation.py` - Test Runner

**Location:** `tests/` directory  
**Purpose:** Links `.feature` files to pytest

```python
from pytest_bdd import scenarios

# This line tells pytest-bdd to:
# 1. Find the feature file
# 2. Generate test functions for each scenario
# 3. Match steps to step definitions in steps/
scenarios('../features/button_automation.feature')
```

**How it works:**
- pytest-bdd reads the feature file
- Generates a test function for each `Scenario:`
- Automatically matches steps to step definitions
- Runs each scenario as a separate test

---

### 4. `steps/button_steps.py` - Step Definitions

**Location:** `steps/` directory  
**Purpose:** Defines what each Gherkin step does

**Key Changes from Behave:**
- ✅ `from pytest_bdd import given, when, then` (not `behave`)
- ✅ `parsers.parse()` for parameterized steps
- ✅ Uses `context` fixture (injected automatically)
- ✅ No need for manual driver setup (handled by fixtures)

**Example:**
```python
@given('I am on the button page')
def step_navigate_to_button_page(context):
    # context is automatically injected from conftest.py
    context.driver.get(DEFAULT_URL)
```

---

### 5. `features/button_automation.feature` - Gherkin Scenarios

**Location:** `features/` directory  
**Purpose:** Plain English test scenarios

**No changes needed!** Your existing feature file works as-is.

---

## 🚀 How pytest-bdd Auto-Discovery Works

### Step 1: pytest finds test files
```
pytest looks in: tests/, features/
Finds: tests/test_button_automation.py
```

### Step 2: pytest-bdd reads feature files
```
test_button_automation.py has: scenarios('../features/button_automation.feature')
pytest-bdd reads: features/button_automation.feature
```

### Step 3: pytest-bdd generates test functions
```
For each Scenario: in feature file
  → Creates a test function
  → Example: test_click_a_primary_button()
```

### Step 4: pytest-bdd matches steps
```
For each step in scenario:
  → Looks in steps/ directory
  → Finds matching step definition
  → Injects fixtures (context, driver, etc.)
```

### Step 5: pytest runs tests
```
Each scenario runs as a separate test
Fixtures are created/destroyed automatically
```

---

## 📝 Step Definition Syntax

### Simple Steps (No Parameters)
```python
@when('I click the primary button')
def step_click_primary_button(context):
    # No parsers needed
    step_click_button_by_type(context, 'primary')
```

### Parameterized Steps (With Variables)
```python
@when(parsers.parse('I click the "{button_type}" type button'))
def step_click_button_by_type(context, button_type):
    # button_type is extracted from feature file
    # Example: "I click the primary type button" → button_type = "primary"
```

**Why `parsers.parse()`?**
- Extracts variables from step text
- `"{button_type}"` becomes a function parameter
- Works with any variable name

---

## 🎯 Running Tests

### Install Dependencies
```powershell
pip install -r requirements.txt
```

### Run All Tests
```powershell
pytest
```

### Run Specific Feature File
```powershell
pytest tests/test_button_automation.py
```

### Run Specific Scenario
```powershell
pytest tests/test_button_automation.py -k "Click a primary button"
```

### Run with Verbose Output
```powershell
pytest -v
```

### Run with Detailed Output
```powershell
pytest -vv
```

### Run and Show Print Statements
```powershell
pytest -s
```

### Run with HTML Report
```powershell
pip install pytest-html
pytest --html=report.html
```

---

## 🔍 How Fixtures Work

### Fixture Chain
```
driver fixture
  ↓
button_handler fixture (uses driver)
  ↓
context fixture (uses driver + button_handler)
  ↓
Step definitions (receive context)
```

### Example Flow
```python
# 1. pytest creates driver
driver = DriverSetup.get_chrome_driver()

# 2. pytest creates button_handler using driver
button_handler = ButtonHandler(driver)

# 3. pytest creates context using both
context = Context(driver, button_handler)

# 4. pytest injects context into step definition
@given('I am on the button page')
def step_navigate_to_button_page(context):  # ← context injected here
    context.driver.get(DEFAULT_URL)  # ← uses injected context

# 5. pytest cleans up after test
driver.quit()  # ← automatic cleanup
```

---

## ✅ Verification Checklist

- [x] `conftest.py` exists in root directory
- [x] `pytest.ini` exists in root directory
- [x] `requirements.txt` includes `pytest` and `pytest-bdd`
- [x] `steps/button_steps.py` uses `pytest_bdd` imports
- [x] `tests/test_button_automation.py` imports scenarios
- [x] Feature file path is correct in `scenarios()`
- [x] Step definitions match feature file steps exactly

---

## 🐛 Troubleshooting

### Issue: "Step definition not found"
**Solution:** 
- Check step text matches exactly (case-sensitive)
- Verify `steps/` directory is in `pytest.ini` `bdd_steps_base_dir`
- Check step definition uses correct decorator (`@given`, `@when`, `@then`)

### Issue: "Fixture not found"
**Solution:**
- Verify `conftest.py` is in root directory
- Check fixture name matches what you're using
- Ensure fixture is defined with `@pytest.fixture`

### Issue: "Feature file not found"
**Solution:**
- Check path in `scenarios()` is correct (relative to test file)
- Verify feature file exists
- Check `bdd_features_base_dir` in `pytest.ini`

### Issue: "Driver not closing"
**Solution:**
- Verify `yield` is used in driver fixture (not `return`)
- Check `scope="function"` is set
- Ensure `driver.quit()` is after `yield`

---

## 📊 Example Test Execution

```powershell
$ pytest -v

========================= test session starts =========================
platform win32 -- Python 3.12.0
pytest-bdd 7.1.0
collected 6 items

tests/test_button_automation.py::test_click_a_primary_button PASSED
tests/test_button_automation.py::test_click_a_default_button PASSED
tests/test_button_automation.py::test_click_a_dashed_button PASSED
tests/test_button_automation.py::test_click_a_text_button PASSED
tests/test_button_automation.py::test_click_a_link_button PASSED
tests/test_button_automation.py::test_click_a_danger_button PASSED

========================= 6 passed in 45.23s =========================
```

---

## 🎓 Key Differences: Behave vs pytest-bdd

| Aspect | Behave | pytest-bdd |
|--------|--------|------------|
| **Imports** | `from behave import given, when, then` | `from pytest_bdd import given, when, then` |
| **Context** | Built-in `context` object | Custom `context` fixture |
| **Fixtures** | Not used | Pytest fixtures (`@pytest.fixture`) |
| **Parameters** | Automatic | Use `parsers.parse()` |
| **Discovery** | Automatic in `steps/` | Configured in `pytest.ini` |
| **Running** | `behave` command | `pytest` command |
| **Cleanup** | `after_scenario()` | Fixture teardown (`yield`) |

---

## ✨ Benefits of pytest-bdd

1. ✅ **Full pytest ecosystem** - Use pytest plugins, reports, markers
2. ✅ **Better fixtures** - Reusable, composable fixtures
3. ✅ **Parallel execution** - Run tests in parallel with `pytest-xdist`
4. ✅ **Better debugging** - Use pytest's debugging tools
5. ✅ **HTML reports** - Generate beautiful HTML reports
6. ✅ **CI/CD integration** - Works seamlessly with Jenkins, GitHub Actions, etc.

---

## 📚 Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Run tests: `pytest -v`
3. Check output and verify all scenarios pass
4. Customize fixtures in `conftest.py` as needed
5. Add more feature files and step definitions

---

**You're all set!** 🎉 Your framework is now integrated with pytest-bdd!

