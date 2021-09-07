# slack-trigger-pd

Trigger PagerDuty incidents from Slack without users needing to have associated PagerDuty accounts.

Runs as a serverless application on [Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/).

## Project status

Working prototype.
Everything works, but it has various sharp edges and a naive trust in data it accepts.

Also, it's only been tested locally (`func start`, requires [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)) and hasn't been run from Azure itself yet.

## To-do

- [ ] Verify requests come from Slack
- [x] Reduce duplication in PagerDuty API client
- [x] Proper error handling in PagerDuty API client
- [ ] Set limit=100 on PagerDuty services API call
- [ ] Tests
- [ ] More extensive typing
- [ ] Support > 100 services in PagerDuty services API call
- [ ] Display user feedback after opening incidents
- [ ] Attach more Slack metadata to opened incidents

## License

This software is dual-licensed under the [Apache 2.0](LICENSE-APACHE) and the [MIT](LICENSE-MIT) licenses.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this project by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any additional terms or conditions.


