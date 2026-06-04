import requests
import time
from dataclasses import dataclass
from requests.exceptions import ConnectionError, Timeout, RequestException

# ---------------------------
# Data Model
# ---------------------------

@dataclass
class MonitorResult:
    name: str
    url: str
    status: str
    response_time: float
    status_code: int
    http_message: str


# ---------------------------
# HTTP Status Mapping
# ---------------------------

HTTP_STATUS_MAP = {
    200: "OK",
    301: "Redirect",
    302: "Redirect",
    403: "Forbidden",
    404: "Not Found",
    500: "Internal Server Error",
    503: "Service Unavailable",
}


def classify_http_status(code: int) -> str:
    return HTTP_STATUS_MAP.get(code, f"HTTPS {code}")


def classify_response_time(ms: float) -> str:
    thresholds = [
        (1000, "Good"),
        (3000, "Slow"),
    ]

    for limit, label in thresholds:
        if ms < limit:
            return label

    return "Very Slow"


# ---------------------------
# Core Monitor Function (With Retry)
# ---------------------------

def check_website(name: str, url: str) -> MonitorResult:

    max_retries = 2
    retry_delay = 2  # seconds

    for attempt in range(max_retries + 1):

        try:
            start = time.perf_counter()

            response = requests.get(
                url,
                timeout=10,
                allow_redirects=False
            )

            response_time = (time.perf_counter() - start) * 1000

            # If we got a response, no need to retry
            status_label = classify_http_status(response.status_code)

            if response.status_code == 200:
                status_label = classify_response_time(response_time)

            return MonitorResult(
                name=name,
                url=url,
                status=status_label,
                response_time=response_time,
                status_code=response.status_code,
                http_message=response.reason
            )

        except (ConnectionError, Timeout):

            if attempt < max_retries:
                time.sleep(retry_delay)
                continue
            else:
                # All retries failed → Server Down
                return MonitorResult(
                    name=name,
                    url=url,
                    status="Server Down",
                    response_time=None,
                    status_code=None,
                    http_message="No Response After Retries"
                )

        except RequestException:
            return MonitorResult(
                name=name,
                url=url,
                status="Request Failed",
                response_time=None,
                status_code=None,
                http_message="Unknown Error"
            )
        