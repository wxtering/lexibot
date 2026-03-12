#!/bin/bash
set -e
echo "start migrations"
uv run alembic upgrade head
uv run start_scripts/add_questions.py
echo "migrations completed"

exec "$@"
