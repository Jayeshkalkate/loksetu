# LOKSETU — new features from the cybercafe project

This adds: Gallery, Reviews, Job & Recruitment Notifications, and Book Appointment
(+ a "My appointments" section on the profile/dashboard page). Terms, Privacy,
Dashboard and Profile already existed in LOKSETU so those were extended in place
instead of duplicated.

Already tested end-to-end (migrations applied, all pages return 200, both the
review form and appointment form submit and redirect correctly).

## How to apply

1. Copy these folders straight into your LOKSETU project root (same level as
   `manage.py`), overwriting nothing that doesn't already exist there:
   - `gallery/`
   - `reviews/`
   - `jobs/`
   - `appointments/`
   - `templates/gallery/`, `templates/reviews/`, `templates/appointments/`
     (merge into your existing `templates/` folder)

2. These 3 files already exist in your project and were modified — replace them:
   - `config/settings.py` — added `'gallery', 'reviews', 'jobs', 'appointments'`
     to `INSTALLED_APPS` (only that one line changed; if you've edited settings.py
     since, just add those 4 app names yourself instead of overwriting the file)
   - `config/urls.py` — added routes for jobs/gallery/reviews/appointment
   - `accounts/views.py` — `profile()` now also loads the user's recent appointments

3. These 3 templates already exist and were modified — replace them, or apply
   the small diffs yourself if you've customized them:
   - `templates/base.html` — added nav links (Jobs, Gallery, Reviews, Book Appointment)
   - `templates/list.html` — added a "last date to apply" line for job postings
     (harmless no-op for schemes/news, which don't have that field)
   - `templates/profile.html` — added a "My appointments" section + button

4. Run:
   ```
   python manage.py makemigrations   # should say "No changes" — migrations are included
   python manage.py migrate
   ```

## What each app does

- **gallery** — `/gallery/` public photo grid, grouped by category. Manage photos
  from Django admin (`GalleryImage`).
- **reviews** — `/reviews/` logged-in users submit a 1–5 star rating + comment;
  shows only admin-approved reviews publicly. Approve reviews from Django admin
  (there's a bulk "Approve selected reviews" action).
- **jobs** — `/jobs/` public job/recruitment notice board (reuses your existing
  generic list template). Manage from Django admin (`JobNotification`).
- **appointments** — `/appointment/` book an appointment with a department;
  `/appointment/my/` and `/appointment/my/<id>/` for the citizen's own bookings.
  Manage/confirm from Django admin (`Appointment`).
