import sqlite3

def init_db():
    conn = sqlite3.connect('applications.db')   # your db filename
    cursor = conn.cursor()            # get the cursor
    
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
            created_at TIMESTAMP
        )
    '''
    )
    conn.commit()   # save it
    conn.close()   # close it

if __name__ == '__main__':
    init_db()
    print("Database created successfully!")