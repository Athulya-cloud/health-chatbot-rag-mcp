import pandas as pd
import mysql.connector
import json
import time
from google import genai
from my_secrets import DB_CONFIG, GOOGLE_KEY
import traceback
import sys

client = genai.Client(api_key=GOOGLE_KEY)

print("📂 Loading files...")
try:
    df_pat = pd.read_csv('dataset_healthchatbot/PatientCorePopulatedTable.txt', sep='\t')
    df_diag = pd.read_csv('dataset_healthchatbot/AdmissionsDiagnosesCorePopulatedTable.txt', sep='\t')
    merged = pd.merge(df_pat, df_diag, on='PatientID', how='inner')
    print(f"✅ Merged {len(merged)} records\n")
except Exception as e:
    print(f"❌ Failed to load files: {e}")
    traceback.print_exc()
    sys.exit(1)

sample = merged.head(5)
print("🚀 Uploading to database...\n")

# Test embedding first
print("TEST: Trying one embedding...")
try:
    test_story = "Patient 001 is a male born 1980. Diagnosis: Hypertension."
    print(f"Calling API with: {test_story[:50]}...")
    res = client.models.embed_content(
        model="models/text-embedding-004",
        contents=test_story
    )
    print(f"✅ Embedding successful! Got {len(res.embeddings[0].values)} dimensions\n")
except Exception as e:
    print(f"❌ Embedding FAILED: {e}")
    traceback.print_exc()
    print("\n⚠️ Cannot continue without working embeddings")
    sys.exit(1)

# Now try to upload
try:
    print("Connecting to database...")
    conn = mysql.connector.connect(
        **DB_CONFIG,
        connection_timeout=10,
        autocommit=False
    )
    cursor = conn.cursor()
    print("✅ Connected to database\n")
except Exception as e:
    print(f"❌ DB connection failed: {e}")
    traceback.print_exc()
    sys.exit(1)

success = 0
failed = 0

for idx, row in sample.iterrows():
    pid = str(row['PatientID'])
    print(f"\n[{idx+1}/5] Processing Patient {pid}...")
    
    try:
        story = f"Patient {pid} is a {row['PatientRace']} {row['PatientGender']} born {row['PatientDateOfBirth']}. Diagnosis: {row['PrimaryDiagnosisDescription']}."
        
        # Check if exists
        cursor.execute("SELECT id FROM patient_vectors WHERE patient_id = %s", (pid,))
        if cursor.fetchone():
            print(f"  ⏩ Already in DB, skipping")
            continue
        
        # Get embedding
        print(f"  🧠 Getting embedding...")
        res = client.models.embed_content(
            model="models/text-embedding-004",
            contents=story
        )
        vector = list(res.embeddings[0].values)
        print(f"  ✅ Got embedding ({len(vector)} dims)")
        
        # Save to DB
        print(f"  💾 Saving to database...")
        cursor.execute(
            "INSERT INTO patient_vectors (patient_id, story_text, vector_json) VALUES (%s, %s, %s)",
            (pid, story, json.dumps(vector))
        )
        conn.commit()
        print(f"  ✅ SAVED")
        success += 1
        time.sleep(1)
        
    except Exception as e:
        failed += 1
        print(f"  ❌ ERROR: {e}")
        traceback.print_exc()
        time.sleep(2)

conn.close()
print(f"\n🎉 Complete! Saved: {success}, Failed: {failed}")
