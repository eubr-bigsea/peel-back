#!/bin/sh
set -e

# Export common environment variables
export FLASK_ENV=${FLASK_ENV:-development}
export FLASK_APP=${FLASK_APP:-/peel-back/xai_app.py}
export TZ=${TZ:-America/Sao_Paulo}

# Navigate to the working directory
cd /peel-back

# Function to initialize migrations directory if not exists
initialize_migrations() {
    if [ ! -f "migrations/env.py" ]; then
        echo "Initializing migrations directory..."
        if ! flask db init; then
            echo "Failed to initialize migrations directory."
            exit 1
        fi
        if ! flask db migrate -m "automated migration"; then
            echo "Failed to create initial migration."
            exit 1
        fi
        if ! flask db upgrade; then
            echo "Failed to apply initial migration."
            exit 1
        fi
        echo "Migrations initialized successfully."
    else
        if ! flask db upgrade; then
            echo "Failed to apply migrations."
            exit 1
        fi
        echo "Migrations directory already exists and migrations applied."
    fi
}

# Initialize migrations directory if not exists
initialize_migrations

# Start the Gunicorn server
echo "Starting Gunicorn server..."
exec gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - xai_app:app
