import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

STATES = ("OPEN", "IN_PROGRESS", "RESOLVED")
NEXT_STATES = {"OPEN": ("OPEN", "IN_PROGRESS"), "IN_PROGRESS": ("IN_PROGRESS", "RESOLVED"), "RESOLVED": ("RESOLVED",)}


class ConflictError(Exception):
    pass


def validate_change(current, status, note):
    if status not in STATES:
        raise ValueError("处理状态无效。")
    if status not in NEXT_STATES.get(current, ()):
        raise ValueError("请按待处理、处理中、已解决的顺序更新，不能跳过或退回。")
    if not isinstance(note, str) or not note.strip():
        raise ValueError("请填写跟进备注。")
    if len(note.strip()) > 1000:
        raise ValueError("跟进备注不能超过1000字。")
    return note.strip()


class FollowUpStore:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS followups (
                exception_id TEXT PRIMARY KEY,
                handling_status TEXT NOT NULL CHECK(handling_status IN ('OPEN','IN_PROGRESS','RESOLVED')),
                follow_up_note TEXT NOT NULL,
                updated_at TEXT NOT NULL)""")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def overlay(self, rows):
        with self.connect() as db:
            saved = {r['exception_id']: dict(r) for r in db.execute("SELECT * FROM followups")}
        result = []
        for original in rows:
            row = dict(original)
            row['source_handling_status'] = row['handling_status']
            row['saved_locally'] = row['exception_id'] in saved
            row['local_updated_at'] = None
            if row['saved_locally']:
                local = saved[row['exception_id']]
                row.update(handling_status=local['handling_status'], follow_up_note=local['follow_up_note'], local_updated_at=local['updated_at'])
            result.append(row)
        return result

    def save(self, source, status, note, expected_status):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            local = db.execute("SELECT handling_status FROM followups WHERE exception_id=?", (source['exception_id'],)).fetchone()
            current = local['handling_status'] if local else source['handling_status']
            if expected_status != current:
                raise ConflictError("记录状态已变化，请重新读取后再保存。")
            clean_note = validate_change(current, status, note)
            updated = datetime.now(timezone.utc).isoformat()
            db.execute("""INSERT INTO followups VALUES (?,?,?,?)
                ON CONFLICT(exception_id) DO UPDATE SET
                handling_status=excluded.handling_status,follow_up_note=excluded.follow_up_note,updated_at=excluded.updated_at""",
                (source['exception_id'], status, clean_note, updated))
        return self.overlay([source])[0]
