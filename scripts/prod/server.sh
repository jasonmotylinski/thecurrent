source venv/bin/activate
export PYTHONPATH=dashboard/.
gunicorn --workers 2 --log-level DEBUG --bind unix:/run/thecurrent.sock dashboard.app:server