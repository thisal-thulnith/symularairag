#!/bin/sh
set -e

if [ -z "$(ls -A /app/vectorstore 2>/dev/null)" ]; then
  echo "Vectorstore empty — running ingestion..."
  python -m src.ingest
else
  echo "Vectorstore found — skipping ingestion."
fi

exec "$@"
