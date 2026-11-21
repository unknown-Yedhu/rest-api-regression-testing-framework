
import json
from datetime import datetime
from pathlib import Path
from html import escape


class ReportGenerator:

    def __init__(self, report_dir="reports"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, test_results):
        """
        Generate a structured regression testing report
        with performance metrics.
        """

        total_tests = len(test_results)

        passed_tests = sum(
            1 for result in test_results
            if result.get("status") == "PASSED"
        )

        failed_tests = sum(
            1 for result in test_results
            if result.get("status") == "FAILED"
        )

        skipped_tests = sum(
            1 for result in test_results
            if result.get("status") == "SKIPPED"
        )

        overall_status = (
            "PASSED"
            if failed_tests == 0
            else "FAILED"
        )

        # Collect response times
        performance_data = []

        for result in test_results:

            response_time = result.get("response_time")

            if response_time is not None:

                performance_data.append({
                    "test_name": result.get(
                        "test_name",
                        "Unnamed Test"
                    ),
                    "endpoint": result.get(
                        "endpoint",
                        "Unknown Endpoint"
                    ),
                    "method": result.get(
                        "method",
                        "GET"
                    ),
                    "response_time_ms": round(
                        response_time * 1000,
                        2
                    )
                })

        response_times = [
            item["response_time_ms"]
            for item in performance_data
        ]

        average_response_time = (
            round(
                sum(response_times) / len(response_times),
                2
            )
            if response_times
            else 0
        )

        fastest_request = (
            min(
                performance_data,
                key=lambda item: item["response_time_ms"]
            )
            if performance_data
            else None
        )

        slowest_request = (
            max(
                performance_data,
                key=lambda item: item["response_time_ms"]
            )
            if performance_data
            else None
        )

        performance_summary = {
            "requests_measured": len(performance_data),
            "average_response_time_ms": average_response_time,
            "fastest_request": fastest_request,
            "slowest_request": slowest_request,
            "request_details": performance_data
        }

        report = {
            "report_name": "REST API Regression Testing Report",
            "generated_at": datetime.now().isoformat(),

            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": (
                    round(
                        (passed_tests / total_tests) * 100,
                        2
                    )
                    if total_tests > 0
                    else 0
                ),
                "overall_status": overall_status
            },

            "performance": performance_summary,

            "test_results": test_results
        }

        return report

    def save_json_report(
        self,
        report,
        filename="regression_report.json"
    ):
        """
        Save the generated report as JSON.
        """

        report_path = self.report_dir / filename

        with open(
            report_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4
            )

        return report_path

    def generate_html_report(self, report):
        """
        Generate a professional HTML report
        containing regression and performance results.
        """

        summary = report["summary"]

        performance = report.get(
            "performance",
            {}
        )

        status = summary["overall_status"]

        status_class = (
            "passed"
            if status == "PASSED"
            else "failed"
        )

        # Generate test execution rows
        test_rows = ""

        for result in report["test_results"]:

            test_status = result.get(
                "status",
                "UNKNOWN"
            )

            status_class_for_test = (
                "passed"
                if test_status == "PASSED"
                else "failed"
                if test_status == "FAILED"
                else "skipped"
            )

            response_time = result.get(
                "response_time"
            )

            response_time_display = (
                f"{response_time * 1000:.2f} ms"
                if response_time is not None
                else "N/A"
            )

            differences_html = ""

            comparison = result.get(
                "comparison",
                {}
            )

            differences = comparison.get(
                "differences",
                []
            )

            if differences:

                differences_html = "<div class='differences'>"

                for difference in differences:

                    differences_html += f"""
                    <div class="difference-item">

                        <strong>Type:</strong>
                        {escape(str(
                            difference.get(
                                'type',
                                'Unknown'
                            )
                        ))}

                        <br>

                        <strong>Path:</strong>
                        {escape(str(
                            difference.get(
                                'path',
                                'Unknown'
                            )
                        ))}

                        <br>

                        <strong>Expected:</strong>
                        {escape(str(
                            difference.get(
                                'expected'
                            )
                        ))}

                        <br>

                        <strong>Actual:</strong>
                        {escape(str(
                            difference.get(
                                'actual'
                            )
                        ))}

                    </div>
                    """

                differences_html += "</div>"

            test_rows += f"""
            <tr>

                <td>
                    {escape(str(
                        result.get(
                            'test_name',
                            'Unnamed Test'
                        )
                    ))}
                </td>

                <td>
                    {escape(str(
                        result.get(
                            'method',
                            'N/A'
                        )
                    ))}
                </td>

                <td>
                    {escape(str(
                        result.get(
                            'endpoint',
                            'N/A'
                        )
                    ))}
                </td>

                <td>
                    <span class="badge {status_class_for_test}">
                        {escape(test_status)}
                    </span>
                </td>

                <td>
                    {response_time_display}
                </td>

                <td>
                    {differences_html}
                </td>

            </tr>
            """

        # Generate performance rows
        performance_rows = ""

        request_details = performance.get(
            "request_details",
            []
        )

        for request in request_details:

            performance_rows += f"""
            <tr>

                <td>
                    {escape(str(
                        request.get(
                            'test_name',
                            'Unknown Test'
                        )
                    ))}
                </td>

                <td>
                    {escape(str(
                        request.get(
                            'method',
                            'GET'
                        )
                    ))}
                </td>

                <td>
                    {escape(str(
                        request.get(
                            'endpoint',
                            'Unknown Endpoint'
                        )
                    ))}
                </td>

                <td>
                    <strong>
                        {request.get(
                            'response_time_ms',
                            0
                        ):.2f} ms
                    </strong>
                </td>

            </tr>
            """

        fastest = performance.get(
            "fastest_request"
        )

        slowest = performance.get(
            "slowest_request"
        )

        fastest_display = (
            f"{fastest['response_time_ms']:.2f} ms"
            if fastest
            else "N/A"
        )

        slowest_display = (
            f"{slowest['response_time_ms']:.2f} ms"
            if slowest
            else "N/A"
        )

        fastest_endpoint = (
            escape(str(fastest["endpoint"]))
            if fastest
            else "N/A"
        )

        slowest_endpoint = (
            escape(str(slowest["endpoint"]))
            if slowest
            else "N/A"
        )

        average_response_time = performance.get(
            "average_response_time_ms",
            0
        )

        generated_at = escape(
            str(
                report.get(
                    "generated_at",
                    "Unknown"
                )
            )
        )

        html_content = f"""
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>REST API Regression Testing Report</title>

    <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: #f4f7fb;
            color: #1f2937;
        }}

        .container {{
            max-width: 1300px;
            margin: auto;
            padding: 30px;
        }}

        .header {{
            background: #172554;
            color: white;
            padding: 35px;
            border-radius: 12px;
            margin-bottom: 25px;
        }}

        .header h1 {{
            margin: 0 0 10px;
            font-size: 28px;
        }}

        .header p {{
            margin: 5px 0;
            color: #cbd5e1;
        }}

        .overall-status {{
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
        }}

        .overall-status.passed {{
            background: #dcfce7;
            color: #166534;
        }}

        .overall-status.failed {{
            background: #fee2e2;
            color: #991b1b;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(
                auto-fit,
                minmax(180px, 1fr)
            );
            gap: 20px;
            margin-bottom: 25px;
        }}

        .card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(
                0,
                0,
                0,
                0.05
            );
        }}

        .card h3 {{
            margin: 0 0 10px;
            color: #64748b;
            font-size: 14px;
        }}

        .card .number {{
            font-size: 32px;
            font-weight: bold;
        }}

        .passed-number {{
            color: #16a34a;
        }}

        .failed-number {{
            color: #dc2626;
        }}

        .success-number {{
            color: #2563eb;
        }}

        .performance-number {{
            color: #7c3aed;
        }}

        .section {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(
                0,
                0,
                0,
                0.05
            );
        }}

        .section h2 {{
            margin-top: 0;
            margin-bottom: 20px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th,
        td {{
            text-align: left;
            padding: 15px;
            border-bottom: 1px solid #e5e7eb;
            vertical-align: top;
        }}

        th {{
            background: #f8fafc;
            color: #475569;
        }}

        .badge {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }}

        .badge.passed {{
            background: #dcfce7;
            color: #166534;
        }}

        .badge.failed {{
            background: #fee2e2;
            color: #991b1b;
        }}

        .badge.skipped {{
            background: #fef3c7;
            color: #92400e;
        }}

        .difference-item {{
            background: #fff1f2;
            border-left: 4px solid #dc2626;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 5px;
            font-size: 13px;
            line-height: 1.7;
            word-break: break-word;
        }}

        .differences {{
            min-width: 250px;
        }}

        .performance-highlight {{
            background: #f5f3ff;
            border-left: 4px solid #7c3aed;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}

        .performance-highlight h3 {{
            margin-top: 0;
            color: #6d28d9;
        }}

        .footer {{
            text-align: center;
            padding: 20px;
            color: #64748b;
            font-size: 13px;
        }}

        @media screen and (max-width: 768px) {{

            .container {{
                padding: 15px;
            }}

            .header {{
                padding: 25px;
            }}

            table {{
                display: block;
                overflow-x: auto;
            }}

        }}

    </style>

</head>

<body>

<div class="container">

    <div class="header">

        <h1>REST API Regression Testing Report</h1>

        <p>Automated API Testing & Snapshot Comparison</p>

        <p>Generated: {generated_at}</p>

        <span class="overall-status {status_class}">
            OVERALL STATUS: {escape(status)}
        </span>

    </div>

    <div class="summary-grid">

        <div class="card">

            <h3>Total Tests</h3>

            <div class="number">
                {summary['total_tests']}
            </div>

        </div>

        <div class="card">

            <h3>Passed Tests</h3>

            <div class="number passed-number">
                {summary['passed']}
            </div>

        </div>

        <div class="card">

            <h3>Failed Tests</h3>

            <div class="number failed-number">
                {summary['failed']}
            </div>

        </div>

        <div class="card">

            <h3>Success Rate</h3>

            <div class="number success-number">
                {summary['success_rate']}%
            </div>

        </div>

    </div>

    <div class="section">

        <h2>Performance Summary</h2>

        <div class="summary-grid">

            <div class="card">

                <h3>Average Response Time</h3>

                <div class="number performance-number">
                    {average_response_time:.2f} ms
                </div>

            </div>

            <div class="card">

                <h3>Fastest Request</h3>

                <div class="number passed-number">
                    {fastest_display}
                </div>

                <p>{fastest_endpoint}</p>

            </div>

            <div class="card">

                <h3>Slowest Request</h3>

                <div class="number failed-number">
                    {slowest_display}
                </div>

                <p>{slowest_endpoint}</p>

            </div>

            <div class="card">

                <h3>Requests Measured</h3>

                <div class="number">
                    {performance.get(
                        'requests_measured',
                        0
                    )}
                </div>

            </div>

        </div>

    </div>

    <div class="section">

        <h2>Individual API Performance</h2>

        <table>

            <thead>

                <tr>
                    <th>Test Name</th>
                    <th>Method</th>
                    <th>Endpoint</th>
                    <th>Response Time</th>
                </tr>

            </thead>

            <tbody>

                {performance_rows}

            </tbody>

        </table>

    </div>

    <div class="section">

        <h2>Test Execution Details</h2>

        <table>

            <thead>

                <tr>
                    <th>Test Name</th>
                    <th>Method</th>
                    <th>Endpoint</th>
                    <th>Status</th>
                    <th>Response Time</th>
                    <th>Differences</th>
                </tr>

            </thead>

            <tbody>

                {test_rows}

            </tbody>

        </table>

    </div>

    <div class="footer">

        REST API Regression Testing Framework

        <br>

        Automated report generated by the framework.

    </div>

</div>

</body>

</html>
"""

        return html_content

    def save_html_report(
        self,
        report,
        filename="regression_report.html"
    ):
        """
        Save the HTML report to disk.
        """

        html_content = self.generate_html_report(
            report
        )

        report_path = self.report_dir / filename

        with open(
            report_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(html_content)

        return report_path

    def generate_and_save_report(
        self,
        test_results,
        filename="regression_report.json"
    ):
        """
        Generate and save both JSON and HTML reports.
        """

        report = self.generate_report(
            test_results
        )

        json_report_path = self.save_json_report(
            report,
            filename
        )

        html_filename = (
            Path(filename)
            .with_suffix(".html")
            .name
        )

        html_report_path = self.save_html_report(
            report,
            html_filename
        )

        return {
            "success": True,
            "report": report,
            "report_path": str(
                json_report_path
            ),
            "html_report_path": str(
                html_report_path
            )
        }
