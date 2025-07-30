source venv/bin/activate
export PYTHONPATH=.
gunicorn --workers 7 --worker-class gevent --log-level DEBUG --bind unix:/run/thecurrent.sock dashboard.server:app