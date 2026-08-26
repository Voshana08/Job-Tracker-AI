import sqlite3

def init_db():
    conn = sqlite3.connect('applications.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            role TEXT,
            job_description TEXT,
            resume_filename TEXT,
            status TEXT,
            date_applied TIMESTAMP,
            match_score INTEGER,
            missing_keywords TEXT,
            notes TEXT,
            status_updated_at TEXT,
            created_at TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database created successfully!")