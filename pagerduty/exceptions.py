from typing import List


class PagerdutyClientError(Exception):
    """Base class for PagerDuty API exceptions"""


class PagerDutyClientHTTPError(PagerdutyClientError):
    """
    Returned when a request to the PagerDuty API fails in the underlying
    HTTP connection.
    """


class PagerDutyClientAPIError(PagerdutyClientError):
    """Returned when a request to the PagerDuty API is successfully
    established, but the API itself returns an error code"""

    def __init__(self, code: int, message: str, errors: List[str]):
        self.code = code
        self.errors = errors
        super().__init__(f"{message}: {errors}")
