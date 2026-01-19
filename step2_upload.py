import mysql.connector
import json
from my_secrets import DB_CONFIG

print("📂 Loading local vector file...")
try:
    with open("patient_vectors_dump.json", "r") as f:
        data = json.load(f)
    print(f"✅ Loaded {len(data)} ready-to-upload records.")
except FileNotFoundError:
    print("❌ Error: Run Step 1 first!")
    exit()

print("🔌 Connecting to TiDB Cloud...")
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("✅ Connected!")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    exit()

print("\n🚀 Uploading to Database...")
count = 0
for item in data:
    try:
        # 1. Check duplicate
        cursor.execute("SELECT id FROM patient_vectors WHERE patient_id = %s", (item['patient_id'],))
        if cursor.fetchone():
            print(f"⏩ Skipping {item['patient_id']} (Already exists)")
            continue

        # 2. Insert
        # Note: We dump the vector list to a JSON string for storage
        sql = "INSERT INTO patient_vectors (patient_id, story_text, vector_json) VALUES (%s, %s, %s)"
        cursor.execute(sql, (item['patient_id'], item['story'], json.dumps(item['vector'])))
        conn.commit()
        
        print(f"✅ Uploaded Patient {item['patient_id']}")
        count += 1
        
    except Exception as e:
        print(f"❌ DB Error on {item['patient_id']}: {e}")

conn.close()
print(f"\n🎉 PHASE 3 COMPLETE: {count} new records added to the Cloud DB.")