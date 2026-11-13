"""Same check as check_setup.py, using pg8000 (pure Python) instead of psycopg.

Use it when psycopg-binary cannot load (e.g. Windows Smart App Control blocks its DLL).
Read-only: connects, checks the pgvector extension, prints versions.
"""
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import pg8000.native
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / '.env')
url = os.getenv('DATABASE_URL')
if not url:
    sys.exit('DATABASE_URL missing: copy starter/.env.example to starter/.env first.')
u = urlparse(url)
try:
    connection = pg8000.native.Connection(
        user=u.username, password=u.password, host=u.hostname,
        port=u.port or 5432, database=u.path.lstrip('/'), timeout=5)
    row = connection.run(
        "SELECT current_database(), current_setting('server_version'), extversion "
        "FROM pg_extension WHERE extname = 'vector'")
    connection.close()
except Exception as exc:
    sys.exit(f'Database connection failed ({type(exc).__name__}). Check Docker, port and DATABASE_URL in starter/.env.')
if not row:
    sys.exit('Connected, but pgvector extension is missing. See starter/README.md.')
print(f'Database: {row[0][0]} | PostgreSQL: {row[0][1]} | pgvector: {row[0][2]}')
print('Setup OK (pg8000).')
