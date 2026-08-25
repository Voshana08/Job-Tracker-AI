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
    "INSERT INTO applications (company, role, status) VALUES (?, ?, ?)",
    ("Atlassian", "Junior Developer", "Applied")
)

# repeat this a few more times with different fake data
cursor.execute(
    "INSERT INTO applications (company, role, status) VALUES (?, ?, ?)",
    ("Google", "Junior Developer", "Applied")
)
cursor.execute(
    "INSERT INTO applications (company, role, status) VALUES (?, ?, ?)",
    ("Microsoft", "Junior Developer", "Applied")
)
cursor.execute(
    "INSERT INTO applications (company, role, status) VALUES (?, ?, ?)",
    ("Apple", "Junior Developer", "Interview")
)
cursor.execute(
    "INSERT INTO applications (company, role, status) VALUES (?, ?, ?)",
    ("Monash", "Junior Developer", "Offer")
)
cursor.execute(
    "INSERT INTO applications (company, role, status) VALUES (?, ?, ?)",
    ("Yahoo", "Junior Developer", "Rejected")
)
cursor.execute(
    "INSERT INTO applications (company, role, status) VALUES (?, ?, ?)",
    ("Webx", "Junior Developer", "Offer")
)
cursor.execute(
    "INSERT INTO applications (company, role, status) VALUES (?, ?, ?)",
    ("Anthropic", "Junior Developer", "Offer")
)
conn.commit()
conn.close()