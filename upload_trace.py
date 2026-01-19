import sys
print("Imports starting...", flush=True)

import pandas as pd
print("✅ pandas imported", flush=True)

import mysql.connector
print("✅ mysql imported", flush=True)

import json
print("✅ json imported", flush=True)

import time
print("✅ time imported", flush=True)

from google import genai
print("✅ genai imported", flush=True)

from my_secrets import DB_CONFIG, GOOGLE_KEY
print("✅ secrets imported", flush=True)

import traceback
print("✅ traceback imported\n", flush=True)

print("📂 Loading files...", flush=True)
df_pat = pd.read_csv('dataset_healthchatbot/PatientCorePopulatedTable.txt', sep='\t')
df_diag = pd.read_csv('dataset_healthchatbot/AdmissionsDiagnosesCorePopulatedTable.txt', sep='\t')
merged = pd.merge(df_pat, df_diag, on='PatientID', how='inner')
print(f"✅ Merged {len(merged)} records\n", flush=True)

print("Initializing Gemini client...", flush=True)
client = genai.Client(api_key=GOOGLE_KEY)
print("✅ Gemini client ready\n", flush=True)

sample = merged.head(2)

print("Testing embedding...", flush=True)
res = client.models.embed_content(
    model="models/text-embedding-004",
    contents="Test"
)
print(f"✅ Embedding works\n", flush=True)

print("Connecting to database...", flush=True)
sys.stdout.flush()

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    print("✅ Connected!", flush=True)
except Exception as e:
    print(f"❌ DB Error: {e}", flush=True)
    traceback.print_exc()
