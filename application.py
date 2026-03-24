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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT content, created_at FROM messages ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# ---------- Routes ----------

@application.route("/")
def health():
    return "Application started successfully"

@application.route("/messages")
def messages():
    seed_if_needed()
    rows = fetch_messages()

    html = [
        "<!doctype html>",
        "<html>",
        "<head><meta charset='utf-8'><title>Messages</title></head>",
        "<body style='font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; padding:24px;'>",
        "<h1>Messages</h1>",
        "<ul>"
    ]

    for content, created_at in rows:
        html.append(
            f"<li>{content} "
            f"<small style='color:#666;'>({created_at})</small></li>"
        )

    html.extend(["</ul>", "</body>", "</html>"])
    return "\n".join(html)

# ---------- Local development only ----------

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=True)

