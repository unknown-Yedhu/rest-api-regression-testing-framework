import pytest

from framework.regression_engine import RegressionEngine


@pytest.fixture
def engine(tmp_path):
    return RegressionEngine(
        snapshot_dir=str(tmp_path)
    )


def test_capture_baseline(engine):
    """
    Test whether an API response can be captured
    and saved as a baseline snapshot.
    """

    engine.api_runner.send_request = lambda **kwargs: {
        "success": True,
        "method": "GET",
        "url": "http://127.0.0.1:5000/api/health",
        "status_code": 200,
        "headers": {},
        "response_body": {
            "status": "healthy",
            "service": "Product API"
        },
        "response_time": 0.01,
        "error": None
    }

    result = engine.capture_baseline(
        endpoint="/api/health",
        snapshot_name="health_baseline"
    )

    assert result["success"] is True
    assert result["status_code"] == 200
    assert engine.snapshot_manager.snapshot_exists(
        "health_baseline"
    )


def test_regression_test_passes_when_responses_match(engine):
    """
    Test that the regression engine passes when
    the current response matches the baseline.
    """

    baseline_data = {
        "status_code": 200,
        "response_body": {
            "status": "healthy",
            "service": "Product API"
        }
    }

    engine.snapshot_manager.save_snapshot(
        "health_baseline",
        baseline_data
    )

    engine.api_runner.send_request = lambda **kwargs: {
        "success": True,
        "method": "GET",
        "url": "http://127.0.0.1:5000/api/health",
        "status_code": 200,
        "headers": {},
        "response_body": {
            "status": "healthy",
            "service": "Product API"
        },
        "response_time": 0.01,
        "error": None
    }

    result = engine.run_regression_test(
        endpoint="/api/health",
        snapshot_name="health_baseline"
    )

    assert result["success"] is True
    assert result["regression_detected"] is False
    assert result["status"] == "PASSED"
    assert result["comparison"]["match"] is True


def test_regression_detected_when_response_changes(engine):
    """
    Test that a regression is detected when
    the API response differs from the baseline.
    """

    baseline_data = {
        "status_code": 200,
        "response_body": {
            "status": "healthy",
            "service": "Product API"
        }
    }

    engine.snapshot_manager.save_snapshot(
        "health_baseline",
        baseline_data
    )

    engine.api_runner.send_request = lambda **kwargs: {
        "success": True,
        "method": "GET",
        "url": "http://127.0.0.1:5000/api/health",
        "status_code": 200,
        "headers": {},
        "response_body": {
            "status": "unhealthy",
            "service": "Product API"
        },
        "response_time": 0.01,
        "error": None
    }

    result = engine.run_regression_test(
        endpoint="/api/health",
        snapshot_name="health_baseline"
    )

    assert result["success"] is True
    assert result["regression_detected"] is True
    assert result["status"] == "FAILED"
    assert result["comparison"]["match"] is False
    assert result["comparison"]["total_differences"] > 0


def test_missing_baseline(engine):
    """
    Test handling when the requested baseline
    snapshot does not exist.
    """

    result = engine.run_regression_test(
        endpoint="/api/health",
        snapshot_name="missing_baseline"
    )

    assert result["success"] is False
    assert result["regression_detected"] is None
    assert result["message"] == "Baseline snapshot does not exist."


def test_api_request_failure(engine):
    """
    Test handling when the API request fails.
    """

    engine.snapshot_manager.save_snapshot(
        "health_baseline",
        {
            "status_code": 200,
            "response_body": {
                "status": "healthy",
                "service": "Product API"
            }
        }
    )

    engine.api_runner.send_request = lambda **kwargs: {
        "success": False,
        "method": "GET",
        "url": "http://127.0.0.1:5000/api/health",
        "status_code": None,
        "headers": {},
        "response_body": None,
        "response_time": None,
        "error": "Unable to connect to API"
    }

    result = engine.run_regression_test(
        endpoint="/api/health",
        snapshot_name="health_baseline"
    )

    assert result["success"] is False
    assert result["regression_detected"] is True
    assert result["message"] == "API request failed."