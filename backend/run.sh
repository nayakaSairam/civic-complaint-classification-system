#!/usr/bin/env bash
set -e
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
uvicorn server:app --host 0.0.0.0 --port 10000