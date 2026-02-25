source venv/bin/activate
export PYTHONPATH=.
gunicorn --workers 2 --worker-class gevent --log-level DEBUG --bind unix:/run/thecurrent.sock dashboard.server:app