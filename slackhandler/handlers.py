import json
import uuid

import azure.functions as func

from slackhandler.modals import incident_created_modal_payload, incident_modal_payload


def handle_incident_trigger(state, req: func.HttpRequest) -> func.HttpResponse:
    """Handler for the `/incident` slash command"""
    state.slack_client.views_open(
        trigger_id=req.form["trigger_id"],
        view=incident_modal_payload(),
    )
    return func.HttpResponse("", status_code=200)


def handle_block_suggestion(state, _req: func.HttpRequest) -> func.HttpResponse:
    """
    Handler for Slack's block_suggestion event.

    This is called to get items for the "Affected service" selection dropdown.
    """
    service_selections = [
        {
            "value": service["id"],
            "text": {
                "type": "plain_text",
                "text": service["name"],
            },
        }
        for service in state.get_pagerduty_services()
    ]
    return func.HttpResponse(
        json.dumps({"options": service_selections}),
        status_code=200,
        headers={"Content-Type": "application/json"},
    )


def handle_view_submission(
    state, _req: func.HttpRequest, view_payload
) -> func.HttpResponse:
    """
    Handler for Slack's view_submission event.

    This is called when a user presses Submit on the modal created by
    `handle_incident_trigger`.
    """
    # The user attribute in view_payload only contains the user `id`,
    # `team_id`, `username` and `name` attributes. Slack API docs mention
    # `name` is deprecated and should not be used. This leaves us with `name`
    # (holding the user's @username) as the only usable attribute.
    slack_username = view_payload["user"]["username"]
    form_values = view_payload["view"]["state"]["values"]

    service_id = form_values["service"]["service_value"]["selected_option"]["value"]
    title = form_values["title"]["title_value"]["value"]
    description = form_values["description"]["description_value"]["value"]

    incident_body = f"This incident was created via Slack by {slack_username}"
    if description is not None and description.strip() != "":
        incident_body += f" with the following description:\n\n{description}"

    incident_info = state.pd_client.rpost(
        "/incidents",
        json={
            "incident": {
                "type": "incident",
                "title": title,
                "service": {"id": service_id, "type": "service_reference"},
                "urgency": "high",
                "incident_key": uuid.uuid4().hex,
                "body": {"type": "incident_body", "details": incident_body},
            }
        },
    )
    return func.HttpResponse(
        json.dumps(incident_created_modal_payload(incident_info)),
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
