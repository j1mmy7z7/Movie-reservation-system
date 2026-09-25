"""Gunicorn config for the Event Reservation System (Django).

Run:
    poetry run gunicorn core.wsgi:application -c gunicorn.conf.py

Docker-ready: no hardcoded users/paths, binds 0.0.0.0, logs to stdout/stderr.
No nginx required for now — Gunicorn serves Django directly.
"""

import multiprocessing
import os


def _workers_default() -> int:
    # Classic formula: (2 * CPU) + 1. Works on any box, no server tuning needed.
    # Override with WEB_CONCURRENCY env on cheap VPS (e.g. WEB_CONCURRENCY=2).
    try:
        return (multiprocessing.cpu_count() * 2) + 1
    except NotImplementedError:
        return 3


# NOTE: .env PORT is the Postgres port, not the HTTP port.
# Use GUNICORN_PORT to avoid the collision. Defaults to 8000.
bind = f"0.0.0.0:{os.getenv('GUNICORN_PORT', '8000')}"

workers = int(os.getenv("WEB_CONCURRENCY", str(_workers_default())))
worker_class = "sync"  # correct for Django ORM; use "gthread" only if M-Pesa I/O blocks
threads = int(os.getenv("GUNICORN_THREADS", "1"))

# Daraja STK push can be slow — default 30s timeout would kill workers mid-payment.
timeout = int(os.getenv("GUNICORN_TIMEOUT", "90"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = 5

# Recycle workers to guard against slow memory growth. Zero server setup needed.
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "100"))

# Docker-friendly logging: container runtimes capture stdout/stderr.
# On a VPS with systemd, the same stream is captured by journalctl.
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOGLEVEL", "info")

proc_name = "event-reservation-system"

# False is safer with Django DB connections (each worker connects after fork).
# True would save RAM but risks sharing connections across workers.
preload_app = False

# Fail fast if required env is missing — settings.py reads SECRET_KEY and
# NGROK_URL (used in ALLOWED_HOSTS) via django-environ at import time.
# Ensure .env / environment provides them before launching.
