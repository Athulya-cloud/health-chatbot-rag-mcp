import pandas as pd
import mysql.connector
import json
import time
from google import genai
from my_secrets import DB_CONFIG, GOOGLE_KEY

print("📂 Loading files...")
df_pat = pd.read_csv('dataset_healthchatbot/PatientCorePopulatedTable.txt', sep='\t')
df_diag = pd.read_csv('dataset_healthchatbot/AdmissionsDiagnosesCorePopulatedTable.txt', sep='\t')
merged = pd.merge(df_pat, df_diag, on='PatientID', how='inner')
print(f"✅ Merged {len(merged)} records\n")

sample = merged.head(5)

print("🚀 Uploading to database...\n")

success = 0
for idx, row in sample.iterrows():
    pid = str(row['PatientID'])
    print(f"[{idx+1}] Patient {pid}...", end=" ", flush=True)
    
    try:
        story = f"Patient {pid} is a {row['PatientRace']} {row['PatientGender']} born {row['PatientDateOfBirth']}. Diagnosis: {row['PrimaryDiagnosisDescription']}."
        
        # Fresh connection for each iteration
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute("SELECT id FROM patient_vectors WHERE patient_id = %s", (pid,))
        if cursor.fetchone():
            print("⏩ Already in DB")
            conn.close()
            continue
        
        # Get embedding
        client = genai.Client(api_key=GOOGLE_KEY)
        res = client.models.embed_content(
            model="models/text-embedding-004",
            contents=story
        )
        vector = list(res.embeddings[0].values)
        
        # Save to DB
        cursor.execute(
            "INSERT INTO patient_vectors (patient_id, story_text, vector_json) VALUES (%s, %s, %s)",
            (pid, story, json.dumps(vector))
        )
        conn.commit()
        conn.close()
        
        print("✅ Saved")
        success += 1
        time.sleep(1)
        
    except Exception as e:
        print(f"❌ {e}")
        try:
            conn.close()
        except:
            pass

print(f"\n✅ Saved {success} records!")