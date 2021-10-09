# slack-trigger-pd

Trigger [PagerDuty](https://www.pagerduty.com/) incidents from [Slack](https://slack.com/) without users needing to have associated PagerDuty accounts.

Runs as a serverless application on [Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/).

## Project status

This is being actively used and supported by the engineering department at [Castor](https://www.castoredc.com/) to allow anyone within the company to open incidents.

## Configuration

In order to work correctly, the following [app settings](https://docs.microsoft.com/en-us/azure/azure-functions/functions-app-settings) are required:

- `PAGERDUTY_API_KEY`:
    A valid PagerDuty [user API token](https://developer.pagerduty.com/docs/ZG9jOjExMDI5NTUx-authentication) (it's recommended to create a dedicated "robot" account for this).
- `PAGERDUTY_USER_EMAIL`: 
    The email address of the user associated with above API key.
- `SLACK_API_TOKEN`: 
    The Slack API token associated with the Slack App (see [Installing into a Slack workspace](#installing-into-a-slack-workspace) below).
- `SLACK_SIGNING_SECRET`: 
    The Slack signing secret, used to validate requests coming from Slack.

### Optional configuration

These optional app settings can be set for additional functionality:

- `SENTRY_DSN`: A [Sentry DSN](https://docs.sentry.io/product/sentry-basics/dsn-explainer/) to enable exception tracking with [Sentry](https://sentry.io/).

## Installing into a Slack workspace

1. Visit <https://api.slack.com/apps/> and click _Create New App_.
2. Choose _From an app manifest_ and select the desired workspace.
3. Paste in the contents from `slack-app-manifest.yml`, making sure to replace `${FUNCTIONS_APP_DOMAIN}` with the endpoint of your deployed Azure Functions app. 
    - Hint: envsubst can be helpful here, try: `FUNCTIONS_APP_DOMAIN=your-function-name.azurewebsites.net envsubst < slack-app-manifest.yml`)
4. Review and complete the installation, then proceed with _Install to Workspace_.

## License

This software is dual-licensed under the [Apache 2.0](LICENSE-APACHE) and the [MIT](LICENSE-MIT) licenses.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this project by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any additional terms or conditions.
