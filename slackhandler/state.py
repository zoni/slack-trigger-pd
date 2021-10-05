import logging
import threading
import pdpyras
import slack_sdk.web.client


class State:
    """
    State holds data which is retained across multiple invocations and shared
    between multiple, potentially concurrent, threads of execution.

    It's primary use is to:

        - Hold references to API clients, so that connection pools are
          shared/reused across different threads.
        - Cache the list of PagerDuty services so that repeated trigger
          invocations are sped up. This is especially important because the app
          only has 3 seconds to respond to Slack requests, so if PagerDuty's
          API were to be slow, we might miss this deadline.
    """
    def __init__(
        self,
        pd_client: pdpyras.APISession,
        slack_client: slack_sdk.web.client.WebClient,
    ):
        self.pd_client = pd_client
        self.slack_client = slack_client
        self._pd_services = None
        self._lock = threading.Lock()

    def get_pagerduty_services(self):
        """
        Get PagerDuty services

        This returns a list of services following the schema documented at
        https://developer.pagerduty.com/api-reference/reference/REST/openapiv3.json/paths/~1services/get

        Results from to this method are stored so that subsequent calls are
        immediately returned from cache.
        """
        logger = logging.getLogger(__class__.__name__)

        logger.debug("Acquiring lock")
        with self._lock:
            logger.debug("Lock acquired")

            if self._pd_services is not None:
                logger.info("Returning PagerDuty services from cache")
                return self._pd_services

            logger.info("Returning PagerDuty services from API")
            # iter_all() returns a generator, so the wrapping with list() here
            # ensures we save the result of it into the cache, rather than the
            # generator object itself.
            self._pd_services = list(self.pd_client.iter_all("/services"))
            return self._pd_services
