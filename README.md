# Event Reservation System (Movies)

Django + DRF cinema reservation API with JWT auth and M-Pesa (Daraja) STK push.
Field-level shapes, request/response examples, and try-it-out live in Swagger/Redoc — this README is a map, not a schema dump.

- Swagger UI: `GET /api/docs/`
- Redoc: `GET /api/redoc/`
- Raw schema: `GET /api/schema/`

## How booking works

1. `POST /showtimes/{showtime_id}/hold/` — hold seats (`HOLD_DURATION = 10 min`).
2. `POST /payments/initiate/` — creates `MpesaPayment(PENDING)` + STK push to phone.
3. Safaricom → `POST /mpesa/callback/` — `COMPLETED` → tickets become `BOOKED`; failure → `FAILED`.
4. `POST /tickets/cancel/` — releases `HELD`/`BOOKED` tickets back to `AVAILABLE`.
5. Guards: can't book within `BOOKING_CUTOFF = 10 min` of `start_time`; overlapping `Showtime`s on the same `Screen` are rejected (`Showtime.clean()`).

Ticket lifecycle: `available → held → booked`. Payments: `pending → completed | failed`.

## Stack

Python >=3.14, Django, DRF, SimpleJWT, drf-spectacular, Postgres (`psycopg[binary]`), Gunicorn, `django-environ`. Managed with Poetry.

## Quickstart

```bash
poetry install
cp .env.example .env   # fill in real values; .env is gitignored
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
poetry run python manage.py runserver
curl -s localhost:8000/health/
```

Run tests:

```bash
poetry run python manage.py test system.tests
```

## Required env

Database: `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT` (Postgres port — not the HTTP port).
Django: `SECRET_KEY`, `NGROK_URL` (required — used in `ALLOWED_HOSTS`; use your ngrok host or domain).
M-Pesa Daraja: `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `MPESA_SHORTCODE`, `MPESA_PASSKEY`, `MPESA_CALLBACK_URL`, plus `MPESA_BASE_URL` (e.g. sandbox `https://sandbox.safaricom.co.ke`).

## Run with Gunicorn (no nginx)

```bash
poetry run gunicorn core.wsgi:application -c gunicorn.conf.py
# custom port / workers:
GUNICORN_PORT=8000 WEB_CONCURRENCY=2 poetry run gunicorn core.wsgi:application -c gunicorn.conf.py
```

What `gunicorn.conf.py` does:

- `bind = 0.0.0.0:$GUNICORN_PORT` (default `8000`). `$PORT` in `.env` is Postgres — intentionally separate.
- `workers = $WEB_CONCURRENCY or (2*CPU)+1`. You need workers: master + N workers serve concurrent API/callback requests; one slow Daraja call would otherwise block everything. No server tuning needed — set `WEB_CONCURRENCY=2` on a small VPS.
- `worker_class = sync` (right for Django ORM), `timeout = 90` (Daraja is slow; default 30s kills payments), `max_requests = 1000 + jitter` (recycle workers).
- Logs to stdout/stderr (`accesslog/errorlog = "-"`) — Docker captures it; on a VPS `journalctl` captures it. Django app log still goes to `logs/system.log`.
- `preload_app = False` so each worker opens its own DB connection after fork.

Docker-ready means: same file + same command work on a VPS and in a container (no hardcoded paths/users, `0.0.0.0` bind, env-driven). Add TLS/static handling later via a proxy if needed.

Check config without booting:

```bash
poetry run gunicorn --check-config core.wsgi:application -c gunicorn.conf.py
```

## Auth

JWT (`rest_framework_simplejwt`):

```bash
POST /auth/register/  # username, email, phone_number, password
POST /auth/login/     # -> access + refresh
GET  /clients/me/     # Header: Authorization: Bearer <access>
POST /auth/refresh/   # -> new access
```

`/mpesa/callback/` and `/health/` are public (`AllowAny`); everything else requires JWT except register/login/refresh.

## Endpoints (see live docs for shapes)

| Group    | Method & path                              | Auth |
|----------|---------------------------------------------|------|
| Movies   | `GET /movies/`, `GET /movies/<id>/`         | JWT  |
| Showtimes| `GET /showtimes/`, `GET /showtimes/<id>/`   | JWT  |
| Cinemas  | `GET /cinemas/`, `GET /cinemas/<id>/`       | JWT  |
|          | `GET /cinemas/<cinema_id>/showtimes/`       | JWT  |
| Tickets  | `GET /showtimes/<showtime_id>/tickets/`     | JWT  |
|          | `POST /showtimes/<showtime_id>/hold/`       | JWT  |
|          | `POST /tickets/cancel/`                     | JWT  |
| Payments | `POST /payments/initiate/`                  | JWT  |
|          | `GET /payments/<id>/`                       | JWT  |
|          | `POST /mpesa/callback/`                     | open |
| Auth     | `POST /auth/register|login|refresh/`        | open |
| Clients  | `GET /clients/me/`                          | JWT  |
| System   | `GET /health/`                              | open |
| Docs     | `GET /api/schema|docs|redoc/`               | open |

Models in brief: `Cinema → Screen → Seat`; `Movie → Showtime(screen, start/end, price)`; `Ticket(showtime+seat unique, held_by, held_until, payment)`; `MpesaPayment(checkout_request_id, status, amount)`; `Client(AbstractUser, UUID PK, phone_number)`. Full fields + serializers (`Cinema/Screen/Seat`, `Movie/Showtime`, `Ticket/Hold`, `PaymentInitiate/MpesaPayment`, `Client/Registration`) are documented in Swagger/Redoc.

Validate docs build:

```bash
poetry run python manage.py spectacular --file /tmp/schema.yml --validate
```

## Layout

```text
core/            # settings, urls (incl. api/schema|docs|redoc), wsgi
system/
  models/        # cinema, movies, ticket, client
  serializers/   # cinema, movie, ticket, mpesa, client
  views/         # cinema, movies, showtimes, bookings, client, health_checks
  tests/
  urls.py
gunicorn.conf.py
logs/system.log  # gitignored
```

## Ops notes

- `DEBUG=False` in `core/settings.py` — don't run `runserver` in prod; use Gunicorn.
- Missing `NGROK_URL` crashes boot (used in `ALLOWED_HOSTS`). For prod without ngrok, replace with your domain env.
- `mpesa/callback/` must be publicly reachable (ngrok/domain + `MPESA_CALLBACK_URL` pointing at it), else Safaricom can't deliver receipts.
