# Server login pastes an address instead of using a device code

Google's device code login ("enter this code on another device") only allows a few scopes, and the Smart Device Management scope is not one of them ([Google's list](https://developers.google.com/identity/protocols/oauth2/limited-input-device)). On a machine with no browser, a Login therefore follows Google's [Device Access guide](https://developers.google.com/nest/device-access/authorize): the developer approves on another device, Google redirects to `https://www.google.com`, and the developer pastes that address back. Developers create a Web application OAuth client with both `https://www.google.com` and `http://localhost:8080` as redirect addresses, so one client covers browser Login, Server login and SSH tunnels.

## Considered Options

- **Device code flow**: not allowed for the Nest scope.
- **Paste a `localhost` address that fails to load**: works, but `www.google.com` loads, so it is less confusing.
- **Copying the Token from another machine**: also supported, but it still needs one Login somewhere.
