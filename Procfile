release: poetry run alembic --config /app/migrations/alembic.ini upgrade head
web: poetry run frame -v --pretty server --workers 2 --port $PORT --host 0.0.0.0
