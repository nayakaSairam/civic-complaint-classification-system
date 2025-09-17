#!/bin/sh

# Run database migrations/creation
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Start the Uvicorn server, explicitly pointing to the app directory
uvicorn main:app --app-dir app --host 0.0.0.0 --port 10000