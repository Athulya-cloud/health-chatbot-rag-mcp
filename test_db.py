import mysql.connector
from secrets import DB_CONFIG

print("🔌 Attempting to connect to TiDB Cloud...")

try:
    # 1. Connect
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 2. Test Query
    cursor.execute("SELECT 1;")
    result = cursor.fetchone()
    print(f"✅ CONNECTION SUCCESS! Database responded: {result[0]}")
    
    # 3. Create the Table (So we don't have to do it later)
    print("🔨 Creating 'patient_vectors' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_vectors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id VARCHAR(50),
            story_text TEXT,
            vector_json JSON 
        );
    """)
    print("✅ Table 'patient_vectors' is ready.")
    
    conn.close()

except Exception as e:
    print(f"❌ CONNECTION FAILED: {e}")
    print("👉 Common Fixes:")
    print("1. Did you copy the password correctly?")
    print("2. Is your IP allowed? (TiDB usually allows all IPs by default)")
    print("3. Check 'ssl_disabled=True' in secrets.py")