"""Generate the static loader's runtime config from Render's BACKEND_URL env var."""
import json
import os
from pathlib import Path
from urllib.parse import urlparse

root = Path(__file__).resolve().parent
raw_url = os.environ.get("BACKEND_URL", "").strip().rstrip("/")
if not raw_url:
    raise SystemExit(
        "BACKEND_URL is required. Set it in the Render Static Site environment, "
        "for example https://loksetu-api.onrender.com, then redeploy."
    )

parsed = urlparse(raw_url)
is_local_http = parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1"}
if (parsed.scheme != "https" and not is_local_http) or not parsed.netloc or parsed.username or parsed.password:
    raise SystemExit("BACKEND_URL must be a public HTTPS origin (HTTP is allowed only for localhost preview)")
if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
    raise SystemExit("BACKEND_URL must be an origin only: do not include a path, query, or fragment")

# JSON encoding safely escapes the value before inserting it into JavaScript.
config = "/* Generated from the Render BACKEND_URL environment variable. */\n"
config += "window.LOKSETU_CONFIG = { backendUrl: " + json.dumps(raw_url) + " };\n"
(root / "config.js").write_text(config, encoding="utf-8")
print(f"Generated loader config for {parsed.netloc}")
