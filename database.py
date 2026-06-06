import sqlite3
from datetime import datetime

DB = 'wisdom_library.db'

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with conn() as c:
        c.executescript('''
            CREATE TABLE IF NOT EXISTS students (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT    NOT NULL,
                seat    INTEGER NOT NULL UNIQUE,
                fees    REAL    NOT NULL,
                phone   TEXT    DEFAULT '',
                shift   TEXT    DEFAULT 'Full Day',
                plan    TEXT    DEFAULT 'Monthly',
                note    TEXT    DEFAULT '',
                joined  TEXT    DEFAULT (date('now'))
            );

            CREATE TABLE IF NOT EXISTS attendance (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date       TEXT    NOT NULL,
                status     TEXT    NOT NULL DEFAULT 'absent',
                UNIQUE(student_id, date),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS fees (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                month      TEXT    NOT NULL,
                status     TEXT    NOT NULL DEFAULT 'pending',
                paid_on    TEXT,
                UNIQUE(student_id, month),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );
        ''')

# ─── Students ─────────────────────────────────────────────────
def row_to_dict(row):
    return dict(row) if row else None

def get_all_students():
    with conn() as c:
        rows = c.execute('SELECT * FROM students ORDER BY seat').fetchall()
        return [dict(r) for r in rows]

def seat_taken(seat, exclude_id=None):
    with conn() as c:
        if exclude_id:
            r = c.execute('SELECT id FROM students WHERE seat=? AND id!=?', (seat, exclude_id)).fetchone()
        else:
            r = c.execute('SELECT id FROM students WHERE seat=?', (seat,)).fetchone()
        return r is not None

def add_student(name, seat, fees, phone, shift, plan, note):
    joined = datetime.now().strftime('%d %b %Y')
    with conn() as c:
        cur = c.execute(
            'INSERT INTO students (name,seat,fees,phone,shift,plan,note,joined) VALUES (?,?,?,?,?,?,?,?)',
            (name, seat, fees, phone, shift, plan, note, joined)
        )
        return row_to_dict(c.execute('SELECT * FROM students WHERE id=?', (cur.lastrowid,)).fetchone())

def update_student(sid, data):
    fields = ['name','seat','fees','phone','shift','plan','note']
    updates = {k: data[k] for k in fields if k in data}
    if not updates:
        return None
    set_clause = ', '.join(f'{k}=?' for k in updates)
    vals = list(updates.values()) + [sid]
    with conn() as c:
        c.execute(f'UPDATE students SET {set_clause} WHERE id=?', vals)
        return row_to_dict(c.execute('SELECT * FROM students WHERE id=?', (sid,)).fetchone())

def delete_student(sid):
    with conn() as c:
        c.execute('DELETE FROM students WHERE id=?', (sid,))

# ─── Attendance ────────────────────────────────────────────────
def get_attendance(date):
    with conn() as c:
        rows = c.execute('SELECT * FROM attendance WHERE date=?', (date,)).fetchall()
        return {str(r['student_id']): r['status'] for r in rows}

def mark_attendance(student_id, date, status):
    with conn() as c:
        c.execute('''
            INSERT INTO attendance (student_id, date, status) VALUES (?,?,?)
            ON CONFLICT(student_id, date) DO UPDATE SET status=excluded.status
        ''', (student_id, date, status))
        return {'student_id': student_id, 'date': date, 'status': status}

def bulk_mark_attendance(student_ids, date, status):
    with conn() as c:
        for sid in student_ids:
            c.execute('''
                INSERT INTO attendance (student_id, date, status) VALUES (?,?,?)
                ON CONFLICT(student_id, date) DO UPDATE SET status=excluded.status
            ''', (sid, date, status))

# ─── Fees ──────────────────────────────────────────────────────
def get_fees(month):
    with conn() as c:
        rows = c.execute('SELECT * FROM fees WHERE month=?', (month,)).fetchall()
        return {str(r['student_id']): r['status'] for r in rows}

def update_fee(student_id, month, status):
    paid_on = datetime.now().strftime('%d %b %Y') if status == 'paid' else None
    with conn() as c:
        c.execute('''
            INSERT INTO fees (student_id, month, status, paid_on) VALUES (?,?,?,?)
            ON CONFLICT(student_id, month) DO UPDATE SET status=excluded.status, paid_on=excluded.paid_on
        ''', (student_id, month, status, paid_on))
        return {'student_id': student_id, 'month': month, 'status': status}

# ─── Stats ────────────────────────────────────────────────────
def get_stats(date, month):
    with conn() as c:
        total = c.execute('SELECT COUNT(*) FROM students').fetchone()[0]
        present = c.execute(
            "SELECT COUNT(*) FROM attendance WHERE date=? AND status='present'", (date,)
        ).fetchone()[0]
        pending_count = total - c.execute(
            "SELECT COUNT(*) FROM fees WHERE month=? AND status='paid'", (month,)
        ).fetchone()[0]
        pending_amt = c.execute(
            '''SELECT COALESCE(SUM(s.fees),0) FROM students s
               WHERE s.id NOT IN (SELECT student_id FROM fees WHERE month=? AND status='paid')''',
            (month,)
        ).fetchone()[0]
        collected = c.execute(
            '''SELECT COALESCE(SUM(s.fees),0) FROM students s
               JOIN fees f ON f.student_id=s.id
               WHERE f.month=? AND f.status='paid' ''',
            (month,)
        ).fetchone()[0]
        free_seats = 53 - total
        return {
            'total_students': total,
            'free_seats': free_seats,
            'present_today': present,
            'fees_pending_count': pending_count,
            'fees_pending_amt': pending_amt,
            'fees_collected': collected
        }