import pandas as pd
import json
from google import genai
from my_secrets import GOOGLE_KEY

print("📂 Loading files...")
df_pat = pd.read_csv('dataset_healthchatbot/PatientCorePopulatedTable.txt', sep='\t')
df_diag = pd.read_csv('dataset_healthchatbot/AdmissionsDiagnosesCorePopulatedTable.txt', sep='\t')
merged = pd.merge(df_pat, df_diag, on='PatientID', how='inner')
print(f"✅ Merged {len(merged)} records\n")

sample = merged.head(5)

print("🧠 PHASE 1: Getting all embeddings (no DB yet)...\n")

client = genai.Client(api_key=GOOGLE_KEY)
embeddings_data = []

for idx, row in sample.iterrows():
    pid = str(row['PatientID'])
    story = f"Patient {pid} is a {row['PatientRace']} {row['PatientGender']} born {row['PatientDateOfBirth']}. Diagnosis: {row['PrimaryDiagnosisDescription']}."
    
    print(f"[{idx+1}] Embedding {pid}...", end=" ", flush=True)
    try:
        res = client.models.embed_content(
            model="models/text-embedding-004",
            contents=story
        )
        vector = list(res.embeddings[0].values)
        embeddings_data.append({
            'patient_id': pid,
            'story_text': story,
            'vector': vector
        })
        print("✅")
    except Exception as e:
        print(f"❌ {e}")

print(f"\n✅ Got {len(embeddings_data)} embeddings\n")

# Now we're DONE with Gemini. Close it.
del client

# NOW do database operations
print("💾 PHASE 2: Saving to database...\n")

import mysql.connector
from my_secrets import DB_CONFIG

for data in embeddings_data:
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute("SELECT id FROM patient_vectors WHERE patient_id = %s", (data['patient_id'],))
        if cursor.fetchone():
            print(f"  ⏩ {data['patient_id']} already in DB")
            conn.close()
            continue
        
        # Insert
        cursor.execute(
            "INSERT INTO patient_vectors (patient_id, story_text, vector_json) VALUES (%s, %s, %s)",
            (data['patient_id'], data['story_text'], json.dumps(data['vector']))
        )
        conn.commit()
        conn.close()
        
        print(f"  ✅ Saved {data['patient_id']}")
        
    except Exception as e:
        print(f"  ❌ {data['patient_id']}: {e}")

print("\n✅ Done!")
