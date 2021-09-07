import asyncio
import json
import logging
import os
import azure.functions as func

from slack_sdk.web.async_client import AsyncWebClient as SlackWebClient

import pagerduty
from slackhandler.modals import incident_modal_payload


async def handle_incident_trigger(state, req: func.HttpRequest) -> func.HttpResponse:
    await present_incident_modal(state, req)
    return func.HttpResponse("", status_code=200)


async def handle_block_suggestion(state, req: func.HttpRequest) -> func.HttpResponse:
    service_selections = [
        {
            "value": service["id"],
            "text": {
                "type": "plain_text",
                "text": service["name"],
            },
        }
        for service in await state.get_pagerduty_services()
    ]
    logging.info("Returning options: %s", service_selections)
    return func.HttpResponse(
        json.dumps({"options": service_selections}),
        status_code=200,
        headers={"Content-Type": "application/json"},
    )


async def handle_view_submission(
    state, req: func.HttpRequest, view_payload
) -> func.HttpResponse:
    form_values = view_payload["view"]["state"]["values"]
    await state.pd_client.create_incident(
        service_id=form_values["service"]["service_value"]["selected_option"]["value"],
        from_email=os.environ["PAGERDUTY_USER_EMAIL"],
        title=form_values["title"]["title_value"]["value"],
        description=form_values["description"]["description_value"]["value"],
    )
    return func.HttpResponse("", status_code=200)


async def present_incident_modal(state, req: func.HttpRequest):
    slack_client = SlackWebClient(
        token=os.environ["SLACK_API_TOKEN"],
        session=state.http_client,
    )

    await slack_client.views_open(
        trigger_id=req.form["trigger_id"],
        view=incident_modal_payload(),
    )
