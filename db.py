import sqlite3
from misc import db_name

db_connection = sqlite3.connect(db_name)
db_cursor = db_connection.cursor()

def init_db():
    db_cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER UNIQUE, first_name TEXT, last_name TEXT, username TEXT, date TEXT, is_admin INTEGER DEFAULT 0, nominal_name TEXT, admin_by INTEGER REFERENCES users (chat_id))")
    db_cursor.execute("CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY AUTOINCREMENT, question_text TEXT, question_answers TEXT, question_text_ent TEXT)")
    db_cursor.execute("CREATE TABLE IF NOT EXISTS answers (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER REFERENCES users (chat_id), question_id INTEGER REFERENCES questions (id), answer TEXT)")
    db_cursor.execute("CREATE TABLE IF NOT EXISTS content (id INTEGER PRIMARY KEY AUTOINCREMENT, content_text TEXT, content_text_ent TEXT, content_photo TEXT, content_video TEXT, content_audio TEXT, content_document TEXT, published INTEGER DEFAULT 0, published_date TEXT, published_by INTEGER REFERENCES users (chat_id))")
    db_connection.commit()
    db_cursor.close()
    print ("Database initialized")