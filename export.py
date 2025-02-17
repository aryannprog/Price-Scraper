import sqlite3

# Connect to SQLite database (creates historical.db if it doesn't exist)
conn = sqlite3.connect("historical.db")
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS prices (
        SKU_CODE INT NOT NULL,
        Product_Description TEXT NOT NULL,
        Sales_Channel TEXT NOT NULL,
        Price REAL NOT NULL,
        Timestamp TEXT NOT NULL
    )
""")

# Commit and close
conn.commit()
conn.close()

print("✅ historical.db created successfully with the required table.")
