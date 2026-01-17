#!/bin/bash

git pull
redis-cli flushdb
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
systemctl restart thecurrent.socket