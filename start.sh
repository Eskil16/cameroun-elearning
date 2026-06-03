#!/usr/bin/env bash
set -e
cd backend
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --log-level info \
    --access-logfile -
