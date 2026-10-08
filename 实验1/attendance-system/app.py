"""A small local attendance system for software engineering lab 1."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, url_for


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("ATTENDANCE_SECRET_KEY", "local-lab-demo-key"),
        DATABASE=Path(app.instance_path) / "attendance.sqlite3",
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    def get_db() -> sqlite3.Connection:
        if "db" not in g:
            database = Path(app.config["DATABASE"])
            database.parent.mkdir(parents=True, exist_ok=True)
            g.db = sqlite3.connect(database)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(_error: BaseException | None) -> None:
        db = g.pop("db", None)
        if db is not None:
            db.close()

    with app.app_context():
        db = get_db()
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL REFERENCES events(id),
                student_id TEXT NOT NULL,
                name TEXT NOT NULL,
                checked_in_at TEXT NOT NULL
            );
            """
        )
        db.commit()

    @app.get("/")
    def index():
        events = get_db().execute(
            """
            SELECT e.id, e.title, e.created_at, COUNT(c.id) AS checkin_count
            FROM events AS e LEFT JOIN checkins AS c ON c.event_id = e.id
            GROUP BY e.id ORDER BY e.id DESC
            """
        ).fetchall()
        return render_template("index.html", events=events)

    @app.post("/events")
    def create_event():
        title = request.form.get("title", "").strip()
        if not title or len(title) > 80:
            flash("活动名称须为 1 至 80 个字符。", "error")
            return redirect(url_for("index"))
        now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
        db = get_db()
        cursor = db.execute("INSERT INTO events (title, created_at) VALUES (?, ?)", (title, now))
        db.commit()
        flash("签到活动已创建。", "success")
        return redirect(url_for("event_detail", event_id=cursor.lastrowid))

    @app.get("/events/<int:event_id>")
    def event_detail(event_id: int):
        db = get_db()
        event = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
        if event is None:
            abort(404)
        checkins = db.execute(
            "SELECT student_id, name, checked_in_at FROM checkins WHERE event_id = ? ORDER BY id DESC",
            (event_id,),
        ).fetchall()
        return render_template("event.html", event=event, checkins=checkins)

    @app.post("/events/<int:event_id>/checkin")
    def checkin(event_id: int):
        db = get_db()
        event = db.execute("SELECT id FROM events WHERE id = ?", (event_id,)).fetchone()
        if event is None:
            abort(404)
        student_id = request.form.get("student_id", "").strip()
        name = request.form.get("name", "").strip()
        if not (1 <= len(student_id) <= 30 and 1 <= len(name) <= 30):
            flash("学号和姓名均须为 1 至 30 个字符。", "error")
            return redirect(url_for("event_detail", event_id=event_id))
        now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
        db.execute(
            "INSERT INTO checkins (event_id, student_id, name, checked_in_at) VALUES (?, ?, ?, ?)",
            (event_id, student_id, name, now),
        )
        db.commit()
        flash("签到成功。", "success")
        return redirect(url_for("event_detail", event_id=event_id))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
