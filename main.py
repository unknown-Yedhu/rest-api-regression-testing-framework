import argparse
import json
import sys
from pathlib import Path

from framework.config_manager import ConfigManager
from framework.test_suite import RegressionTestSuite
from framework.regression_engine import RegressionEngine


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

DEFAULT_CONFIG = "config.json"


def load_configuration(config_path):
    """
    Load and validate the framework configuration.
    """

    try:
        config_manager = ConfigManager(config_path)
        return config_manager

    except Exception as error:
        print(f"\n[ERROR] Configuration error: {error}")
        sys.exit(1)


# --------------------------------------------------
# RUN REGRESSION TESTS
# --------------------------------------------------

def run_tests(config_path):
    """
    Load configured tests, execute them,
    and generate a regression report.
    """

    print("\n" + "=" * 60)
    print("REST API REGRESSION TESTING FRAMEWORK")
    print("=" * 60)

    suite = RegressionTestSuite(
        config_path=config_path
    )

    suite.load_tests_from_config()

    print(f"\nLoaded {len(suite.tests)} configured tests.")

    print("\nStarting regression testing...\n")

    results = suite.run_all()

    for result in results:

        test_name = result.get(
            "test_name",
            "Unnamed Test"
        )

        status = result.get(
            "status",
            "UNKNOWN"
        )

        print(f"[{status}] {test_name}")

        if result.get("regression_detected"):

            print("    Regression detected!")

            differences = result.get(
                "comparison",
                {}
            ).get(
                "differences",
                []
            )

            for difference in differences:

                print(
                    f"    - {difference.get('path')}: "
                    f"{difference.get('type')}"
                )

        elif result.get("success") is False:

            print(
                f"    Error: {result.get('error')}"
            )

    print("\n" + "-" * 60)

    report_result = suite.save_report()

    report = report_result["report"]

    summary = report["summary"]

    print("\nTEST SUMMARY")
    print("-" * 60)

    print(f"Total Tests  : {summary['total_tests']}")
    print(f"Passed       : {summary['passed']}")
    print(f"Failed       : {summary['failed']}")
    print(f"Skipped      : {summary['skipped']}")
    print(f"Success Rate : {summary['success_rate']}%")
    print(f"Overall      : {summary['overall_status']}")

    print("\nReport saved:")
    print(report_result["report_path"])

    print("\n" + "=" * 60)

    if summary["failed"] > 0:
        return 1

    return 0


# --------------------------------------------------
# CAPTURE BASELINES
# --------------------------------------------------

def capture_baselines(config_path):
    """
    Capture baseline snapshots for enabled tests.
    """

    config_manager = load_configuration(
        config_path
    )

    config = config_manager.get_config()

    api_config = config_manager.get_api_config()

    directory_config = config_manager.get_directory_config()

    engine = RegressionEngine(
        base_url=api_config["base_url"],
        snapshot_dir=directory_config["snapshots"]
    )

    enabled_tests = config_manager.get_enabled_tests()

    print("\n" + "=" * 60)
    print("BASELINE SNAPSHOT CAPTURE")
    print("=" * 60)

    successful = 0
    failed = 0

    for test in enabled_tests:

        print(
            f"\nCapturing: {test['name']}"
        )

        result = engine.capture_baseline(
            endpoint=test["endpoint"],
            snapshot_name=test["snapshot"],
            method=test["method"]
        )

        if result["success"]:

            successful += 1

            print("[SUCCESS] Baseline captured")

            print(
                f"Snapshot: {result['snapshot_name']}"
            )

        else:

            failed += 1

            print("[FAILED] Baseline capture failed")

            print(
                f"Error: {result.get('error')}"
            )

    print("\n" + "-" * 60)

    print(f"Successful captures: {successful}")
    print(f"Failed captures    : {failed}")

    print("=" * 60)

    return 1 if failed > 0 else 0


# --------------------------------------------------
# UPDATE BASELINES
# --------------------------------------------------

def update_baselines(config_path):
    """
    Update existing baseline snapshots
    using the latest API responses.
    """

    config_manager = load_configuration(
        config_path
    )

    api_config = config_manager.get_api_config()

    directory_config = config_manager.get_directory_config()

    engine = RegressionEngine(
        base_url=api_config["base_url"],
        snapshot_dir=directory_config["snapshots"]
    )

    enabled_tests = config_manager.get_enabled_tests()

    print("\n" + "=" * 60)
    print("UPDATE BASELINE SNAPSHOTS")
    print("=" * 60)

    successful = 0
    failed = 0

    for test in enabled_tests:

        print(
            f"\nUpdating: {test['name']}"
        )

        result = engine.update_baseline(
            endpoint=test["endpoint"],
            snapshot_name=test["snapshot"],
            method=test["method"]
        )

        if result["success"]:

            successful += 1

            print("[SUCCESS] Baseline updated")

        else:

            failed += 1

            print("[FAILED] Baseline update failed")

            print(
                f"Error: {result.get('error')}"
            )

    print("\n" + "-" * 60)

    print(f"Successful updates: {successful}")
    print(f"Failed updates    : {failed}")

    print("=" * 60)

    return 1 if failed > 0 else 0


# --------------------------------------------------
# DISPLAY REPORT
# --------------------------------------------------

def display_report(config_path):
    """
    Display the latest saved regression report.
    """

    config_manager = load_configuration(
        config_path
    )

    directory_config = config_manager.get_directory_config()

    report_path = (
        Path(directory_config["reports"])
        / "regression_report.json"
    )

    if not report_path.exists():

        print("\n[ERROR] No regression report found.")

        print(
            "Run 'python main.py run' first."
        )

        return 1

    try:

        with open(
            report_path,
            "r",
            encoding="utf-8"
        ) as file:

            report = json.load(file)

    except Exception as error:

        print(
            f"\n[ERROR] Unable to read report: {error}"
        )

        return 1

    summary = report.get(
        "summary",
        {}
    )

    print("\n" + "=" * 60)
    print("REGRESSION TEST REPORT")
    print("=" * 60)

    print(
        f"Report Name : {report.get('report_name')}"
    )

    print(
        f"Generated   : {report.get('generated_at')}"
    )

    print("\nSUMMARY")
    print("-" * 60)

    print(
        f"Total Tests  : {summary.get('total_tests', 0)}"
    )

    print(
        f"Passed       : {summary.get('passed', 0)}"
    )

    print(
        f"Failed       : {summary.get('failed', 0)}"
    )

    print(
        f"Skipped      : {summary.get('skipped', 0)}"
    )

    print(
        f"Success Rate : {summary.get('success_rate', 0)}%"
    )

    print(
        f"Overall      : {summary.get('overall_status', 'UNKNOWN')}"
    )

    print("\nTEST RESULTS")
    print("-" * 60)

    for result in report.get(
        "test_results",
        []
    ):

        print(
            f"[{result.get('status', 'UNKNOWN')}] "
            f"{result.get('test_name', 'Unnamed Test')}"
        )

    print("\nFull report location:")
    print(report_path)

    print("=" * 60)

    return 0


# --------------------------------------------------
# CLI ARGUMENTS
# --------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description=(
            "REST API Regression Testing Framework "
            "with Snapshot Testing"
        )
    )

    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help="Path to configuration file"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands"
    )

    # Run command
    subparsers.add_parser(
        "run",
        help="Execute regression tests"
    )

    # Capture command
    subparsers.add_parser(
        "capture",
        help="Capture baseline snapshots"
    )

    # Update baselines command
    subparsers.add_parser(
        "update-baselines",
        help="Update existing baseline snapshots"
    )

    # Report command
    subparsers.add_parser(
        "report",
        help="Display the latest regression report"
    )

    args = parser.parse_args()

    if args.command == "run":

        exit_code = run_tests(
            args.config
        )

    elif args.command == "capture":

        exit_code = capture_baselines(
            args.config
        )

    elif args.command == "update-baselines":

        exit_code = update_baselines(
            args.config
        )

    elif args.command == "report":

        exit_code = display_report(
            args.config
        )

    else:

        parser.print_help()

        exit_code = 0

    sys.exit(exit_code)


# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()