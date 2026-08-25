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
    "INSERT INTO applications (company, role, status,date_applied) VALUES (?, ?, ?,?)",
    ("Atlassian", "Junior Developer", "Applied","12-08-2026")
)

# repeat this a few more times with different fake data
cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied) VALUES (?, ?, ?,?)",
    ("Google", "Junior Developer", "Applied","23-08-2026")
)
cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied) VALUES (?, ?, ?,?)",
    ("Microsoft", "Junior Developer", "Applied","25-08-2026")
)
cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied) VALUES (?, ?, ?,?)",
    ("Apple", "Junior Developer", "Interview","17-08-2026")
)
cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied) VALUES (?, ?, ?,?)",
    ("Monash", "Junior Developer", "Interview","17-08-2026")
)
cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied) VALUES (?, ?, ?,?)",
    ("Yahoo", "Junior Developer", "Rejected","17-08-2026")
)
cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied) VALUES (?, ?, ?,?)",
    ("Webx", "Junior Developer", "Interview","19-08-2026")
)
cursor.execute(
    "INSERT INTO applications (company, role, status,date_applied) VALUES (?, ?, ?,?)",
    ("Anthropic", "Junior Developer", "Offer","21-08-2026")
)
conn.commit()
conn.close()