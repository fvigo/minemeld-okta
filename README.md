# minemeld-okta

This repo contains the code for the MineMeld extension for Okta.

The extension currently includes a single MineMeld Output node that enables the remediation use case: once an indicator of type "user-id" is sent to the Output node, the module invokes Okta's API to either add the user to an Okta group (i.e. Quarantine), Suspend the user (and Unsuspend when the indicator is withdrawn) and Clear User's Sessions within Okta.

The configuration can be set through the Web UI. Parameters include the Okta base URL, the Authentication Token, the Quarantine Group and booleans to determine the behavior (Clear User Sessions, Suspend User on update, Unsuspend User on withdraw)

# EXPERIMENTAL

This software is experimental, use at your own risk!

