from flask import Flask
import os
import psycopg2

application = Flask(__name__)

def conn_info():
    return {
        "host": os.environ["DB_HOST"],
        "port": int(os.environ.get("DB_PORT", "5432")),
        "database": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASS"]
    }

def seed_if_needed():
    """Create the table if it doesn't exist and insert seed rows only once."""
    conn = psycopg2.connect(**conn_info())
    cur = conn.cursor()
    # Create table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    # Check if table is empty
    cur.execute("SELECT COUNT(*) FROM messages;")
    (count,) = cur.fetchone()
    if count == 0:
        # Insert seed data only if empty
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
    conn = psycopg2.connect(**conn_info())
    cur = conn.cursor()
    cur.execute("SELECT content, created_at FROM messages ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@application.route("/")
def index():
    # Ensure seed happened before display
    seed_if_needed()

    rows = fetch_messages()
    html = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'><title>Messages</title></head>",
        "<body style='font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; padding:24px;'>",
        "<h1>Messages</h1>",
        "<ul>"
    ]
    for content, created_at in rows:
        html.append(f"<li>{content} <small style='color:#666;'>({created_at})</small></li>")
    html.append("</ul>")
    html.append("</body></html>")
    return "\n".join(html)

if __name__ == "__main__":
    # Local run convenience. EB uses gunicorn via Procfile.
    application.run(host="0.0.0.0", port=5000, debug=True)
