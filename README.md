# hello world

A minimal Python site that serves a single **Hello World** heading at:

https://hello-world.roymeshulam.com

## Runtime

- **Application:** `app.py`
- **Backend listener:** `127.0.0.1:8001` only
- **Service:** `hello-world.service` (enabled persistent systemd user service)
- **Public route:** Caddy reverse proxy at `hello-world.roymeshulam.com`
- **Health check:** `http://127.0.0.1:8001/healthz`

`Caddyfile.snippet` contains the site’s Caddy route for reference.
