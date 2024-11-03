source venv/bin/activate
export PYTHONPATH=dashboard/.
gunicorn --workers 3 --log-level DEBUG --bind unix:/run/thecurrent.sock dashboard.app:server