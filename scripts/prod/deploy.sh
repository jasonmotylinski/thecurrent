#!/bin/bash

git pull
redis-cli flushdb
systemctl restart thecurrent.socket