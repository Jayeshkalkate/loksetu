# LOKSETU Render loading page

This folder is a standalone Render Static Site. It displays a custom, branded loading screen while it probes the Django web service's `/healthz/` endpoint. When that endpoint returns HTTP 200 with the exact text `ok`, the loader redirects the visitor to the Django site.

## Render setup

1. Deploy the Django app as a **Web Service** as usual. Keep its backend URL, for example `https://loksetu-api.onrender.com`.
2. In Render, create a separate **Static Site** from the same repository and branch.
3. Configure the Static Site:
   - **Root Directory:** `loading-site`
   - **Build Command:** `python build_config.py`
   - **Publish Directory:** `.`
   - **Environment Variable:** `BACKEND_URL` = the Django Web Service origin, e.g. `https://loksetu-api.onrender.com` (HTTPS, no path, query, or trailing slash required).
4. Deploy the Static Site. Its own Render URL should show the LOKSETU loading screen first.
5. Share the **Static Site URL** with users. If you use a custom domain, attach that domain to the Static Site, not directly to the Django Web Service. Keep the backend URL as the destination used by the loader.

The build script deliberately fails if `BACKEND_URL` is missing or malformed, instead of deploying a page that silently points to the wrong place. After changing `BACKEND_URL`, trigger a new Static Site deploy so `config.js` is regenerated.

## Important limitation

This cannot replace Render's platform wake-up page when a visitor goes directly to the Django Web Service URL. Render controls that page before Django starts. This loader works by making the Static Site the public entry URL: the Static Site stays available, performs the wake-up request invisibly, and redirects after Django and its database are ready. Direct backend links and links shared by your app may still display Render's own wake-up UI.

## How readiness works

- The page requests `GET {BACKEND_URL}/healthz/` with cache disabled.
- Django's health endpoint runs a lightweight `SELECT 1` database check.
- A successful response must be HTTP 200 with body `ok`.
- The endpoint sets `Access-Control-Allow-Origin: *` because it exposes only a non-sensitive readiness result, allowing the separate static origin to read the response. It does not enable cross-origin access to authenticated application pages.
- The loader retries with a delay while the service wakes. After five minutes it shows a retry button and troubleshooting hint; the page does not claim success unless it gets a real healthy response.

## Local preview and smoke tests

The checked-in `config.js` intentionally has an empty URL and displays a configuration message. For a local preview, run these commands from the `loading-site/` directory in a POSIX shell:

```bash
BACKEND_URL=http://127.0.0.1:8000 python build_config.py
python -m http.server 8001
```

Start Django separately on port 8000 and visit `http://127.0.0.1:8001`. The builder allows HTTP only for localhost preview; public Render URLs must use HTTPS. Restore the checked-in blank `config.js` afterwards if you do not want to commit your local backend URL.

Run the dependency-free loader smoke tests with Node.js:

```bash
node test_loader.mjs
```
