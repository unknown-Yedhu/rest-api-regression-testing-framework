
import pytest

from framework.regression_engine import RegressionEngine


def test_complete_baseline_and_regression_workflow(tmp_path):
    """
    Integration test:
    API Request -> Baseline Capture -> Regression Test -> Comparison
    """

    engine = RegressionEngine(
        base_url="http://127.0.0.1:5000",
        snapshot_dir=str(tmp_path)
    )

    endpoint = "/api/health"
    snapshot_name = "health_endpoint_integration"

    # STEP 1: Capture baseline

    baseline_result = engine.capture_baseline(
        endpoint=endpoint,
        snapshot_name=snapshot_name,
        method="GET"
    )

    assert baseline_result["success"] is True
    assert baseline_result["status"] == "BASELINE_CAPTURED"
    assert baseline_result["status_code"] == 200

    # STEP 2: Verify baseline storage

    assert engine.snapshot_manager.snapshot_exists(
        snapshot_name
    )

    saved_baseline = engine.snapshot_manager.load_snapshot(
        snapshot_name
    )

    assert saved_baseline["status_code"] == 200

    # STEP 3: Run regression test
    # Ignore the dynamic timestamp because it changes
    # with every health check request.

    regression_result = engine.run_regression_test(
        endpoint=endpoint,
        snapshot_name=snapshot_name,
        method="GET",
        ignore_paths=[
            "root.response_body.timestamp"
        ]
    )

    # STEP 4: Verify no regression

    assert regression_result["success"] is True
    assert regression_result["regression_detected"] is False
    assert regression_result["status"] == "PASSED"
    assert regression_result["comparison"]["match"] is True

    # STEP 5: Verify metadata

    assert regression_result["execution_time"] >= 0
    assert regression_result["response_time"] >= 0
    assert regression_result["timestamp"] is not None

    # STEP 6: Cleanup

    engine.delete_baseline(snapshot_name)

    assert not engine.snapshot_manager.snapshot_exists(
        snapshot_name
    )


def test_regression_is_detected_when_api_response_changes(tmp_path):
    """
    Integration test:
    Capture baseline -> Modify API data -> Detect regression
    """

    engine = RegressionEngine(
        base_url="http://127.0.0.1:5000",
        snapshot_dir=str(tmp_path)
    )

    snapshot_name = "products_endpoint_integration"

    try:

        # STEP 1: RESET API DATA

        reset_result = engine.api_runner.post(
            "/api/products/reset"
        )

        assert reset_result["success"] is True
        assert reset_result["status_code"] == 200

        # STEP 2: CAPTURE BASELINE

        baseline_result = engine.capture_baseline(
            endpoint="/api/products",
            snapshot_name=snapshot_name,
            method="GET"
        )

        assert baseline_result["success"] is True
        assert baseline_result["status"] == "BASELINE_CAPTURED"

        # STEP 3: MODIFY API DATA

        new_product = {
            "name": "Integration Test Product",
            "category": "Testing",
            "price": 9999,
            "stock": 5
        }

        create_result = engine.api_runner.post(
            "/api/products",
            json_data=new_product
        )

        assert create_result["success"] is True
        assert create_result["status_code"] == 201

        # STEP 4: RUN REGRESSION TEST

        regression_result = engine.run_regression_test(
            endpoint="/api/products",
            snapshot_name=snapshot_name,
            method="GET"
        )

        # STEP 5: VERIFY REGRESSION DETECTION

        assert regression_result["success"] is True

        assert regression_result["regression_detected"] is True

        assert regression_result["status"] == "FAILED"

        assert regression_result["comparison"]["match"] is False

        assert regression_result["expected"] != regression_result["actual"]

    finally:

        # STEP 6: CLEANUP

        engine.api_runner.post(
            "/api/products/reset"
        )

        engine.delete_baseline(snapshot_name)

        engine.api_runner.close()
