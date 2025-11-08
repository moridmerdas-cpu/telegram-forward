import sqlite3
import time

class DB:
    def __init__(self, path='data.db'):
        self.con = sqlite3.connect(path, check_same_thread=False)
        self.cur = self.con.cursor()
        self._init_tables()

    def _init_tables(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT,
            subscription_start INTEGER,
            subscription_end INTEGER
        )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            title TEXT,
            owner_telegram_id INTEGER
        )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_telegram_id INTEGER,
            channel_username TEXT,
            channel_message_id INTEGER,
            created_at INTEGER,
            status TEXT
        )""")
        self.con.commit()

    def add_user(self, telegram_id, username=None):
        self.cur.execute("INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)", (telegram_id, username))
        self.con.commit()

    def set_subscription(self, telegram_id, months=0, weeks=0, days=0):
        now = int(time.time())
        add_seconds = months*30*24*3600 + weeks*7*24*3600 + days*24*3600
        row = self.cur.execute("SELECT subscription_end FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()
        if row and row[0]:
            current_end = row[0]
            if current_end > now:
                new_end = current_end + add_seconds
            else:
                new_end = now + add_seconds
        else:
            new_end = now + add_seconds
        self.cur.execute("UPDATE users SET subscription_start=?, subscription_end=? WHERE telegram_id=?", (now, new_end, telegram_id))
        self.con.commit()

    def get_subscription(self, telegram_id):
        row = self.cur.execute("SELECT subscription_start, subscription_end FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()
        if not row:
            return None
        start, end = row
        return {'start': start, 'end': end}

    def is_subscribed(self, telegram_id):
        row = self.cur.execute("SELECT subscription_end FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()
        if not row or not row[0]:
            return False
        import time
        return int(time.time()) < row[0]

    def add_group(self, telegram_id, title, owner_telegram_id):
        self.cur.execute("INSERT INTO groups (telegram_id, title, owner_telegram_id) VALUES (?, ?, ?)", (telegram_id, title, owner_telegram_id))
        self.con.commit()

    def list_groups(self, owner_telegram_id):
        rows = self.cur.execute("SELECT telegram_id, title FROM groups WHERE owner_telegram_id=?", (owner_telegram_id,)).fetchall()
        return [{'telegram_id': r[0], 'title': r[1]} for r in rows]

    def remove_group(self, telegram_id, owner_telegram_id):
        self.cur.execute("DELETE FROM groups WHERE telegram_id=? AND owner_telegram_id=?", (telegram_id, owner_telegram_id))
        self.con.commit()

    def create_job(self, owner_telegram_id, channel_username, channel_message_id):
        now = int(time.time())
        self.cur.execute("INSERT INTO jobs (owner_telegram_id, channel_username, channel_message_id, created_at, status) VALUES (?, ?, ?, ?, ?)", (owner_telegram_id, channel_username, channel_message_id, now, 'pending'))
        self.con.commit()
        return self.cur.lastrowid

    def list_jobs(self, owner_telegram_id):
        rows = self.cur.execute("SELECT id, channel_username, channel_message_id, created_at, status FROM jobs WHERE owner_telegram_id=?", (owner_telegram_id,)).fetchall()
        return [{'id': r[0], 'channel': r[1], 'msg_id': r[2], 'created_at': r[3], 'status': r[4]} for r in rows]
