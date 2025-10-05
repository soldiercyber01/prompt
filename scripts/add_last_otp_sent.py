"""Simple helper to add last_otp_sent column to the `user` table if missing.

Run from the project root with your venv active:

    python scripts/add_last_otp_sent.py

This uses the app's SQLALCHEMY_DATABASE_URI and will operate on the same database.
"""
from sqlalchemy import text
from app import app
from extensions import db

with app.app_context():
    with db.engine.connect() as conn:
        # Check if column exists in the current database
        check_sql = text("""
            SELECT COUNT(*) AS cnt
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'user'
              AND COLUMN_NAME = 'last_otp_sent'
        """)
        res = conn.execute(check_sql)
        cnt = res.scalar() if hasattr(res, 'scalar') else list(res)[0][0]
        if cnt and int(cnt) > 0:
            print("Column 'last_otp_sent' already exists. No action taken.")
        else:
            print("Adding column 'last_otp_sent' to table 'user'...")
            alter_sql = text("ALTER TABLE `user` ADD COLUMN last_otp_sent DATETIME NULL;")
            conn.execute(alter_sql)
            print("Column added successfully.")
