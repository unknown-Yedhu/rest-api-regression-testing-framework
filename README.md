# REST API Regression Testing Framework with Snapshot Testing

A Python-based framework for automated REST API regression testing using snapshot (baseline) testing. The framework captures API responses, stores them as snapshots, compares subsequent responses against saved baselines, detects regressions, and generates detailed test reports.

---

## 📌 Project Overview

The **REST API Regression Testing Framework** is designed to automate the process of testing REST APIs and identifying unintended changes in their behavior.

It uses snapshot testing to establish a baseline response for an API endpoint. During subsequent test executions, the framework compares the current response against the saved baseline and identifies differences in response status codes, headers, JSON structures, data values, and other relevant information.

The framework supports configurable test cases, automated baseline management, regression detection, and report generation.

---

## 🎯 Objectives

- Automate REST API regression testing.
- Capture and maintain API response baselines.
- Detect unexpected changes in API responses.
- Compare JSON responses recursively.
- Support configurable API test cases.
- Handle API errors, timeouts, and unexpected responses.
- Generate JSON and HTML regression reports.
- Provide a command-line interface for test execution and baseline management.

---

## ✨ Features

### 1. API Test Runner
- Supports HTTP methods including GET, POST, PUT, PATCH, DELETE, HEAD, and OPTIONS.
- Handles request headers, query parameters, JSON payloads, and form data.
- Supports authentication configurations.
- Configurable request timeouts.
- SSL verification configuration.
- Captures response status, headers, body, and response time.
- Handles connection errors and request failures.

### 2. Snapshot Management
- Captures and stores API response snapshots.
- Loads previously saved snapshots.
- Supports snapshot versioning and metadata.
- Provides snapshot listing and deletion.
- Prevents invalid snapshot names.
- Handles corrupted snapshot files.
- Uses safe file-writing mechanisms.

### 3. Response Comparison
- Recursively compares JSON responses.
- Detects missing fields.
- Detects unexpected fields.
- Identifies value mismatches.
- Detects data type differences.
- Compares nested objects and arrays.
- Supports numeric tolerance.
- Supports ignored paths for dynamic response fields.

### 4. Regression Engine
- Captures baseline responses.
- Executes regression tests against saved snapshots.
- Identifies API regressions.
- Updates existing baselines.
- Lists and manages snapshots.
- Records execution metadata.

### 5. Configuration Management
- Loads test configuration from JSON.
- Validates configuration values.
- Supports configurable API endpoints.
- Supports configurable HTTP methods and test parameters.
- Allows test cases to be enabled or disabled.
- Supports ignored response paths.

### 6. Test Suite
- Organizes multiple API test cases.
- Executes configured test cases.
- Tracks pass and fail results.
- Generates execution summaries.

### 7. Report Generation
- Generates JSON regression reports.
- Generates HTML regression reports.
- Displays test summaries.
- Reports passed, failed, and skipped tests.
- Displays overall success rate.

---

## 🏗️ Project Architecture

The framework is organized into independent modules:

```text
REST API Regression Testing Framework
│
├── app/
│   └── api.py
│
├── framework/
│   ├── api_test_runner.py
│   ├── config_manager.py
│   ├── regression_engine.py
│   ├── report_generator.py
│   ├── response_comparator.py
│   ├── snapshot_manager.py
│   └── test_suite.py
│
├── tests/
│   ├── test_api_test_runner.py
│   ├── test_api_test_runner_advanced.py
│   ├── test_config_manager.py
│   ├── test_integration.py
│   ├── test_regression_engine.py
│   ├── test_regression_engine_advanced.py
│   ├── test_report_generator.py
│   ├── test_response_comparator.py
│   ├── test_snapshot_manager.py
│   └── test_test_suite.py
│
├── snapshots/
│
├── reports/
│
├── docs/
│
├── config.json
│
├── main.py
│
└── README.md
```

---

## ⚙️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.13 | Core programming language |
| Flask | Sample REST API |
| Requests | HTTP communication |
| Pytest | Automated testing |
| JSON | Configuration and snapshot storage |
| HTML | Regression report generation |
| PowerShell | Development and execution environment |

---

## 🚀 Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- Visual Studio Code or another Python IDE

### 1. Clone the repository

```bash
git clone <repository-url>
```

Navigate into the project directory:

```bash
cd rest-api-regression-testing-framework
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
.venv\Scripts\activate.bat
```

### 4. Install dependencies

```bash
pip install flask requests pytest
```

---

## ▶️ Running the Framework

### Step 1: Start the sample API server

Open a terminal and run:

```bash
python app/api.py
```

The API server will run locally at:

```text
http://127.0.0.1:5000
```

Keep this terminal running.

### Step 2: Run the regression test suite

Open another terminal, activate the virtual environment, and execute:

```bash
python main.py run
```

The framework will:

1. Load the configured test cases.
2. Send requests to the API.
3. Load the corresponding baseline snapshots.
4. Compare current responses with saved snapshots.
5. Detect regressions.
6. Display the test execution summary.
7. Generate the regression report.

---

## 💻 Command-Line Interface

The framework provides several CLI commands.

### Run regression tests

```bash
python main.py run
```

Executes all enabled test cases against the configured API and compares the responses with existing baselines.

### Capture baselines

```bash
python main.py capture
```

Captures the current API responses and saves them as baseline snapshots.

### Update baselines

```bash
python main.py update-baselines
```

Updates existing snapshots using the current API responses.

### Generate a report

```bash
python main.py report
```

Displays the regression test summary and generates the report files.

### Display CLI help

```bash
python main.py --help
```

---

## 🧪 Automated Testing

The framework includes unit tests, advanced tests, and integration tests using Pytest.

Run the complete test suite:

```bash
python -m pytest -v
```

### Test Coverage Areas

- API request execution
- HTTP methods
- Request parameters and headers
- Authentication configurations
- Timeout handling
- Connection errors
- Snapshot capture and loading
- Snapshot versioning
- Snapshot metadata
- Snapshot corruption handling
- JSON response comparison
- Nested data comparison
- Type mismatch detection
- Numeric tolerance
- Ignored paths
- Regression detection
- Baseline updating
- Configuration validation
- Test suite execution
- Report generation
- Integration workflows

### Final Testing Results

| Metric | Result |
|---|---:|
| Total automated tests | 107 |
| Passed | 107 |
| Failed | 0 |
| Success rate | 100% |
| Execution time | 6.08 seconds |

---

## 📊 Reports

The framework generates two report formats.

### JSON Report

```text
reports/regression_report.json
```

Contains structured regression testing results that can be consumed by other tools or systems.

### HTML Report

```text
reports/regression_report.html
```

Provides a visual representation of regression testing results, including:

- Test execution summary
- Total tests
- Passed tests
- Failed tests
- Skipped tests
- Success rate
- Individual test results

---

## 📸 Sample Test Scenarios

The configured test suite includes:

| Test Case | Description |
|---|---|
| Health Check | Verifies the API health endpoint |
| Get All Products | Retrieves the complete product list |
| Get Laptop | Retrieves a specific product |
| Get Smartphone | Retrieves another specific product |
| Get Nonexistent Product | Tests handling of an unavailable product |
| Missing API Endpoint | Tests handling of an invalid endpoint |

---

## 🔄 Regression Testing Workflow

```text
        ┌──────────────────────┐
        │    Start Testing     │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Execute API Request │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Capture API Response │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Load Baseline Snapshot│
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Compare Responses    │
        └──────────┬───────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Changes Detected?│
          └───────┬──────────┘
              Yes │ No
           ┌──────┴──────┐
           ▼             ▼
    ┌────────────┐  ┌────────────┐
    │ Regression │  │ Test Passed│
    │ Detected   │  │            │
    └──────┬─────┘  └──────┬─────┘
           │               │
           └───────┬───────┘
                   ▼
        ┌──────────────────────┐
        │ Generate Test Report │
        └──────────────────────┘
```

---

## ⚡ Performance Testing

Performance testing was conducted to evaluate framework execution time and API response handling.

### Full Regression Suite

The framework was executed repeatedly to measure total execution time.

| Run | Execution Time |
|---|---:|
| Run 1 | 971.40 ms |
| Run 2 | 638.58 ms |
| Run 3 | 658.06 ms |
| Run 4 | 812.94 ms |
| Run 5 | 747.70 ms |
| Run 6 | 916.27 ms |

**Average execution time:** 790.83 ms

**Fastest execution:** 638.58 ms

**Slowest execution:** 971.40 ms

### API Response Time

| Metric | Value |
|---|---:|
| Average API response time | 15.88 ms |
| Fastest response | 4.06 ms |
| Slowest response | 25.54 ms |

### Framework Overhead

| Metric | Value |
|---|---:|
| Average framework overhead | 2.14 ms |
| Minimum overhead | 1.67 ms |
| Maximum overhead | 2.74 ms |

A larger response payload test was also conducted using approximately 1,004 products and a response payload of approximately 140 KB.

---

## 🛡️ Robustness and Edge Case Testing

The framework was tested against several failure scenarios:

- API server unavailable
- Corrupted snapshot JSON
- Unexpected response data
- HTTP 500 responses
- Missing API endpoints
- Slow API responses
- Invalid HTTP methods
- Malformed configuration JSON
- Disabled test cases
- Invalid API base URLs
- Incomplete snapshots
- Empty snapshots
- Invalid snapshot structures
- Missing snapshot files

The framework handled these scenarios gracefully without unexpected crashes.

---

## 🔮 Future Enhancements

Potential future improvements include:

- Parallel test execution
- Support for additional authentication methods
- Database-backed snapshot storage
- CI/CD pipeline integration
- Enhanced test result visualization
- API schema validation
- Additional report formats
- Advanced performance benchmarking
- Test scheduling
- Support for external API testing environments

---

## 🎓 Academic Project

This project was developed as part of a final-year undergraduate project focused on software engineering, automated testing, and API quality assurance.

The project demonstrates practical implementation of:

- Software testing principles
- Regression testing
- Snapshot testing
- Modular software architecture
- API automation
- Test automation
- Error handling
- Performance evaluation
- Report generation

---

## 👨‍💻 Author

**Yedhu Krishnan T A**

BCA Honours – Software Engineering

---

## 📄 License

This project is developed for academic and educational purposes.
