import pytest
from unittest.mock import Mock

from framework.api_test_runner import APITestRunner


# --------------------------------------------------
# FIXTURE
# --------------------------------------------------

@pytest.fixture
def runner():
    return APITestRunner(
        base_url="http://127.0.0.1:5000"
    )


# --------------------------------------------------
# HTTP METHOD SUPPORT
# --------------------------------------------------

def test_head_request(runner):

    response = runner.head("/api/health")

    assert response["success"] is True
    assert response["method"] == "HEAD"
    assert response["status_code"] == 200
    assert response["response_body"] is None


def test_options_request(runner):

    response = runner.options("/api/health")

    assert response["success"] is True
    assert response["method"] == "OPTIONS"
    assert response["status_code"] in [200, 204]


# --------------------------------------------------
# QUERY PARAMETERS
# --------------------------------------------------

def test_query_parameters(runner):

    response = runner.get(
        "/api/products",
        params={"category": "Testing"}
    )

    assert response["success"] is True

    assert "category=Testing" in response["url"]


# --------------------------------------------------
# REQUEST INFORMATION
# --------------------------------------------------

def test_request_information_is_captured(runner):

    response = runner.get("/api/health")

    assert response["success"] is True

    assert isinstance(response["request"], dict)

    assert response["request"]["method"] == "GET"

    assert (
        response["request"]["url"]
        == "http://127.0.0.1:5000/api/health"
    )


# --------------------------------------------------
# CUSTOM HEADERS
# --------------------------------------------------

def test_custom_headers(runner):

    response = runner.get(
        "/api/health",
        headers={
            "X-Test-Header": "RegressionFramework"
        }
    )

    assert response["success"] is True

    assert (
        response["request"]["headers"]["X-Test-Header"]
        == "RegressionFramework"
    )


# --------------------------------------------------
# BEARER TOKEN
# --------------------------------------------------

def test_bearer_token_header():

    runner = APITestRunner()

    response = runner.send_request(
        method="GET",
        endpoint="/api/health",
        bearer_token="test_token_123"
    )

    assert response["request"]["headers"]["Authorization"] == (
        "Bearer test_token_123"
    )


# --------------------------------------------------
# TIMEOUT CONFIGURATION
# --------------------------------------------------

def test_custom_timeout():

    runner = APITestRunner(
        timeout=20
    )

    assert runner.timeout == 20


def test_request_timeout_override():

    runner = APITestRunner()

    original_request = runner.session.request

    captured_arguments = {}

    def mock_request(**kwargs):

        captured_arguments.update(kwargs)

        return original_request(**kwargs)

    runner.session.request = mock_request

    response = runner.get(
        "/api/health",
        timeout=3
    )

    assert response["success"] is True

    assert captured_arguments["timeout"] == 3


# --------------------------------------------------
# SSL CONFIGURATION
# --------------------------------------------------

def test_ssl_verification_configuration():

    runner = APITestRunner(
        verify=False
    )

    assert runner.verify is False


# --------------------------------------------------
# RESPONSE INFORMATION
# --------------------------------------------------

def test_response_contains_error_type_on_connection_failure():

    runner = APITestRunner(
        base_url="http://127.0.0.1:5999"
    )

    response = runner.get("/api/health")

    assert response["success"] is False

    assert response["error_type"] == "ConnectionError"


# --------------------------------------------------
# SESSION MANAGEMENT
# --------------------------------------------------

def test_session_is_created(runner):

    assert runner.session is not None


def test_session_can_be_closed(runner):

    runner.close()

    assert runner.session is not None


# --------------------------------------------------
# CONTEXT MANAGER
# --------------------------------------------------

def test_runner_context_manager():

    with APITestRunner() as runner:

        response = runner.get("/api/health")

        assert response["success"] is True