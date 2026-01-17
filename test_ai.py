from google import genai
from secrets import GOOGLE_KEY

print("🧠 Testing Google Gemini API...")

try:
    client = genai.Client(api_key=GOOGLE_KEY)
    
    # FIX: Changed model name to a more generic stable version
    print("Test 1: Asking Gemini to say hello...")
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp", # Try the experimental flash if 1.5 fails, or just "gemini-1.5-flash-002"
        contents="Say 'Hello Doctor' if you can hear me."
    )
    print(f"🤖 Answer: {response.text}")
    
    print("Test 2: Creating a vector...")
    vec_resp = client.models.embed_content(
        model="text-embedding-004",
        contents="Medical Record"
    )
    vector = vec_resp.embeddings[0].values
    
    if len(vector) > 0:
        print(f"✅ SUCCESS! Received a vector with {len(vector)} dimensions.")

except Exception as e:
    print(f"❌ ERROR: {e}")