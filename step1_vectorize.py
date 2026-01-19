import pandas as pd
import json
import time
from google import genai
from my_secrets import GOOGLE_KEY

client = genai.Client(api_key=GOOGLE_KEY)

print("📂 Reading raw files...")
try:
    df_pat = pd.read_csv('dataset_healthchatbot/PatientCorePopulatedTable.txt', sep='\t')
    df_diag = pd.read_csv('dataset_healthchatbot/AdmissionsDiagnosesCorePopulatedTable.txt', sep='\t')
    
    # Merge them first
    merged = pd.merge(df_pat, df_diag, on='PatientID', how='inner')
    
    # --- THE FIX: GROUP BY PATIENT ID ---
    # We combine all diagnoses for the same patient into one comma-separated string
    print("🔄 Aggregating diagnoses per patient...")
    grouped = merged.groupby('PatientID').agg({
        'PatientRace': 'first',
        'PatientGender': 'first',
        'PatientDateOfBirth': 'first',
        'PrimaryDiagnosisDescription': lambda x: ', '.join(x.unique()) # <--- The Magic Line
    }).reset_index()
    
    print(f"✅ Consolidated into {len(grouped)} unique patient profiles.")

except Exception as e:
    print(f"❌ File Error: {e}")
    exit()

# Process top 20 unique patients
sample = grouped.head(20)
results = []

print("\n🧠 Starting Vectorization (One Story Per Patient)...")
for index, row in sample.iterrows():
    pid = str(row['PatientID'])
    try:
        # Create the "Mega Story"
        story = (f"Patient {pid} is a {row['PatientRace']} {row['PatientGender']} "
                 f"born on {row['PatientDateOfBirth']}. "
                 f"Medical History includes: {row['PrimaryDiagnosisDescription']}.")
        
        resp = client.models.embed_content(
            model="models/text-embedding-004",
            contents=story
        )
        
        results.append({
            "patient_id": pid,
            "story": story,
            "vector": resp.embeddings[0].values
        })
        print(f"✅ Vectorized Patient {pid}")
        time.sleep(1) 
        
    except Exception as e:
        print(f"❌ Failed on {pid}: {e}")

with open("patient_vectors_dump.json", "w") as f:
    json.dump(results, f)

print("\n💾 DONE! Data aggregated and saved. Now run Step 2 (Upload).")
