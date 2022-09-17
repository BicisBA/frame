#!/bin/bash
/app/docker/wait-for-postgres.sh

echo 'upgrading db'
poetry run alembic --config /app/migrations/alembic.ini upgrade head

echo 'starting server'
poetry run uvicorn frame.api.app:app --workers 4 --host 0.0.0.0 --port 5000 --reload
