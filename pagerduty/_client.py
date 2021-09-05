import uuid
import aiohttp
from typing import Optional

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

    async def get(self, resource: str):
        """
        Get a resource from PagerDuty's API.

        Returns the JSON-decoded result when the request succeeds.
        """
        headers = {
            "accept": "application/vnd.pagerduty+json;version=2",
            "content-type": "application/json",
            "authorization": f"Token token={self.api_key}",
        }
        try:
            async with self.client.get(
                self.base_url + resource, headers=headers, raise_for_status=True
            ) as response:
                response_data = await response.json()
                return response_data["services"]
        except aiohttp.ClientError as error:
            return PagerDutyClientHTTPError(error)

    async def post(self, resource: str, data, extra_headers=None):
        """
        Post to a resource from PagerDuty's API.

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
            async with self.client.post(
                self.base_url + resource,
                headers=headers,
                raise_for_status=True,
                json=data,
            ) as response:
                response_data = await response.json()
                return response_data
        except aiohttp.ClientError as error:
            return PagerDutyClientHTTPError(error)

    async def get_services(self):
        """
        Get PagerDuty services

        This returns a list of services following the schema documented at
        https://developer.pagerduty.com/api-reference/reference/REST/openapiv3.json/paths/~1services/get
        """
        return await self.get("/services")

    async def create_incident(
        self, service_id: str, from_email: str, title: str, description: Optional[str]
    ):
        """
        Create a new PagerDuty incident.

        The email address of a valid PagerDuty user must be included when making API calls to this endpoint, hence the inclusion of `from_email`.
        """
        return await self.post(
            "/incidents",
            data={
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
