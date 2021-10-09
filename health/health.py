import azure.functions as func
import pdpyras
import os
import concurrent.futures

from slack_sdk.web.client import WebClient as SlackWebClient


def check_pagerduty():
    pd = pdpyras.APISession(os.environ["PAGERDUTY_API_KEY"])
    user = pd.rget("/users/me")
    if user["email"] != os.environ["PAGERDUTY_USER_EMAIL"]:
        raise Exception(
            "PagerDuty connection OK but account email does not match PAGERDUTY_USER_EMAIL"
        )
    return "OK"


def check_slack():
    client = SlackWebClient(token=os.environ["SLACK_API_TOKEN"])
    client.auth_test()
    return "OK"


def main(req: func.HttpRequest) -> func.HttpResponse:
    # checks maps a human-readable label to the corresponding check function.
    checks = {"slack": check_slack, "pagerduty": check_pagerduty}
    results = {}
    failures = False

    with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(checks)) as executor:
        # futures maps the check names from above to a
        # concurrent.futures.Future object, scheduled for immediate execution
        # on the threadpool.
        futures = {
            check: executor.submit(function)
            for check, function in checks.items()
        }
        for check, future in futures.items():
            try:
                results[check] = future.result()
            except Exception as exception:
                # Stringifying the exception and including it in the HTTP
                # response text assumes libraries are well-behaved and don't
                # leak sensitive information through their exceptions. This
                # should be the case for pdpyras and slack_sdk.
                results[check] = "ERROR: " + str(exception).replace("\n", " ")
                failures = True

    return func.HttpResponse("".join(
        [f"{check}: {result}\n" for check, result in results.items()]),
                             status_code=503 if failures else 200)
