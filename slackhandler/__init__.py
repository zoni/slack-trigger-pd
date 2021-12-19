import json
import logging
import os

import azure.functions as func
import pdpyras
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.client import WebClient as SlackWebClient

from slackhandler.handlers import (
    handle_block_suggestion,
    handle_incident_trigger,
    handle_view_submission,
)
from slackhandler.state import State

if (SENTRY_DSN := os.environ.get("SENTRY_DSN")) is not None:
    import sentry_sdk
    from sentry_sdk.integrations.serverless import serverless_function

    sentry_sdk.init(SENTRY_DSN)

# Global variables are unfortunately the only way to share state across
# multiple threads of execution.
#
# See also:
# https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=azurecli-linux%2Capplication-level#global-variables
_pd_client = pdpyras.APISession(
    os.environ["PAGERDUTY_API_KEY"], default_from=os.environ["PAGERDUTY_USER_EMAIL"]
)
_slack_client = SlackWebClient(token=os.environ["SLACK_API_TOKEN"])
_state = State(pd_client=_pd_client, slack_client=_slack_client)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure function entrypoint"""
    handler = _handle_request
    if SENTRY_DSN is not None:
        handler = serverless_function(handler)
    return handler(req)


def _handle_request(req: func.HttpRequest) -> func.HttpResponse:
    global _state  # pylint: disable=invalid-name

    signature_verifier = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"])
    if not signature_verifier.is_valid_request(req.get_body(), req.headers):
        # req.headers doesn't have a proper __str__ or __repr__ defined, so
        # trying to print it results in a
        # "<azure.functions._http.HttpRequestHeaders object at 0x7faac2cf0280>"
        # representation without the __dict__ hack.
        logging.warning(
            "Missing or invalid Slack signature on request. Secret=%s, Headers=%s",
            os.environ["SLACK_SIGNING_SECRET"],
            req.headers.__dict__["__http_headers__"],
        )
        return func.HttpResponse(
            "Unauthorized: missing or invalid Slack signature",
            status_code=403,
        )

    command = req.form.get("command")
    if command == "/incident":
        return handle_incident_trigger(_state, req)

    try:
        payload = json.loads(req.form.get("payload"))
    except TypeError:
        return func.HttpResponse(
            "Error: request payload not supported",
            status_code=400,
        )

    if payload.get("type") == "block_suggestion":
        return handle_block_suggestion(_state, req)
    if payload.get("type") == "view_submission":
        return handle_view_submission(_state, req, payload)

    return func.HttpResponse(
        "Error: request payload not supported",
        status_code=400,
    )
