import time
import requests


class APITestRunner:
    """
    Execute HTTP requests against an API and capture detailed results.

    Features:
    - Supports GET, POST, PUT, PATCH, DELETE, HEAD, and OPTIONS
    - Custom headers and query parameters
    - JSON and form-data payloads
    - Basic authentication
    - Bearer token authentication
    - Configurable timeout
    - SSL verification configuration
    - Response headers, body, status code, and timing
    - Detailed request information
    - Connection and timeout error handling
    - Reusable HTTP session
    """

    def __init__(
        self,
        base_url="http://127.0.0.1:5000",
        timeout=10,
        verify=True
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify = verify

        # Reusable HTTP session
        self.session = requests.Session()

    # --------------------------------------------------
    # REQUEST EXECUTION
    # --------------------------------------------------

    def send_request(
        self,
        method,
        endpoint,
        headers=None,
        params=None,
        json_data=None,
        data=None,
        auth=None,
        bearer_token=None,
        timeout=None,
        verify=None
    ):
        """
        Send an HTTP request to the API and capture the response.

        Parameters:
            method:
                HTTP method.

            endpoint:
                API endpoint.

            headers:
                Custom HTTP headers.

            params:
                Query parameters.

            json_data:
                JSON request payload.

            data:
                Form data or raw request data.

            auth:
                Basic authentication tuple.
                Example: ("username", "password")

            bearer_token:
                Bearer authentication token.

            timeout:
                Request timeout override.

            verify:
                SSL verification override.

        Returns:
            Dictionary containing request and response information.
        """

        method = method.upper()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        request_headers = headers.copy() if headers else {}

        # --------------------------------------------------
        # BEARER TOKEN AUTHENTICATION
        # --------------------------------------------------

        if bearer_token:

            request_headers["Authorization"] = (
                f"Bearer {bearer_token}"
            )

        # --------------------------------------------------
        # REQUEST CONFIGURATION
        # --------------------------------------------------

        request_timeout = (
            timeout if timeout is not None else self.timeout
        )

        request_verify = (
            verify if verify is not None else self.verify
        )

        # --------------------------------------------------
        # REQUEST INFORMATION
        # --------------------------------------------------

        request_information = {
            "method": method,
            "url": url,
            "headers": request_headers,
            "params": params,
            "json": json_data,
            "data": data
        }

        # --------------------------------------------------
        # EXECUTE REQUEST
        # --------------------------------------------------

        start_time = time.perf_counter()

        try:

            response = self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                params=params,
                json=json_data,
                data=data,
                auth=auth,
                timeout=request_timeout,
                verify=request_verify
            )

            elapsed_time = time.perf_counter() - start_time

            # --------------------------------------------------
            # RESPONSE BODY PARSING
            # --------------------------------------------------

            if method == "HEAD":

                response_body = None

            else:

                try:
                    response_body = response.json()

                except ValueError:
                    response_body = response.text

            # --------------------------------------------------
            # SUCCESSFUL REQUEST EXECUTION
            # --------------------------------------------------

            return {
                "success": True,
                "method": method,
                "url": response.url,
                "request": request_information,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "response_body": response_body,
                "response_time": elapsed_time,
                "error": None
            }

        # --------------------------------------------------
        # TIMEOUT ERROR
        # --------------------------------------------------

        except requests.exceptions.Timeout:

            elapsed_time = time.perf_counter() - start_time

            return {
                "success": False,
                "method": method,
                "url": url,
                "request": request_information,
                "status_code": None,
                "headers": {},
                "response_body": None,
                "response_time": elapsed_time,
                "error": "Request timed out",
                "error_type": "TimeoutError"
            }

        # --------------------------------------------------
        # CONNECTION ERROR
        # --------------------------------------------------

        except requests.exceptions.ConnectionError:

            elapsed_time = time.perf_counter() - start_time

            return {
                "success": False,
                "method": method,
                "url": url,
                "request": request_information,
                "status_code": None,
                "headers": {},
                "response_body": None,
                "response_time": elapsed_time,
                "error": "Unable to connect to API",
                "error_type": "ConnectionError"
            }

        # --------------------------------------------------
        # GENERAL REQUEST ERROR
        # --------------------------------------------------

        except requests.exceptions.RequestException as error:

            elapsed_time = time.perf_counter() - start_time

            return {
                "success": False,
                "method": method,
                "url": url,
                "request": request_information,
                "status_code": None,
                "headers": {},
                "response_body": None,
                "response_time": elapsed_time,
                "error": str(error),
                "error_type": type(error).__name__
            }

    # --------------------------------------------------
    # HTTP METHOD HELPERS
    # --------------------------------------------------

    def get(self, endpoint, **kwargs):

        return self.send_request(
            "GET",
            endpoint,
            **kwargs
        )

    def post(self, endpoint, **kwargs):

        return self.send_request(
            "POST",
            endpoint,
            **kwargs
        )

    def put(self, endpoint, **kwargs):

        return self.send_request(
            "PUT",
            endpoint,
            **kwargs
        )

    def patch(self, endpoint, **kwargs):

        return self.send_request(
            "PATCH",
            endpoint,
            **kwargs
        )

    def delete(self, endpoint, **kwargs):

        return self.send_request(
            "DELETE",
            endpoint,
            **kwargs
        )

    def head(self, endpoint, **kwargs):

        return self.send_request(
            "HEAD",
            endpoint,
            **kwargs
        )

    def options(self, endpoint, **kwargs):

        return self.send_request(
            "OPTIONS",
            endpoint,
            **kwargs
        )

    # --------------------------------------------------
    # SESSION MANAGEMENT
    # --------------------------------------------------

    def close(self):
        """
        Close the reusable HTTP session.
        """

        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()