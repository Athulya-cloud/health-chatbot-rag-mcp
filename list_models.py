from google import genai
from my_secrets import GOOGLE_KEY

client = genai.Client(api_key=GOOGLE_KEY)

print("🔍 Fetching available models for your API key...")

try:
    # This calls the 'ListModels' method mentioned in your error message
    for model in client.models.list():
        # Print model details to see available attributes
        print(f"Name: {model.name} | Display Name: {model.display_name}")
except Exception as e:
    print(f"❌ Failed to list models: {e}")