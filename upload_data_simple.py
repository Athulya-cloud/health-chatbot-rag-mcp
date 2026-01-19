import pandas as pd
import mysql.connector
import json
import time
from google import genai
from my_secrets import DB_CONFIG, GOOGLE_KEY

client = genai.Client(api_key=GOOGLE_KEY)

print("📂 Loading files...")
df_pat = pd.read_csv('dataset_healthchatbot/PatientCorePopulatedTable.txt', sep='\t')
df_diag = pd.read_csv('dataset_healthchatbot/AdmissionsDiagnosesCorePopulatedTable.txt', sep='\t')
merged = pd.merge(df_pat, df_diag, on='PatientID', how='inner')
print(f"✅ Merged {len(merged)} records")

sample = merged.head(5)  # Just 5 for testing

print("🚀 Uploading to database...")
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

for idx, row in sample.iterrows():
    pid = str(row['PatientID'])
    story = f"Patient {pid} is a {row['PatientRace']} {row['PatientGender']} born {row['PatientDateOfBirth']}. Diagnosis: {row['PrimaryDiagnosisDescription']}."
    
    try:
        # Check if exists
        cursor.execute("SELECT id FROM patient_vectors WHERE patient_id = %s", (pid,))
        if cursor.fetchone():
            print(f"⏩ {pid} already exists")
            continue
        
        # Get embedding
        print(f"🧠 Embedding {pid}...")
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
        print(f"✅ Saved {pid} ({len(vector)} dimensions)")
        time.sleep(1)
        
    except Exception as e:
        print(f"❌ Error: {e}")

conn.close()
print("✅ Upload complete!")
