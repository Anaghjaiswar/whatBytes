#!/bin/sh

set -e

ls -la /vol/
ls -la /vol/web

whoami

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate

# Load initial data for development (creates users, patients, doctors, etc.)
# Only run ingest if there are no PatientProfile records yet
if python manage.py shell -c "from app.models import PatientProfile; print(PatientProfile.objects.exists())" | grep -q True; then
	echo "Initial data exists — skipping ingest_initial_data"
else
	echo "No initial data found — running ingest_initial_data"
	python manage.py ingest_initial_data
fi

python -m gunicorn --workers 4 --bind 0.0.0.0:8000  core.asgi:application -k uvicorn.workers.UvicornWorker