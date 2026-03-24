from flask import Flask
import os
import psycopg2

# Elastic Beanstalk expects this object to be named "application"
application = Flask(__name__)

# ---------- Database helpers ----------

def conn_info():
    return {
        "host": os.environ["DB_HOST"],
        "port": int(os.environ.get("DB_PORT", "5432")),
        "database": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASS"],
    }

def get_connection():
    return psycopg2.connect(**conn_info())

def seed_if_needed():
    """
    Create the table if it doesn't exist and insert seed rows only once.
    Safe to call multiple times.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("SELECT COUNT(*) FROM messages;")
    (count,) = cur.fetchone()

    if count == 0:
        cur.execute("""
            INSERT INTO messages (content) VALUES
              ('Welcome to the Implementation app'),
              ('Seeded data stored in Amazon RDS (PostgreSQL)'),
              ('Rendered by a tiny Flask app');
        """)

    conn.commit()
    cur.close()
    conn.close()

def fetch_messages():

