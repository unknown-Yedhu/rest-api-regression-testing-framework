
import time
from datetime import datetime, timezone

from framework.api_test_runner import APITestRunner
from framework.snapshot_manager import SnapshotManager
from framework.response_comparator import ResponseComparator


class RegressionEngine:
    """
    Core regression testing engine.

    Features:
    - Baseline capture
    - Baseline comparison
    - Regression detection
    - Baseline updating
    - Execution timing
    - Detailed test metadata
    - Error handling
    - Configurable ignored comparison paths
    """

    def __init__(
        self,
        base_url="http://127.0.0.1:5000",
        snapshot_dir="snapshots"
    ):
        self.api_runner = APITestRunner(
            base_url=base_url
        )

        self.snapshot_manager = SnapshotManager(
            snapshot_dir=snapshot_dir
        )

        self.comparator = ResponseComparator()

    # --------------------------------------------------
    # TIMESTAMP
    # --------------------------------------------------

    def _get_timestamp(self):
        """
        Return the current UTC timestamp.
        """

        return datetime.now(
            timezone.utc
        ).isoformat()

    # --------------------------------------------------
    # CAPTURE BASELINE
    # --------------------------------------------------

    def capture_baseline(
        self,
        endpoint,
        snapshot_name,
        method="GET",
        **request_kwargs
    ):
        """
        Capture the current API response and save it
        as a baseline snapshot.
        """

        start_time = time.perf_counter()

        timestamp = self._get_timestamp()

        method = method.upper()

        # --------------------------------------------------
        # EXECUTE API REQUEST
        # --------------------------------------------------

        response = self.api_runner.send_request(
            method=method,
            endpoint=endpoint,
            **request_kwargs
        )

        execution_time = (
            time.perf_counter() - start_time
        )

        # --------------------------------------------------
        # HANDLE REQUEST FAILURE
        # --------------------------------------------------

        if not response["success"]:

            return {
                "success": False,
                "status": "FAILED",
                "message": "Failed to capture baseline.",
                "snapshot_name": snapshot_name,
                "endpoint": endpoint,
                "method": method,
                "error": response.get("error"),
                "error_type": response.get("error_type"),
                "response_time": response.get(
                    "response_time"
                ),
                "execution_time": execution_time,
                "timestamp": timestamp
            }

        # --------------------------------------------------
        # PREPARE SNAPSHOT
        # --------------------------------------------------

        snapshot_data = {
            "status_code": response["status_code"],
            "response_body": response["response_body"]
        }

        # --------------------------------------------------
        # SAVE SNAPSHOT
        # --------------------------------------------------

        try:

            snapshot_path = (
                self.snapshot_manager.save_snapshot(
                    snapshot_name,
                    snapshot_data,
                    metadata={
                        "endpoint": endpoint,
                        "method": method,
                        "status_code": response["status_code"],
                        "captured_at": timestamp
                    }
                )
            )

        except Exception as error:

            return {
                "success": False,
                "status": "FAILED",
                "message": "Unable to save baseline snapshot.",
                "snapshot_name": snapshot_name,
                "endpoint": endpoint,
                "method": method,
                "error": str(error),
                "error_type": type(error).__name__,
                "response_time": response.get(
                    "response_time"
                ),
                "execution_time": execution_time,
                "timestamp": timestamp
            }

        # --------------------------------------------------
        # SUCCESS RESULT
        # --------------------------------------------------

        return {
            "success": True,
            "status": "BASELINE_CAPTURED",
            "message": "Baseline snapshot captured successfully.",
            "snapshot_name": snapshot_name,
            "snapshot_path": str(snapshot_path),
            "endpoint": endpoint,
            "method": method,
            "status_code": response["status_code"],
            "response_body": response["response_body"],
            "response_time": response.get(
                "response_time"
            ),
            "execution_time": execution_time,
            "timestamp": timestamp
        }

    # --------------------------------------------------
    # RUN REGRESSION TEST
    # --------------------------------------------------

    def run_regression_test(
        self,
        endpoint,
        snapshot_name,
        method="GET",
        ignore_paths=None,
        **request_kwargs
    ):
        """
        Execute an API request and compare it
        against a saved baseline.

        Optional ignore_paths allows dynamic response
        fields to be excluded from comparison.
        """

        start_time = time.perf_counter()

        timestamp = self._get_timestamp()

        method = method.upper()

        # --------------------------------------------------
        # CHECK BASELINE EXISTENCE
        # --------------------------------------------------

        if not self.snapshot_manager.snapshot_exists(
            snapshot_name
        ):

            execution_time = (
                time.perf_counter() - start_time
            )

            return {
                "success": False,
                "regression_detected": None,
                "status": "ERROR",
                "message": "Baseline snapshot does not exist.",
                "snapshot_name": snapshot_name,
                "endpoint": endpoint,
                "method": method,
                "error": (
                    f"Snapshot '{snapshot_name}' not found."
                ),
                "execution_time": execution_time,
                "timestamp": timestamp
            }

        # --------------------------------------------------
        # LOAD BASELINE
        # --------------------------------------------------

        try:

            expected_snapshot = (
                self.snapshot_manager.load_snapshot(
                    snapshot_name
                )
            )

        except Exception as error:

            execution_time = (
                time.perf_counter() - start_time
            )

            return {
                "success": False,
                "regression_detected": None,
                "status": "ERROR",
                "message": "Unable to load baseline snapshot.",
                "snapshot_name": snapshot_name,
                "endpoint": endpoint,
                "method": method,
                "error": str(error),
                "error_type": type(error).__name__,
                "execution_time": execution_time,
                "timestamp": timestamp
            }

        # --------------------------------------------------
        # EXECUTE CURRENT API REQUEST
        # --------------------------------------------------

        actual_response = self.api_runner.send_request(
            method=method,
            endpoint=endpoint,
            **request_kwargs
        )

        # --------------------------------------------------
        # HANDLE API REQUEST FAILURE
        # --------------------------------------------------

        if not actual_response["success"]:

            execution_time = (
                time.perf_counter() - start_time
            )

            return {
                "success": False,
                "regression_detected": True,
                "status": "FAILED",
                "message": "API request failed.",
                "snapshot_name": snapshot_name,
                "endpoint": endpoint,
                "method": method,
                "error": actual_response.get(
                    "error"
                ),
                "error_type": actual_response.get(
                    "error_type"
                ),
                "actual_response": actual_response,
                "execution_time": execution_time,
                "timestamp": timestamp
            }

        # --------------------------------------------------
        # PREPARE CURRENT RESPONSE
        # --------------------------------------------------

        actual_snapshot = {
            "status_code": actual_response["status_code"],
            "response_body": actual_response["response_body"]
        }

        # --------------------------------------------------
        # COMPARE RESPONSES
        # --------------------------------------------------

        comparator = ResponseComparator(
            ignore_paths=ignore_paths or []
        )

        comparison_result = comparator.compare(
            expected_snapshot,
            actual_snapshot
        )

        regression_detected = (
            not comparison_result["match"]
        )

        execution_time = (
            time.perf_counter() - start_time
        )

        # --------------------------------------------------
        # DETERMINE STATUS
        # --------------------------------------------------

        status = (
            "FAILED"
            if regression_detected
            else "PASSED"
        )

        message = (
            "Regression detected!"
            if regression_detected
            else "No regression detected."
        )

        # --------------------------------------------------
        # RESULT
        # --------------------------------------------------

        return {
            "success": True,
            "regression_detected": regression_detected,
            "status": status,
            "message": message,
            "snapshot_name": snapshot_name,
            "endpoint": endpoint,
            "method": method,
            "expected": expected_snapshot,
            "actual": actual_snapshot,
            "comparison": comparison_result,
            "ignored_paths": ignore_paths or [],
            "response_time": actual_response.get(
                "response_time"
            ),
            "execution_time": execution_time,
            "timestamp": timestamp
        }

    # --------------------------------------------------
    # UPDATE BASELINE
    # --------------------------------------------------

    def update_baseline(
        self,
        endpoint,
        snapshot_name,
        method="GET",
        **request_kwargs
    ):
        """
        Update an existing baseline snapshot
        using the latest API response.
        """

        result = self.capture_baseline(
            endpoint=endpoint,
            snapshot_name=snapshot_name,
            method=method,
            **request_kwargs
        )

        if result["success"]:

            result["status"] = "BASELINE_UPDATED"

            result["message"] = (
                "Baseline snapshot updated successfully."
            )

        return result

    # --------------------------------------------------
    # SNAPSHOT INFORMATION
    # --------------------------------------------------

    def list_baselines(self):
        """
        Return all available baseline snapshots.
        """

        return self.snapshot_manager.list_snapshots()

    # --------------------------------------------------
    # DELETE BASELINE
    # --------------------------------------------------

    def delete_baseline(self, snapshot_name):
        """
        Delete a baseline snapshot.
        """

        return self.snapshot_manager.delete_snapshot(
            snapshot_name
        )
