def incident_modal_payload():
    """Return the Slack Block Kit payload for the "Create new incident" modal"""
    return {
        "type": "modal",
        "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
        "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
        "title": {"type": "plain_text", "text": "PagerDuty", "emoji": True},
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Create a new PagerDuty incident",
                    "emoji": True,
                },
            },
            {
                "type": "input",
                "block_id": "service",
                "element": {
                    "type": "external_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select service",
                        "emoji": True,
                    },
                    "action_id": "service_value",
                    "min_query_length": 0,
                },
                "label": {
                    "type": "plain_text",
                    "text": "Affected service",
                    "emoji": True,
                },
            },
            {
                "type": "input",
                "block_id": "title",
                "element": {"type": "plain_text_input", "action_id": "title_value"},
                "label": {"type": "plain_text", "text": "Title", "emoji": True},
            },
            {
                "type": "input",
                "block_id": "description",
                "optional": True,
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "description_value",
                },
                "label": {
                    "type": "plain_text",
                    "text": "Description",
                    "emoji": True,
                },
            },
        ],
    }


def incident_created_modal_payload(pd_api_response):
    """Return the Slack Block Kit payload for the "Incident created" modal"""
    # TODO: Use some of the data from pd_api_response to give back a more
    # meaningful response.
    return {
        "response_action": "update",
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Success"},
            "close": {"type": "plain_text", "text": "Close"},
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "plain_text", "text": "Incident created"},
                }
            ],
        },
    }
