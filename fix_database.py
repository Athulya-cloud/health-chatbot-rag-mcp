import mysql.connector
import json
from my_secrets import DB_CONFIG

print("🔧 Starting Database Repair (JSON Mode)...")

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# 1. Drop old table
print("💥 Dropping old table...")
cursor.execute("DROP TABLE IF EXISTS patient_vectors;")

# 2. Create Simple Table (No "VECTOR" keyword to break things)
print("🔨 Creating new table with JSON storage...")
cursor.execute("""
    CREATE TABLE patient_vectors (
        id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id VARCHAR(255),
        story_text TEXT,
        vector_json JSON  -- Using standard JSON type
    );
""")

# 3. Reload Data
print("📂 Reloading data from 'patient_vectors_dump.json'...")
try:
    with open("patient_vectors_dump.json", "r") as f:
        data = json.load(f)
        
    for item in data:
        # Note: We dump the list to a string for storage
        sql = "INSERT INTO patient_vectors (patient_id, story_text, vector_json) VALUES (%s, %s, %s)"
        cursor.execute(sql, (item['patient_id'], item['story'], json.dumps(item['vector'])))
        conn.commit()
    print(f"✅ Successfully restored {len(data)} records.")

except Exception as e:
    print(f"❌ Error reloading data: {e}")

conn.close()
print("🎉 REPAIR COMPLETE. Database is ready.")