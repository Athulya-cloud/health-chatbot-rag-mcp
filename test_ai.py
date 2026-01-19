import time
from google import genai
from my_secrets import GOOGLE_KEY

print("🧠 Testing Verified Google Gemini Models...")

try:
    client = genai.Client(api_key=GOOGLE_KEY)
    
    # Using the EXACT string from your list_models output
    print("Test 1: Asking Gemini Flash Latest...")
    response = client.models.generate_content(
        model="models/gemini-flash-latest", 
        contents="Say 'Hello Doctor, the brain is online' if you can hear me."
    )
    print(f"🤖 Answer: {response.text}")
    
    time.sleep(2) # Avoid rate limits

    print("Test 2: Creating a vector with Embedding 004...")
    vec_resp = client.models.embed_content(
        model="models/text-embedding-004",
        contents="Patient history includes hypertension and type 2 diabetes."
    )
    
    vector = vec_resp.embeddings[0].values
    print(f"✅ SUCCESS! Received a vector with {len(vector)} dimensions.")

except Exception as e:
    print(f"❌ ERROR: {e}")