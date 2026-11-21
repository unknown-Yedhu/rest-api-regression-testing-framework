import pytest
from framework.report_generator import ReportGenerator


@pytest.fixture
def generator(tmp_path):
    return ReportGenerator(
        report_dir=str(tmp_path)
    )


def test_generate_report(generator):
    test_results = [
        {"status": "PASSED"},
        {"status": "PASSED"},
        {"status": "FAILED"},
        {"status": "SKIPPED"}
    ]

    report = generator.generate_report(test_results)

    assert report["summary"]["total_tests"] == 4
    assert report["summary"]["passed"] == 2
    assert report["summary"]["failed"] == 1
    assert report["summary"]["skipped"] == 1
    assert report["summary"]["success_rate"] == 50.0
    assert report["summary"]["overall_status"] == "FAILED"


def test_generate_report_all_passed(generator):
    test_results = [
        {"status": "PASSED"},
        {"status": "PASSED"},
        {"status": "PASSED"}
    ]

    report = generator.generate_report(test_results)

    assert report["summary"]["total_tests"] == 3
    assert report["summary"]["passed"] == 3
    assert report["summary"]["failed"] == 0
    assert report["summary"]["success_rate"] == 100.0
    assert report["summary"]["overall_status"] == "PASSED"


def test_generate_empty_report(generator):
    report = generator.generate_report([])

    assert report["summary"]["total_tests"] == 0
    assert report["summary"]["passed"] == 0
    assert report["summary"]["failed"] == 0
    assert report["summary"]["success_rate"] == 0
    assert report["summary"]["overall_status"] == "PASSED"


def test_save_json_report(generator):
    test_results = [
        {"status": "PASSED"},
        {"status": "FAILED"}
    ]

    report = generator.generate_report(test_results)

    report_path = generator.save_json_report(
        report,
        "test_report.json"
    )

    assert report_path.exists()
    assert report_path.name == "test_report.json"


def test_generate_and_save_report(generator):
    test_results = [
        {"status": "PASSED"},
        {"status": "PASSED"}
    ]

    result = generator.generate_and_save_report(
        test_results,
        "final_report.json"
    )

    assert result["success"] is True
    assert result["report"]["summary"]["total_tests"] == 2
    assert result["report"]["summary"]["overall_status"] == "PASSED"
    assert result["report_path"].endswith("final_report.json")