import uuid
import aiohttp
from typing import Optional, Any, Dict

from pagerduty.exceptions import *


class Client:
    """Async PagerDuty client"""

    def __init__(
        self,
        http_client: aiohttp.ClientSession,
        api_key: str,
        base_url: str = "https://api.pagerduty.com",
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.client = http_client

    async def request(
        self,
        method: str,
        resource: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        extra_headers: Optional[Dict] = None,
    ):
        """
        Make a request to a resource from PagerDuty's API.

        Returns the API's JSON-decoded response on success.
        """
        headers = {
            "accept": "application/vnd.pagerduty+json;version=2",
            "content-type": "application/json",
            "authorization": f"Token token={self.api_key}",
        }
        if extra_headers is not None:
            headers.update(extra_headers)
        try:
            async with self.client.request(
                method,
                self.base_url + resource,
                headers=headers,
                raise_for_status=False,
                data=data,
                json=json,
            ) as response:
                response_data = await response.json()
                if "error" in response_data:
                    raise PagerDutyClientAPIError(
                        code=response_data["error"]["code"],
                        message=response_data["error"]["message"],
                        errors=response_data["error"]["errors"],
                    )

                # We use raise_for_status=False above because if we raise
                # exceptions automatically, the raised
                # aiohttp.ClientResponseError doesn't allow us to access the
                # response body with error details.
                #
                # This does require this extra check here, which we place after
                # the search for an "error" key because when that is present,
                # we have more information we can return to the caller.
                if not response.ok:
                    raise PagerDutyClientHTTPError(
                        f"HTTP {response.status}: {response.reason}"
                    )

                return response_data
        except aiohttp.ClientResponseError as error:
            raise PagerDutyClientHTTPError(error.message) from error
        except aiohttp.ClientError as error:
            raise PagerDutyClientHTTPError(
                "Failed to make a successful API call"
            ) from error

    async def get_services(self):
        """
        Get PagerDuty services

        This returns a list of services following the schema documented at
        https://developer.pagerduty.com/api-reference/reference/REST/openapiv3.json/paths/~1services/get
        """
        result = await self.request("GET", "/services")
        return result["services"]

    async def create_incident(
        self, service_id: str, from_email: str, title: str, description: Optional[str]
    ):
        """
        Create a new PagerDuty incident.

        The email address of a valid PagerDuty user must be included when making API calls to this endpoint, hence the inclusion of `from_email`.
        """
        return await self.request(
            "POST",
            "/incidents",
            json={
                "incident": {
                    "type": "incident",
                    "title": title,
                    "service": {"id": service_id, "type": "service_reference"},
                    "urgency": "high",
                    "incident_key": uuid.uuid4().hex,
                    "body": {
                        "type": "incident_body",
                        "details": description,
                    },
                }
            },
            extra_headers={"from": from_email},
        )
