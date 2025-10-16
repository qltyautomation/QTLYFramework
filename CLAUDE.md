# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QLTYFramework is a mobile automation testing framework built on Appium for iOS and Android platforms. It provides a comprehensive testing solution with integrations for reporting, CI/CD, and cloud testing services.

## Development Commands

### Installation
```bash
pip install -e .
```

### Running Tests
```bash
# Run all tests
python -m qlty.qlty_tests -p [ios|android]

# Run single test
python -m qlty.qlty_tests -p ios -t TestClassName.test_method_name

# Run with integrations
python -m qlty.qlty_tests -p android -s     # Enable Slack
python -m qlty.qlty_tests -p ios -l         # Enable SauceLabs
```

### Command Line Arguments
- `-p, --platform`: Target platform [ios, android, android_web, ios_web, chrome, firefox] (required)
- `-s, --slack`: Enable Slack notifications
- `-t, --test`: Run single test case
- `-f, --report-on-fail`: Generate reports even for failed tests
- `-l, --saucelabs`: Run tests on SauceLabs
- `-d, --managed`: Enable managed driver functionality

## Architecture

### Core Components

**qlty/config.py**: Framework-wide configuration settings
- Platform selection
- Integration toggles (Slack, SauceLabs)
- Environment configurations

**qlty/qlty_tests.py**: Main test runner entry point
- Orchestrates test discovery and execution
- Manages test lifecycle (setup → execute → report)
- Coordinates with TestReporter and TestRunnerUtils

### Package Structure

**qlty/classes/core/**
- `qlty_testcase.py`: Base test case class (extends unittest.TestCase)
  - Manages driver initialization and teardown
  - Handles result collection and log capture
- `test_runner_utils.py`: Test execution utilities
  - Platform detection helpers
  - Result aggregation and formatting
  - Integration orchestration (Slack, SauceLabs)
- `test_reporter.py`: Test result collection and tracking
  - Registers test cases with metadata (target, feature)
  - Tracks execution status, duration, and messages
  - Associates test case IDs for external tracking
- `test_target.py`: Test target enum (UI, API)

**qlty/classes/selenium/**
- `selenium_operations.py`: WebDriver interaction wrappers
- `web_element_operations.py`: Element manipulation utilities

**qlty/classes/integrations/**
- `slack_reporter.py`: Slack notification integration
- `saucelabs_integration.py`: SauceLabs cloud testing integration

**qlty/utilities/**
- `utils.py`: Common utilities (logging, screenshots, file operations)
- `argument_parser.py`: CLI argument parsing and validation
- `selenium_utils.py`: Driver initialization and management

### Test Case Workflow

1. **Initialization** (`QLTYTestCase.setUp()`)
   - Driver initialization based on platform and configuration
   - Platform-specific capabilities loaded from `settings.py`

2. **Execution** (Test method)
   - Use `self.get_driver()` to access WebDriver
   - Framework handles assertions through unittest

3. **Teardown** (`QLTYTestCase.tearDown()`)
   - Results registered with TestReporter
   - Logs and screenshots captured (if enabled)
   - SauceLabs result posting (if enabled)
   - Driver cleanup

4. **Reporting** (`TestRunnerUtils.report()`)
   - Slack notifications
   - SauceLabs results linking
   - Console output

### Configuration Requirements

Tests require a `settings.py` file in the test repository root with:

```python
# Debug level
DEBUG_LEVEL = logging.DEBUG

# Test run metadata
TEST_RUN_ID = None
PROJECT_CONFIG = {
    'PROJECT_NAME': 'YourProject',
    'RELEASE': '1.0',
    'ENVIRONMENT': 'QA',
    'SOURCE_REPO': 'https://github.com/...'
}

# Selenium/Appium configuration
SELENIUM = {
    'TIMEOUT': 30,
    'APPIUM': {'URL': 'http://localhost:4723'},
    'CAPABILITIES': {
        'ios': {...},
        'android': {...},
        # Add _saucelabs variants if using SauceLabs
    }
}

# Integration settings (optional, based on flags used)
SLACK = {'SLACK_AUTH_TOKEN': os.getenv('SLACK_TOKEN'), 'CHANNEL_ID': 'C123456'}
SAUCELABS = {'USERNAME': '...', 'ACCESS_KEY': '...', 'URL': '...'}
GUS = {'ORG_ID': '...', 'URL': '...', 'PRODUCT_TAG': {...}, ...}
JENKINS = {'JOBS': {...}}
```

### Writing Tests

Create test classes extending `QLTYTestCase`:

```python
from qlty.classes.core.qlty_testcase import QLTYTestCase
from qlty.classes.core.test_target import TestTarget
from qlty.qlty_tests import test_reporter

class MyTestClass(QLTYTestCase):
    def setUp(self):
        super().setUp()
        # Register with reporter
        test_reporter.register_test_case(
            self,
            case_ids=[12345],  # External tracking IDs
            feature_name='Login',
            test_target=TestTarget.UI
        )

    def test_my_feature(self):
        driver = self.get_driver()
        # Test implementation
```

### Important Notes

- All imports use `qlty` package name (not torch)
- Base test class is `QLTYTestCase` (not TorchTestCase)
- Argument parser is `QLTYArgumentParser`
- Main test runner function is `qlty()` in `qlty_tests.py`
- JAR files in `qlty/jars/` are included for Java-based integrations
- Platform detection uses `config.CURRENT_PLATFORM`
- Managed drivers mode bypasses default driver initialization
