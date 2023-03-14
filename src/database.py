import sqlite3
from flask import g

DATABASE = 'mydatabase.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with open('schema.sql') as f:
        db = get_db()
        db.executescript(f.read())
        db.commit()
