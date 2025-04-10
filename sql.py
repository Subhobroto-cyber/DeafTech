import sqlite3
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')
conn.commit()
c.execute("SELECT * FROM users")
rows = c.fetchall()
for row in rows:
    print(row)
conn.close()
