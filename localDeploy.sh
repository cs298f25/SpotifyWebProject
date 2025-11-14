#!/bin/bash

# Source the virtual environment script (activates venv)
source ./virtualEnvironment.sh

# Install redis
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install redis

# Start Redis in the background (so the script continues)
redis-server --daemonize yes

# Wait for Redis to be ready
until redis-cli ping &>/dev/null; do
  sleep 0.1
done

# Run the Flask application
python3 src/app.py