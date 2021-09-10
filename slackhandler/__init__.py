import json
import logging
import os
from pprint import pprint

import asyncio
import aiohttp
import azure.functions as func

import pagerduty
from slackhandler.handlers import (
    handle_incident_trigger,
    handle_block_suggestion,
    handle_view_submission,
)
from slackhandler.state import State

if (SENTRY_DSN := os.environ.get("SENTRY_DSN")) is not None:
    import sentry_sdk
    from sentry_sdk import capture_exception

    sentry_sdk.init(SENTRY_DSN)

# The Azure Functions runtime doesn't give us any way to initialize objects
# outside of the asyncio loop, other than using a module-level global like
# this. Slightly hacky, but works well.
_http_client = aiohttp.ClientSession()
_pd_client = pagerduty.Client(
    http_client=_http_client, api_key=os.environ["PAGERDUTY_API_KEY"]
)
_state = State(http_client=_http_client, pd_client=_pd_client)


async def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure function entrypoint"""
    try:
        command = req.form.get("command")
        if command == "/incident":
            return await handle_incident_trigger(_state, req)

        payload = json.loads(req.form.get("payload"))
        if payload.get("type") == "block_suggestion":
            return await handle_block_suggestion(_state, req)
        if payload.get("type") == "view_submission":
            return await handle_view_submission(_state, req, payload)

        # logging.info("Request form: %s", pprint(req.form.to_dict()))
        return func.HttpResponse(
            "Error: request payload not supported",
            status_code=400,
        )
    except Exception as exc:
        # Current Sentry SDK does not support async Azure Functions, the
        # @serverless_function decorator only supports regular functions.
        #
        # We work around this by manually invoking the capture_exception()
        # method of Sentry's SDK, which we schedule on the default
        # TheadPoolExecutor as Sentry's SDK may be blocking (it's non-async).
        #
        # This works fine, except for missing out one some automatically
        # discovered context/metadata.
        if SENTRY_DSN is not None:
            loop = asyncio.get_running_loop()
            asyncio.shield(loop.run_in_executor(None, capture_exception, exc))
        raise
