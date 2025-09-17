#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Run database creation
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

# Start the Uvicorn server, pointing to the server.py file
uvicorn server:app --host 0.0.0.0 --port 10000