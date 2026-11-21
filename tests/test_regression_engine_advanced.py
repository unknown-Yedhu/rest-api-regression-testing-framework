import json
import pytest

from framework.regression_engine import RegressionEngine


# --------------------------------------------------
# FIXTURE
# --------------------------------------------------

@pytest.fixture
def engine(tmp_path):

    return RegressionEngine(
        snapshot_dir=str(tmp_path)
    )


# --------------------------------------------------
# BASELINE METADATA
# --------------------------------------------------

def test_baseline_contains_execution_metadata(engine):

    engine.api_runner.send_request = lambda **kwargs: {
        "success": True,
        "method": "GET",
        "url": "http://127.0.0.1:5000/api/health",
        "status_code": 200,
        "headers": {},
        "response_body": {
            "status": "healthy"
        },
        "response_time": 0.01,
        "error": None
    }

    result = engine.capture_baseline(
        endpoint="/api/health",
        snapshot_name="health_metadata"
    )

    assert result["success"] is True

    assert result["status"] == "BASELINE_CAPTURED"

    assert result["timestamp"] is not None

    assert result["execution_time"] >= 0

    assert result["endpoint"] == "/api/health"

    assert result["method"] == "GET"


# --------------------------------------------------
# SNAPSHOT METADATA
# --------------------------------------------------

def test_baseline_snapshot_metadata(engine):

    engine.api_runner.send_request = lambda **kwargs: {
        "success": True,
        "method": "GET",
        "url": "http://127.0.0.1:5000/api/health",
        "status_code": 200,
        "headers": {},
        "response_body": {
            "status": "healthy"
        },
        "response_time": 0.01,
        "error": None
    }

    engine.capture_baseline(
        endpoint="/api/health",
        snapshot_name="health_metadata"
    )

    metadata = engine.snapshot_manager.load_metadata(
        "health_metadata"
    )

    assert metadata is not None

    assert metadata["endpoint"] == "/api/health"

    assert metadata["method"] == "GET"

    assert metadata["status_code"] == 200

    assert metadata["captured_at"] is not None


# --------------------------------------------------
# REGRESSION EXECUTION METADATA
# --------------------------------------------------

def test_regression_result_contains_execution_metadata(engine):

    engine.snapshot_manager.save_snapshot(
        "health_baseline",
        {
            "status_code": 200,
            "response_body": {
                "status": "healthy"
            }
        }
    )

    engine.api_runner.send_request = lambda **kwargs: {
        "success": True,
        "method": "GET",
        "url": "http://127.0.0.1:5000/api/health",
        "status_code": 200,
        "headers": {},
        "response_body": {
            "status": "healthy"
        },
        "response_time": 0.01,
        "error": None
    }

    result = engine.run_regression_test(
        endpoint="/api/health",
        snapshot_name="health_baseline"
    )

    assert result["success"] is True

    assert result["status"] == "PASSED"

    assert result["timestamp"] is not None

    assert result["execution_time"] >= 0

    assert result["method"] == "GET"

    assert result["endpoint"] == "/api/health"


# --------------------------------------------------
# BASELINE UPDATE
# --------------------------------------------------

def test_update_baseline(engine):

    engine.api_runner.send_request = lambda **kwargs: {
        "success": True,
        "method": "GET",
        "url": "http://127.0.0.1:5000/api/health",
        "status_code": 200,
        "headers": {},
        "response_body": {
            "status": "updated"
        },
        "response_time": 0.01,
        "error": None
    }

    result = engine.update_baseline(
        endpoint="/api/health",
        snapshot_name="health_baseline"
    )

    assert result["success"] is True

    assert result["status"] == "BASELINE_UPDATED"

    assert result["message"] == (
        "Baseline snapshot updated successfully."
    )

    snapshot = engine.snapshot_manager.load_snapshot(
        "health_baseline"
    )

    assert snapshot["response_body"]["status"] == "updated"


# --------------------------------------------------
# LIST BASELINES
# --------------------------------------------------

def test_list_baselines(engine):

    engine.snapshot_manager.save_snapshot(
        "baseline_one",
        {
            "status_code": 200,
            "response_body": {}
        }
    )

    engine.snapshot_manager.save_snapshot(
        "baseline_two",
        {
            "status_code": 200,
            "response_body": {}
        }
    )

    baselines = engine.list_baselines()

    names = [
        baseline["name"]
        for baseline in baselines
    ]

    assert "baseline_one" in names

    assert "baseline_two" in names

    assert len(baselines) == 2


# --------------------------------------------------
# DELETE BASELINE
# --------------------------------------------------

def test_delete_baseline(engine):

    engine.snapshot_manager.save_snapshot(
        "baseline_to_delete",
        {
            "status_code": 200,
            "response_body": {}
        }
    )

    result = engine.delete_baseline(
        "baseline_to_delete"
    )

    assert result is True

    assert engine.snapshot_manager.snapshot_exists(
        "baseline_to_delete"
    ) is False


# --------------------------------------------------
# CORRUPTED BASELINE
# --------------------------------------------------

def test_corrupted_baseline_is_handled(engine):

    snapshot_path = (
        engine.snapshot_manager.snapshot_dir
        / "corrupted_baseline.json"
    )

    snapshot_path.write_text(
        "{invalid json",
        encoding="utf-8"
    )

    result = engine.run_regression_test(
        endpoint="/api/health",
        snapshot_name="corrupted_baseline"
    )

    assert result["success"] is False

    assert result["status"] == "ERROR"

    assert result["message"] == (
        "Unable to load baseline snapshot."
    )

    assert result["error_type"] == "ValueError"


# --------------------------------------------------
# BASELINE CAPTURE FAILURE
# --------------------------------------------------

def test_baseline_capture_failure_contains_metadata(engine):

    engine.api_runner.send_request = lambda **kwargs: {
        "success": False,
        "method": "GET",
        "url": "http://127.0.0.1:5000/api/health",
        "status_code": None,
        "headers": {},
        "response_body": None,
        "response_time": None,
        "error": "Unable to connect to API",
        "error_type": "ConnectionError"
    }

    result = engine.capture_baseline(
        endpoint="/api/health",
        snapshot_name="failed_baseline"
    )

    assert result["success"] is False

    assert result["status"] == "FAILED"

    assert result["error"] == (
        "Unable to connect to API"
    )

    assert result["timestamp"] is not None

    assert result["execution_time"] >= 0


# --------------------------------------------------
# BASELINE UPDATE FAILURE
# --------------------------------------------------

def test_update_baseline_failure(engine):

    engine.api_runner.send_request = lambda **kwargs: {
        "success": False,
        "method": "GET",
        "url": "http://127.0.0.1:5000/api/health",
        "status_code": None,
        "headers": {},
        "response_body": None,
        "response_time": None,
        "error": "Unable to connect to API",
        "error_type": "ConnectionError"
    }

    result = engine.update_baseline(
        endpoint="/api/health",
        snapshot_name="failed_update"
    )

    assert result["success"] is False

    assert result["status"] == "FAILED"

    assert result["message"] == (
        "Failed to capture baseline."
    )


# --------------------------------------------------
# HTTP METHOD HANDLING
# --------------------------------------------------

def test_regression_method_is_normalized(engine):

    engine.snapshot_manager.save_snapshot(
        "health_baseline",
        {
            "status_code": 200,
            "response_body": {
                "status": "healthy"
            }
        }
    )

    captured_arguments = {}

    def mock_request(**kwargs):

        captured_arguments.update(kwargs)

        return {
            "success": True,
            "method": "GET",
            "url": "http://127.0.0.1:5000/api/health",
            "status_code": 200,
            "headers": {},
            "response_body": {
                "status": "healthy"
            },
            "response_time": 0.01,
            "error": None
        }

    engine.api_runner.send_request = mock_request

    result = engine.run_regression_test(
        endpoint="/api/health",
        snapshot_name="health_baseline",
        method="get"
    )

    assert result["method"] == "GET"

    assert captured_arguments["method"] == "GET"