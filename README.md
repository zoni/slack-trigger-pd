# slack-trigger-pd

Trigger PagerDuty incidents from Slack without users needing to have associated PagerDuty accounts.

Runs as a serverless application on [Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/).

## Project status

Working prototype.
Everything works, but it has various sharp edges and a naive trust in data it accepts.

Also, it's only been tested locally (`func start`, requires [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)) and hasn't been run from Azure itself yet.

## To-do

- [ ] Verify requests come from Slack
- [ ] Tests
- [ ] More extensive typing
- [x] Support > 100 services in PagerDuty services API call
- [x] Display user feedback after opening incidents
- [ ] Attach more Slack metadata to opened incidents

## Installing into a Slack workspace

1. Visit <https://api.slack.com/apps/> and click _Create New App_.
2. Choose _From an app manifest_ and select the desired workspace.
3. Paste in the contents from `slack-app-manifest.yml`, making sure to replace `${FUNCTIONS_APP_DOMAIN}` with the endpoint of your deployed Azure Functions app. 
    - Hint: envsubst can be helpful here, try: `FUNCTIONS_APP_DOMAIN=your-function-name.azurewebsites.net envsubst < slack-app-manifest.yml`)
4. Review and complete the installation, then proceed with _Install to Workspace_.

## License

This software is dual-licensed under the [Apache 2.0](LICENSE-APACHE) and the [MIT](LICENSE-MIT) licenses.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this project by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any additional terms or conditions.


