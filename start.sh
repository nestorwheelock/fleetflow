#!/bin/bash
# FleetFlow Development Server Startup Script
# Runs on port 9091

cd "$(dirname "$0")"

# Kill any existing server on port 9091
pkill -f "runserver.*9091" 2>/dev/null

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run migrations if needed
python manage.py migrate --check >/dev/null 2>&1 || python manage.py migrate

# Start the development server
echo "Starting FleetFlow on http://localhost:9091"
python manage.py runserver 0.0.0.0:9091
