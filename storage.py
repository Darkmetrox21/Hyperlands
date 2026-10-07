import sqlite3, hashlib
from datetime import datetime, timezone
from pathlib import Path

class Store:
    def __init__(self,path):
        self.path=str(path)
        Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS responses (
            token_id TEXT PRIMARY KEY, name TEXT NOT NULL, role TEXT NOT NULL,
            status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")
    def connect(self):
        c=sqlite3.connect(self.path,timeout=15)
        c.row_factory=sqlite3.Row
        return c
    def register(self,token,data):
        tid=hashlib.sha256(token.encode()).hexdigest()
        now=datetime.now(timezone.utc).isoformat(timespec='seconds')
        with self.connect() as c:
            c.execute('INSERT OR IGNORE INTO responses VALUES (?,?,?,?,?,?)',
                      (tid,data['name'],data.get('role','Habitante fundador'),'pendiente',now,now))
        return tid
    def get(self,tid):
        with self.connect() as c:
            row=c.execute('SELECT * FROM responses WHERE token_id=?',(tid,)).fetchone()
            return dict(row) if row else None
    def respond(self,tid,status):
        if status not in ('aceptada','declinada'): raise ValueError('Estado inválido')
        now=datetime.now(timezone.utc).isoformat(timespec='seconds')
        with self.connect() as c:
            result=c.execute('UPDATE responses SET status=?,updated_at=? WHERE token_id=?',(status,now,tid))
            if result.rowcount!=1: raise ValueError('Invitación no registrada')
    def all(self):
        with self.connect() as c:
            return [dict(r) for r in c.execute('SELECT * FROM responses ORDER BY created_at DESC')]
