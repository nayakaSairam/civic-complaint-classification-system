#!/bin/sh

# Add the current directory to the PYTHONPATH
export PYTHONPATH="$PYTHONPATH:."

# Run database migrations/creation
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Start the Uvicorn server
uvicorn app.main:app --host 0.0.0.0 --port 10000
