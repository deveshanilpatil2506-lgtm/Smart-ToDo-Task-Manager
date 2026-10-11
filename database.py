
import sqlite3

DB_NAME = "todo.db"


def update_task(task_id, title, priority, deadline):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET title = ?, priority = ?, deadline = ?
            WHERE id = ?
            """,
            (title, priority, deadline, task_id)
        )


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
        """)

        columns = [
            row[1]
            for row in conn.execute("PRAGMA table_info(tasks)")
        ]

        if "priority" not in columns:
            conn.execute("""
                ALTER TABLE tasks
                ADD COLUMN priority TEXT NOT NULL DEFAULT 'Medium'
            """)

        if "deadline" not in columns:
            conn.execute("""
                ALTER TABLE tasks
                ADD COLUMN deadline TEXT NOT NULL DEFAULT ''
            """)


def add_task(title, priority="Medium", deadline=""):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO tasks (title, priority, deadline)
               VALUES (?, ?, ?)""",
            (title, priority, deadline)
        )


def get_tasks():
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT id, title, completed, priority, deadline
            FROM tasks
            ORDER BY id ASC
        """)
        return cursor.fetchall()


def complete_task(task_id):
    with get_connection() as conn:
        conn.execute(
            "UPDATE tasks SET completed = 1 WHERE id = ?",
            (task_id,)
        )


def delete_task(task_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

