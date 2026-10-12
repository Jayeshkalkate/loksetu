# LOKSETU — Citizen & Customer Issue Resolution Platform

LOKSETU is a Django web application designed to help citizens report civic issues, follow complaint progress, find public-service information, and contact support. It includes role-scoped department workflows, citizen dashboards, a public-safe issue map, appointment booking, moderated reviews, and administrative content modules.

## Main capabilities

- **Citizen accounts:** registration, login throttling, password reset, profile editing, district and mobile validation.
- **Civic complaints:** file a complaint with location and evidence; automatic department routing from category; unique tracking IDs; private evidence access; complaint timeline, notifications, email updates, and status tracking.
- **Citizen complaint management:** edit a complaint only while its status is `Submitted`; withdraw a not-yet-processed complaint. Withdrawals are retained as an auditable `Withdrawn by citizen` status rather than physically deleting the record.
- **Department workflow:** staff dashboard with scoped analytics, department-scoped admin queryset, officer assignment, status actions, evidence/history inlines, and audit entries.
- **Appointments:** request an appointment, see status and officer remarks, reschedule or cancel while pending.
- **Support tickets:** create and track tickets; edit or delete only while the ticket is open.
- **Reviews:** submit a rating and comment; edit or delete one's own review. Edited reviews return to moderation.
- **Public information:** departments, schemes, news, projects, funds, documents, reports, FAQs, emergency contacts, gallery, and job/recruitment notices.
- **Security basics:** CSRF-protected forms, owner-scoped object lookups, role-restricted administration, password validation, file signature and size checks, secure response headers, login throttling, and production secure-cookie settings.

## Requirements

- Python 3.10 or newer (Django 5.2 is required by `requirements.txt`)
- pip and a virtual environment
- SQLite for local development, or PostgreSQL for deployment

## Run locally

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` next to `manage.py` and adjust it for local development:

```dotenv
DEBUG=True
SECRET_KEY=replace-this-with-a-long-random-development-secret
ALLOWED_HOSTS=localhost,127.0.0.1
SECURE_SSL_REDIRECT=False
```

Then run migrations, populate the built-in Maharashtra demo directory, and start the development server:

```bash
python manage.py migrate
python manage.py seed
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. The admin console is at `/admin/`. Use a development-only secret key and demo data locally; never deploy with `DEBUG=True`.

## Tests and checks

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

The test suite covers complaint privacy, ownership and file validation, throttling, admin department scoping, lifecycle CRUD, appointment management, reviews, support tickets, and key public pages.

## Optional Render Static Site loading screen

The `loading-site/` directory contains a branded loader intended to be deployed as a separate Render **Static Site**. It can hide the backend's cold-start wait from users who enter through the Static Site URL: the page checks `/healthz/` and redirects only after the Django app and database respond successfully. See [`loading-site/README.md`](loading-site/README.md) for exact Render settings.

Important: Render controls the platform wake-up page shown when a visitor opens the Django Web Service URL directly. The loader cannot change that platform page; assign your public/custom domain to the Static Site and share its URL to make the branded loader the entry point.

## Production notes

- Set `DEBUG=False`, a strong unique `SECRET_KEY`, `ALLOWED_HOSTS`, and `DATABASE_URL` (PostgreSQL recommended).
- Configure persistent `MEDIA_ROOT` storage for complaint evidence. The app intentionally does not serve evidence through the public media URL; downloads go through an authorization-checking view.
- Configure SMTP environment variables (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL`) to deliver user emails. Without SMTP credentials, Django writes email to the console.
- Configure `CSRF_TRUSTED_ORIGINS` when behind a public HTTPS domain. The Render host is auto-added if `RENDER_EXTERNAL_HOSTNAME` is present.
- Consider a shared cache (Redis, for example) when running multiple web workers; the default local-memory throttle is per process.
- LOKSETU is an independent project, not an official government system unless it has a formal integration or authorization. Do not imply that complaints have been submitted to a department until an authorized workflow confirms receipt.

## Routes added for citizen self-service

- `/profile/edit/` — edit citizen profile details
- `/complaints/<complaint-id>/edit/` — edit a submitted complaint
- `/complaints/<complaint-id>/withdraw/` — withdraw a submitted complaint while retaining its history
- `/appointment/my/<appointment-id>/edit/` — reschedule a pending appointment
- `/appointment/my/<appointment-id>/cancel/` — cancel a pending appointment
- `/support/tickets/<ticket-id>/edit/` and `/delete/` — manage open tickets
- `/reviews/<review-id>/edit/` and `/delete/` — manage the signed-in user's review
