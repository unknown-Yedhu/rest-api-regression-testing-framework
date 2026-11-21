
from framework.regression_engine import RegressionEngine
from framework.report_generator import ReportGenerator
from framework.config_manager import ConfigManager


class RegressionTestSuite:

    def __init__(
        self,
        base_url="http://127.0.0.1:5000",
        snapshot_dir="snapshots",
        report_dir="reports",
        config_path=None
    ):

        self.config_manager = None

        # Load configuration if a config file is provided
        if config_path:

            self.config_manager = ConfigManager(config_path)

            api_config = self.config_manager.get_api_config()
            directory_config = self.config_manager.get_directory_config()

            base_url = api_config["base_url"]
            snapshot_dir = directory_config["snapshots"]
            report_dir = directory_config["reports"]

        self.regression_engine = RegressionEngine(
            base_url=base_url,
            snapshot_dir=snapshot_dir
        )

        self.report_generator = ReportGenerator(
            report_dir=report_dir
        )

        self.tests = []
        self.results = []

    def add_test(
        self,
        test_name,
        endpoint,
        snapshot_name,
        method="GET",
        ignore_paths=None,
        **request_kwargs
    ):
        """
        Add a regression test to the test suite.
        """

        test_case = {
            "test_name": test_name,
            "endpoint": endpoint,
            "snapshot_name": snapshot_name,
            "method": method.upper(),
            "ignore_paths": ignore_paths or [],
            "request_kwargs": request_kwargs
        }

        self.tests.append(test_case)

        return test_case

    def load_tests_from_config(self):
        """
        Load enabled test cases from config.json.
        """

        if self.config_manager is None:
            raise ValueError(
                "Configuration file has not been loaded."
            )

        configured_tests = self.config_manager.get_enabled_tests()

        self.tests.clear()

        for test in configured_tests:

            self.add_test(
                test_name=test["name"],
                endpoint=test["endpoint"],
                snapshot_name=test["snapshot"],
                method=test["method"],
                ignore_paths=test.get("ignore_paths", [])
            )

        return self.tests

    def run_test(self, test_case):
        """
        Execute a single regression test.
        """

        result = self.regression_engine.run_regression_test(
            endpoint=test_case["endpoint"],
            snapshot_name=test_case["snapshot_name"],
            method=test_case["method"],
            ignore_paths=test_case.get("ignore_paths", []),
            **test_case["request_kwargs"]
        )

        result["test_name"] = test_case["test_name"]

        if result.get("success") is False:
            result["status"] = "FAILED"

        return result

    def run_all(self):
        """
        Execute all registered test cases.
        """

        self.results = []

        for test_case in self.tests:

            result = self.run_test(test_case)

            self.results.append(result)

        return self.results

    def generate_report(self):
        """
        Generate a regression testing report.
        """

        return self.report_generator.generate_report(
            self.results
        )

    def save_report(self, filename="regression_report.json"):
        """
        Generate and save the regression report.
        """

        return self.report_generator.generate_and_save_report(
            self.results,
            filename=filename
        )

    def run_and_report(self, filename="regression_report.json"):
        """
        Run the complete test suite and generate a report.
        """

        self.run_all()

        return self.save_report()

    def clear_tests(self):
        """
        Remove all registered test cases and results.
        """

        self.tests.clear()
        self.results.clear()
