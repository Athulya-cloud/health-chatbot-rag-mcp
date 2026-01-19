import pandas as pd
import json
import time
from google import genai
from my_secrets import GOOGLE_KEY

# 1. Setup AI
client = genai.Client(api_key=GOOGLE_KEY)

print("📂 Reading raw files from 'dataset_healthchatbot'...")
try:
    # UPDATED PATHS based on your folder structure
    df_pat = pd.read_csv('dataset_healthchatbot/PatientCorePopulatedTable.txt', sep='\t')
    df_diag = pd.read_csv('dataset_healthchatbot/AdmissionsDiagnosesCorePopulatedTable.txt', sep='\t')
    merged = pd.merge(df_pat, df_diag, on='PatientID', how='inner')
    print(f"✅ Loaded {len(merged)} records.")
except Exception as e:
    print(f"❌ File Error: {e}")
    exit()

# Take top 15 for the POC
sample = merged.head(15)
results = []

print("\n🧠 Starting Vectorization (AI Only)...")
for index, row in sample.iterrows():
    pid = str(row['PatientID'])
    try:
        story = (f"Patient {pid} is a {row['PatientRace']} {row['PatientGender']} "
                 f"born on {row['PatientDateOfBirth']}. "
                 f"Diagnosis: {row['PrimaryDiagnosisDescription']}.")
        
        # Call Google
        resp = client.models.embed_content(
            model="models/text-embedding-004",
            contents=story
        )
        vector = resp.embeddings[0].values
        
        # Save to list
        results.append({
            "patient_id": pid,
            "story": story,
            "vector": vector
        })
        print(f"✅ Vectorized Patient {pid}")
        time.sleep(1) # Be nice to the API
        
    except Exception as e:
        print(f"❌ Failed on {pid}: {e}")

# Save to local file
with open("patient_vectors_dump.json", "w") as f:
    json.dump(results, f)

print("\n💾 DONE! Data saved to 'patient_vectors_dump.json'. Now run Step 2.")