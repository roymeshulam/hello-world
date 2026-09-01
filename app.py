#!/usr/bin/env python3
"""Salesforce CRM year-to-date stock-price dashboard."""

from __future__ import annotations

import html
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


HOST = "127.0.0.1"
PORT = 8001
DATA_PATH = Path(__file__).parent / "data" / "crm_ytd.json"


def load_market_data() -> dict[str, Any]:
    """Load the checked-in, verified daily CRM YTD price snapshot."""
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if payload.get("symbol") != "CRM" or not payload.get("points"):
        raise ValueError("CRM YTD data is missing or invalid")
    return payload


def chart_svg(points: list[dict[str, Any]]) -> str:
    """Build an accessible, dependency-free SVG line chart from daily closes."""
    width, height = 900, 410
    left, right, top, bottom = 70, 24, 26, 54
    chart_width, chart_height = width - left - right, height - top - bottom
    closes = [float(point["close"]) for point in points]
    low, high = min(closes), max(closes)
    padding = max((high - low) * 0.08, 1)
    low, high = low - padding, high + padding

    def x(index: int) -> float:
        return left + chart_width * index / (len(points) - 1)

    def y(price: float) -> float:
        return top + chart_height * (high - price) / (high - low)

    line = " ".join(f"{x(i):.2f},{y(float(point['close'])):.2f}" for i, point in enumerate(points))
    grid = []
    for step in range(5):
        price = low + (high - low) * step / 4
        y_pos = y(price)
        grid.append(
            f'<line x1="{left}" y1="{y_pos:.2f}" x2="{width - right}" y2="{y_pos:.2f}" class="grid"/>'
            f'<text x="{left - 10}" y="{y_pos + 4:.2f}" class="axis" text-anchor="end">${price:.0f}</text>'
        )

    month_labels: list[str] = []
    last_month = ""
    for index, point in enumerate(points):
        month = point["date"][:7]
        if month != last_month:
            label = point["date"][5:7]
            month_labels.append(
                f'<text x="{x(index):.2f}" y="{height - 19}" class="axis" text-anchor="middle">{label}/26</text>'
            )
            last_month = month

    last = points[-1]
    return f'''<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="Salesforce CRM daily closing stock price chart year to date">
      <title>Salesforce CRM YTD closing price</title>
      <rect x="{left}" y="{top}" width="{chart_width}" height="{chart_height}" class="plot"/>
      {''.join(grid)}
      <polyline points="{line}" class="line"/>
      <circle cx="{x(len(points) - 1):.2f}" cy="{y(float(last['close'])):.2f}" r="5" class="dot"/>
      <text x="{x(len(points) - 1) - 10:.2f}" y="{y(float(last['close'])) - 12:.2f}" class="last" text-anchor="end">${float(last['close']):.2f}</text>
      {''.join(month_labels)}
    </svg>'''


def render_page(payload: dict[str, Any]) -> bytes:
    points = payload["points"]
    first, last = points[0], points[-1]
    ytd_change = 100 * (float(last["close"]) / float(first["close"]) - 1)
    direction = "up" if ytd_change >= 0 else "down"
    chart = chart_svg(points)
    today = datetime.now(ZoneInfo("Europe/Zurich")).date().isoformat()
    source = html.escape(str(payload["source"]))
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Salesforce (CRM) YTD Stock Price — {today}</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background: #07111f; color: #e7eefb; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px; }}
    main {{ width: min(100%, 1020px); }}
    .eyebrow {{ color: #61d7bb; font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }}
    h1 {{ margin: .35rem 0 .3rem; font-size: clamp(1.9rem, 5vw, 3.25rem); letter-spacing: -.04em; }}
    .subtle {{ color: #a9bad1; margin: 0 0 22px; }}
    .card {{ background: #0d1b2f; border: 1px solid #1d3554; border-radius: 18px; padding: clamp(16px, 3vw, 30px); box-shadow: 0 18px 45px #0004; }}
    .stats {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-bottom: 22px; }}
    .stat {{ background: #101f36; border-radius: 12px; padding: 14px; }}
    .label {{ display: block; color: #a9bad1; font-size: .75rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }}
    .value {{ display: block; margin-top: 5px; font-size: clamp(1.05rem, 3vw, 1.55rem); font-weight: 750; }}
    .negative {{ color: #ff9d9d; }} .positive {{ color: #61d7bb; }}
    .chart {{ width: 100%; height: auto; display: block; overflow: visible; }}
    .plot {{ fill: #081526; }} .grid {{ stroke: #24415f; stroke-width: 1; stroke-dasharray: 3 6; }}
    .line {{ fill: none; stroke: #61d7bb; stroke-width: 3; stroke-linejoin: round; stroke-linecap: round; }}
    .dot {{ fill: #61d7bb; stroke: #07111f; stroke-width: 3; }} .axis {{ fill: #8fa6c4; font-size: 13px; }} .last {{ fill: #d8fff5; font-size: 15px; font-weight: 700; }}
    footer {{ margin-top: 16px; color: #8fa6c4; font-size: .82rem; }}
    @media (max-width: 560px) {{ body {{ padding: 14px; }} .stats {{ grid-template-columns: 1fr; }} .card {{ padding: 14px; }} }}
  </style>
</head>
<body>
  <main>
    <div class="eyebrow">NYSE: CRM · Daily close</div>
    <h1>Salesforce year to date — {today}</h1>
    <p class="subtle">Daily closing-price performance from {first['date']} through {last['date']}.</p>
    <section class="card" aria-label="Salesforce stock chart and summary">
      <div class="stats">
        <div class="stat"><span class="label">Latest close</span><span class="value">${float(last['close']):.2f}</span></div>
        <div class="stat"><span class="label">YTD change</span><span class="value {'positive' if ytd_change >= 0 else 'negative'}">{ytd_change:+.2f}%</span></div>
        <div class="stat"><span class="label">YTD start</span><span class="value">${float(first['close']):.2f}</span></div>
      </div>
      {chart}
    </section>
    <footer>Data source: {source}. Snapshot as of {payload['as_of']}; prices are not real-time.</footer>
  </main>
</body>
</html>'''.encode("utf-8")


class DashboardHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._send(200, b"", "text/plain; charset=utf-8")
            return
        if self.path == "/api/crm-ytd":
            self._send(200, DATA_PATH.read_bytes(), "application/json; charset=utf-8")
            return
        if self.path == "/":
            self._send(200, render_page(load_market_data()), "text/html; charset=utf-8")
            return
        self.send_error(404)

    def do_HEAD(self) -> None:
        self.do_GET()

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        print("%s - %s" % (self.address_string(), format % args), flush=True)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), DashboardHandler)
    print(f"Serving Salesforce CRM YTD dashboard on http://{HOST}:{PORT}", flush=True)
    server.serve_forever()
