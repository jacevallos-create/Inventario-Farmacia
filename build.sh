#!/usr/bin/env bash
set -o errexit

python -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build
python manage.py collectstatic --no-input
python manage.py migrate --no-input
