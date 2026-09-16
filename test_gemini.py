import os
from dotenv import load_dotenv
from google import genai

# Load .env
load_dotenv()

# Check that the API key exists
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env")

# Create Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Send a simple request
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Explain what MongoDB is in one simple sentence."
)

print("🤖 Gemini response:")
print(response.text)