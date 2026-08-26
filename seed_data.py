#This is just a test file for us to insert and change data on the database when needed to.
#The logic to understand this is given below.
#applications.db = a shared Google Doc

# app.py       → opens the doc, reads from it
# database.py  → opened the doc once, set up the 
#                 page structure/headings
# seed_data.py → opens the SAME doc, types some content into it
import sqlite3

conn = sqlite3.connect('applications.db')   # ← same filename as always
cursor = conn.cursor()

cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied,status_updated_at) VALUES (?, ?, ?,?,?)",
    ("Atlassian", "Junior Developer", "Applied","2026-08-09","2026-08-23")
)

# repeat this a few more times with different fake data
cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied,status_updated_at) VALUES (?, ?, ?,?,?)",
    ("Google", "Junior Developer", "Applied","2026-08-25","2026-08-25")
)
cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied,status_updated_at) VALUES (?, ?, ?,?,?)",
    ("Microsoft", "Junior Developer", "Applied","2026-08-24","2026-08-25")
)
cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied,status_updated_at) VALUES (?, ?, ?,?,?)",
    ("Apple", "Junior Developer", "Interview","2026-08-14","2026-08-23")
)
cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied,status_updated_at) VALUES (?, ?, ?,?,?)",
    ("Monash", "Junior Developer", "Interview","2026-08-11","2026-08-22")
)
cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied,status_updated_at) VALUES (?, ?, ?,?,?)",
    ("Yahoo", "Junior Developer", "Rejected","2026-08-23","2026-08-24")
)
cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied,status_updated_at) VALUES (?, ?, ?,?,?)",
    ("Webx", "Junior Developer", "Interview","2026-08-22","2026-08-24")
)
cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied,status_updated_at) VALUES (?, ?, ?,?,?)",
    ("Anthropic", "Junior Developer", "Offer","2026-08-16","2026-08-23")
)

cursor.execute(
    "INSERT INTO users (username,password) VALUES (?, ?)",
    ("Voshana", "Test0")
)

cursor.execute(
    "INSERT INTO users (username,password) VALUES (?, ?)",
    ( "Nissanka", "Test1")
)

cursor.execute(
    "INSERT INTO users (username,password) VALUES (?, ?)",
    ( "VN1", "Test2")
)

cursor.execute(
    "INSERT INTO users (username,password) VALUES (?, ?)",
    ( "VN2", "Test3")
)
conn.commit()
conn.close()