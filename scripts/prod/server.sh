source venv/bin/activate
export PYTHONPATH=.
gunicorn --workers 3 --log-level DEBUG --bind unix:/run/thecurrent.sock dashboard.server:app