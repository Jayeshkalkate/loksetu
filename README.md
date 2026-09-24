# LOKSETU — Citizen–Government Digital Bridge (Maharashtra)

Django project for reporting and tracking civic complaints, plus schemes, news, departments and emergency contacts.

## Run locally
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed
python manage.py createsuperuser
python manage.py runserver
```

## Roles
Citizens self-register. Officers / department admins are created in `/admin/` (set `role`, `department`, tick "staff",
and grant complaint permissions via a group). Department admins see their department's complaints; officers see assigned ones.

## Not yet built
projects, funds, documents, reports, faq, support and dashboard apps; admin charts; Marathi translation; email/SMS delivery;
multiple evidence files per complaint; district-wise map table (data is at `/complaints/map/data/`).
Seed schemes/news are placeholders: replace them with verified data and official sources.

## Deploying (e.g. Render)
Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py seed`
Set `DEBUG=False`, a real `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS=https://<your-app>.onrender.com`.
The app refuses to start with `DEBUG=False` and no `SECRET_KEY`. Uploaded evidence is stored on local disk, which is
wiped on redeploy on free hosting tiers; use external media storage before going live.
