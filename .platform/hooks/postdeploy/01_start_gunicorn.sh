#!/bin/bash
set -e

# Kill any existing gunicorn processes
pkill gunicorn || true

# Start gunicorn explicitly on the expected port
cd /var/app/current
gunicorn --bind 127.0.0.1:8000 application:application --daemon
