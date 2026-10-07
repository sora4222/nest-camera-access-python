# Login

You log in once. The package then keeps the Token and gets fresh access on its own.

## 1. Google setup (once)

1. Follow Google's [Device Access get started guide](https://developers.google.com/nest/device-access/get-started) to make a Google Cloud project and a Device Access project.
2. In Google Cloud, make an OAuth client of type **Web application** with these redirect URIs:
   - `https://www.google.com` (for Server login)
   - `http://localhost:8080` (for browser login and SSH tunnels)
3. Note the client ID, client secret and Device Access project ID.

## 2. Give the package your Credentials

Pass them in code, or set environment variables:

```sh
GOOGLENESTCAM_CLIENT_ID=...
GOOGLENESTCAM_CLIENT_SECRET=...
GOOGLENESTCAM_PROJECT_ID=...
```

Any of these may be a 1Password reference such as `op://vault/item/field`. That needs `pip install googlenestcam[onepassword]` and `OP_SERVICE_ACCOUNT_TOKEN`. If 1Password fails you get a warning, and values passed in code still work.

## 3. Log in

```python
import googlenestcam as gnc

gnc.login()  # opens your browser
gnc.login(
    "server"
)  # no browser: open the link on any device, then paste the google.com address
```

The Token is saved to `~/.config/googlenestcam/token.json` (only you can read it). Change this with `token_path=` or `GOOGLENESTCAM_TOKEN_PATH`.

## On a server

Pick one:

- **Server login**: `gnc.login("server")`, as above.
- **SSH tunnel**: connect with `ssh -L 8080:localhost:8080 server`, run `gnc.login()` on the server, and open the printed link on your laptop.
- **Copy the Token**: log in on your laptop, then copy the Token file to the server, or put the refresh token in `GOOGLENESTCAM_REFRESH_TOKEN` (an `op://` reference works too).

## When there is no Token

By default the package starts a browser login when it needs a Token and has none. To get a `MissingTokenError` instead, pass `on_missing_token="raise"`.
