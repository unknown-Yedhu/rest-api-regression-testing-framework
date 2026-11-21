import json
import pytest

from framework.test_suite import RegressionTestSuite


@pytest.fixture
def test_suite(tmp_path):
    return RegressionTestSuite(
        base_url="http://127.0.0.1:5000",
        snapshot_dir=tmp_path / "snapshots",
        report_dir=tmp_path / "reports"
    )


@pytest.fixture
def valid_config(tmp_path):
    config = {
        "project": {
            "name": "Test Framework",
            "version": "1.0.0",
            "description": "Testing configuration integration"
        },
        "api": {
            "base_url": "http://127.0.0.1:5000",
            "timeout": 10
        },
        "directories": {
            "snapshots": str(tmp_path / "snapshots"),
            "reports": str(tmp_path / "reports")
        },
        "settings": {
            "save_response_headers": True,
            "save_response_time": True,
            "compare_status_codes": True,
            "compare_response_body": True
        },
        "tests": [
            {
                "name": "Health Check",
                "endpoint": "/api/health",
                "method": "GET",
                "snapshot": "health_baseline",
                "enabled": True
            },
            {
                "name": "Get All Products",
                "endpoint": "/api/products",
                "method": "GET",
                "snapshot": "products_baseline",
                "enabled": True
            },
            {
                "name": "Disabled Test",
                "endpoint": "/api/disabled",
                "method": "GET",
                "snapshot": "disabled_baseline",
                "enabled": False
            }
        ]
    }

    config_path = tmp_path / "config.json"

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4)

    return config_path


# --------------------------------------------------
# TEST: Initialization
# --------------------------------------------------

def test_test_suite_initialization(test_suite):

    assert test_suite.tests == []
    assert test_suite.results == []
    assert test_suite.regression_engine is not None
    assert test_suite.report_generator is not None


# --------------------------------------------------
# TEST: Add Test
# --------------------------------------------------

def test_add_test(test_suite):

    test_case = test_suite.add_test(
        test_name="Health Check",
        endpoint="/api/health",
        snapshot_name="health_baseline",
        method="GET"
    )

    assert len(test_suite.tests) == 1
    assert test_case["test_name"] == "Health Check"
    assert test_case["endpoint"] == "/api/health"
    assert test_case["snapshot_name"] == "health_baseline"
    assert test_case["method"] == "GET"


# --------------------------------------------------
# TEST: Add Multiple Tests
# --------------------------------------------------

def test_add_multiple_tests(test_suite):

    test_suite.add_test(
        test_name="Health Check",
        endpoint="/api/health",
        snapshot_name="health_baseline"
    )

    test_suite.add_test(
        test_name="Products",
        endpoint="/api/products",
        snapshot_name="products_baseline"
    )

    assert len(test_suite.tests) == 2


# --------------------------------------------------
# TEST: Clear Tests
# --------------------------------------------------

def test_clear_tests(test_suite):

    test_suite.add_test(
        test_name="Health Check",
        endpoint="/api/health",
        snapshot_name="health_baseline"
    )

    test_suite.results.append({"status": "PASSED"})

    test_suite.clear_tests()

    assert len(test_suite.tests) == 0
    assert len(test_suite.results) == 0


# --------------------------------------------------
# TEST: Configuration Initialization
# --------------------------------------------------

def test_initialize_with_config(valid_config):

    suite = RegressionTestSuite(
        config_path=valid_config
    )

    assert suite.config_manager is not None

    assert (
        suite.regression_engine.api_runner.base_url
        == "http://127.0.0.1:5000"
    )


# --------------------------------------------------
# TEST: Load Tests from Configuration
# --------------------------------------------------

def test_load_tests_from_config(valid_config):

    suite = RegressionTestSuite(
        config_path=valid_config
    )

    tests = suite.load_tests_from_config()

    assert len(tests) == 2

    assert tests[0]["test_name"] == "Health Check"
    assert tests[0]["endpoint"] == "/api/health"
    assert tests[0]["snapshot_name"] == "health_baseline"

    assert tests[1]["test_name"] == "Get All Products"
    assert tests[1]["endpoint"] == "/api/products"


# --------------------------------------------------
# TEST: Disabled Tests Are Not Loaded
# --------------------------------------------------

def test_disabled_tests_are_not_loaded(valid_config):

    suite = RegressionTestSuite(
        config_path=valid_config
    )

    suite.load_tests_from_config()

    test_names = [
        test["test_name"]
        for test in suite.tests
    ]

    assert "Disabled Test" not in test_names


# --------------------------------------------------
# TEST: Configuration Required
# --------------------------------------------------

def test_load_tests_without_config(test_suite):

    with pytest.raises(
        ValueError,
        match="Configuration file has not been loaded"
    ):

        test_suite.load_tests_from_config()


# --------------------------------------------------
# TEST: Run Single Test
# --------------------------------------------------

def test_run_test(test_suite, monkeypatch):

    test_case = {
        "test_name": "Health Check",
        "endpoint": "/api/health",
        "snapshot_name": "health_baseline",
        "method": "GET",
        "request_kwargs": {}
    }

    expected_result = {
        "success": True,
        "regression_detected": False,
        "status": "PASSED",
        "message": "No regression detected."
    }

    def mock_run_regression_test(**kwargs):
        return expected_result.copy()

    monkeypatch.setattr(
        test_suite.regression_engine,
        "run_regression_test",
        mock_run_regression_test
    )

    result = test_suite.run_test(test_case)

    assert result["test_name"] == "Health Check"
    assert result["status"] == "PASSED"


# --------------------------------------------------
# TEST: Failed Test
# --------------------------------------------------

def test_run_failed_test(test_suite, monkeypatch):

    test_case = {
        "test_name": "Failed Test",
        "endpoint": "/api/test",
        "snapshot_name": "test_baseline",
        "method": "GET",
        "request_kwargs": {}
    }

    expected_result = {
        "success": False,
        "regression_detected": True,
        "message": "API request failed."
    }

    def mock_run_regression_test(**kwargs):
        return expected_result.copy()

    monkeypatch.setattr(
        test_suite.regression_engine,
        "run_regression_test",
        mock_run_regression_test
    )

    result = test_suite.run_test(test_case)

    assert result["status"] == "FAILED"


# --------------------------------------------------
# TEST: Run All Tests
# --------------------------------------------------

def test_run_all(test_suite, monkeypatch):

    test_suite.add_test(
        test_name="Test 1",
        endpoint="/api/test1",
        snapshot_name="snapshot1"
    )

    test_suite.add_test(
        test_name="Test 2",
        endpoint="/api/test2",
        snapshot_name="snapshot2"
    )

    def mock_run_test(test_case):

        return {
            "test_name": test_case["test_name"],
            "status": "PASSED",
            "success": True
        }

    monkeypatch.setattr(
        test_suite,
        "run_test",
        mock_run_test
    )

    results = test_suite.run_all()

    assert len(results) == 2
    assert len(test_suite.results) == 2


# --------------------------------------------------
# TEST: Generate Report
# --------------------------------------------------

def test_generate_report(test_suite):

    test_suite.results = [
        {
            "test_name": "Test 1",
            "status": "PASSED"
        },
        {
            "test_name": "Test 2",
            "status": "FAILED"
        }
    ]

    report = test_suite.generate_report()

    assert report["summary"]["total_tests"] == 2
    assert report["summary"]["passed"] == 1
    assert report["summary"]["failed"] == 1


# --------------------------------------------------
# TEST: Save Report
# --------------------------------------------------

def test_save_report(test_suite):

    test_suite.results = [
        {
            "test_name": "Test 1",
            "status": "PASSED"
        }
    ]

    result = test_suite.save_report(
        filename="test_report.json"
    )

    assert result["success"] is True
    assert "report_path" in result


# --------------------------------------------------
# TEST: Run and Report
# --------------------------------------------------

def test_run_and_report(test_suite, monkeypatch):

    test_suite.add_test(
        test_name="Test 1",
        endpoint="/api/test",
        snapshot_name="test_snapshot"
    )

    def mock_run_all():

        test_suite.results = [
            {
                "test_name": "Test 1",
                "status": "PASSED"
            }
        ]

        return test_suite.results

    monkeypatch.setattr(
        test_suite,
        "run_all",
        mock_run_all
    )

    result = test_suite.run_and_report()

    assert result["success"] is True
    assert len(result["report"]["test_results"]) == 1