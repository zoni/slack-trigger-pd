import logging
import asyncio

import aiohttp
import pagerduty


class State:
    def __init__(self, http_client: aiohttp.ClientSession, pd_client: pagerduty.Client):
        self.http_client = http_client
        self.pd_client = pd_client
        self._pd_services = None
        self._lock = asyncio.Lock()

    async def get_pagerduty_services(self):
        """
        Get PagerDuty services

        This returns a list of services following the schema documented at
        https://developer.pagerduty.com/api-reference/reference/REST/openapiv3.json/paths/~1services/get

        Results from to this method are stored so that subsequent calls are
        immediately returned from cache.
        """
        logger = logging.getLogger(__class__.__name__)

        logger.debug("Acquiring lock")
        async with self._lock:
            logger.debug("Lock acquired")

            if self._pd_services is not None:
                logger.info("Returning PagerDuty services from cache")
                return self._pd_services

            logger.info("Returning PagerDuty services from API")
            self._pd_services = await self.pd_client.get_services()
            return self._pd_services
