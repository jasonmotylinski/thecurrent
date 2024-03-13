source venv/bin/activate
export PYTHONPATH=dashboard/.
gunicorn --workers 2 --log-level DEBUG --logger-class root --bind unix:/run/thecurrent.sock dashboard.app:server