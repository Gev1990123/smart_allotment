import psycopg2
from psycopg2.extras import RealDictCursor
from config import settings

def get_connection():
    return psycopg2.connect(
        host=settings.PSQL_HOST,
        port=settings.PSQL_PORT,
        user=settings.PSQL_USER,
        password=settings.PSQL_PASS,
        dbname=settings.PSQL_DB,
        cursor_factory=RealDictCursor
    )
