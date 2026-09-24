# LOKSETU — Citizen–Government Digital Bridge (Maharashtra)

Django 5.2 project for filing and tracking civic complaints, plus schemes, news, departments and emergency contacts.

## Run locally
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # then set DEBUG=True in .env for local work
python manage.py migrate
python manage.py seed                                 # districts, departments, categories, emergency numbers
python manage.py seed --demo                          # optional: placeholder scheme + announcement (dev only)
python manage.py createsuperuser
python manage.py runserver
```
`DEBUG` is **off by default** (secure by default). With it off, `SECRET_KEY` is mandatory.

## Tests
```bash
DEBUG=True python manage.py test
```
30 tests cover registration, login/throttling, password reset, complaint filing, upload validation, privacy rules,
evidence access control, admin department scoping and the public pages.

## Roles
Citizens self-register. Staff accounts are created in `/admin/` → Users: set **role** (Officer / Department
Administrator / Super Administrator) and **department**. Saving the user automatically ticks *staff* and adds them to the
right permission group (`Officers` / `Department Admins`, created on every `migrate`).

| Role | Sees in admin | Can change |
|---|---|---|
| Officer | complaints assigned to them | status only |
| Department Admin | their department's complaints | status + assign to an officer of their department |
| Super Admin / superuser | everything | everything |

Bulk actions "Mark as In progress / Resolved" record timeline entries, notify the citizen and write an audit log.

## Privacy model
* The public tracking page (by Complaint ID) shows only category, status, district, department and timeline.
  Title, description, notes and evidence are visible to the complainant and in-scope staff only.
* Evidence files are **never served directly**. They are streamed by `/complaints/evidence/<id>/` after a permission check.
* Uploads are checked for extension, size (10 MB) **and** real file signature (JPG/PNG/PDF/MP4).
* The public map rounds coordinates to ~1 km and exposes no personal data.
* Rate limits: login, registration, password reset, complaint filing (20/day/user) and ID lookups.

## Deploying (Render / Heroku-style)
Build command:
```
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py seed
```
Start command: `gunicorn config.wsgi` (the `Procfile` has a tuned version). Health check path: `/healthz/`.

Environment variables (see `.env.example`):
* `SECRET_KEY` (required), `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS=https://<your-app>` (Render's hostname is auto-added)
* `DATABASE_URL` — a Postgres URL (e.g. Neon, with `?sslmode=require`)
* `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` — Gmail app password or any SMTP; without it emails print to the log
* `MEDIA_ROOT` — **must point to a persistent disk** (see below)
* `CONTACT_EMAIL`, `LINKEDIN_URL`, `PORTFOLIO_URL`, `GITHUB_URL`, `INSTAGRAM_URL` — shown on the Contact page/footer; blank ones are hidden
* `SENTRY_DSN` — optional error monitoring

Create the first admin without a shell prompt:
`DJANGO_SUPERUSER_PASSWORD=... python manage.py createsuperuser --noinput --username admin --email you@example.com`

### Things to know before real users arrive
1. **Evidence storage.** Files live on local disk (`MEDIA_ROOT`). On free tiers with an ephemeral filesystem they vanish on
   redeploy, so attach a persistent disk. Cloud object storage (S3/R2) is a sensible next step for scale.
2. **Rate limits use per-process memory.** With N gunicorn workers the effective limit is up to N× higher. For strict
   limits switch `CACHES` to Redis or the database cache.
3. **SQLite is for development only.** Set `DATABASE_URL` in production.
4. **Content.** Add real schemes/news in `/admin/` with their official source URLs; nothing placeholder is loaded in production.
5. The Bootstrap/Leaflet assets load from public CDNs; vendor them under `static/` if you need a strict Content-Security-Policy.

## Not yet built
Projects, funds, documents, reports, FAQ and support apps; admin charts; Marathi translation; SMS delivery;
multiple evidence files per complaint; district-wise map table (data is at `/complaints/map/data/`).
