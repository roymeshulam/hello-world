# hello world

A dependency-free Python dashboard serving the Salesforce (`CRM`) year-to-date stock-price chart at:

https://hello-world.roymeshulam.com

## Runtime

- **Application:** `app.py`
- **Backend listener:** `127.0.0.1:8001` only
- **Service:** `hello-world.service` (enabled persistent systemd user service)
- **Public route:** Caddy reverse proxy at `hello-world.roymeshulam.com`
- **Health check:** `http://127.0.0.1:8001/healthz`
- **Data endpoint:** `http://127.0.0.1:8001/api/crm-ytd`

## Market data

The dashboard renders a responsive, dependency-free SVG chart from the verified daily CRM snapshot in `data/crm_ytd.json`.

- **Coverage:** Jan 2–Aug 26, 2026
- **Source:** Tastytrade DxLink daily candles
- **Note:** The checked-in snapshot is not a real-time quote.

`Caddyfile.snippet` contains the site’s Caddy route for reference.
