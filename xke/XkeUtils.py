from google import genai
import json
import os
import requests

def truncate_string(s, max_length=100):
    return s[:min(max_length, len(s))]

def json2str(json_obj):
    return json.dumps(json_obj, indent=4)

def get_embedding_via_client(texts):
    client = genai.Client()
    result = client.models.embed_content(
            model="gemini-embedding-001",
            contents= [
                "What is the meaning of life?",
                "What is the purpose of existence?",
                "How do I bake a cake?"
            ])

    for embedding in result.embeddings:
        print(embedding)



def get_embedding(text):
    import requests
import json
import os

# 1. Configuration from environment variable
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:batchEmbedContents"

# 2. Define the JSON payload
payload = {
    "requests": [
        {
            "model": "models/gemini-embedding-001",
            "content": {"parts": [{"text": "What is the meaning of life?"}]},
        },
        {
            "model": "models/gemini-embedding-001",
            "content": {"parts": [{"text": "How much wood would a woodchuck chuck?"}]},
        },
        {
            "model": "models/gemini-embedding-001",
            "content": {"parts": [{"text": "How does the brain work?"}]},
        },
    ]
}

# 3. Define the headers
headers = {
    "x-goog-api-key": API_KEY,
    "Content-Type": "application/json",
}

print("Sending batch embedding request via requests library...")

# 4. Make the POST request
try:
    response = requests.post(URL, headers=headers, data=json.dumps(payload))
    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

    # 5. Process the JSON response
    data = response.json()
    
    # The embeddings are in the 'embeddings' key
    embeddings = data.get('embeddings', [])

    print(f"\nSuccessfully generated {len(embeddings)} embeddings.")
    
    if embeddings:
        # The embedding values are under the 'values' key
        first_embedding_values = embeddings[0]['values']
        print(f"Dimensionality of embedding: {len(first_embedding_values)}")
        print(f"First 5 values of the first embedding: {first_embedding_values[:5]}")
    else:
        print("No embeddings were returned in the response.")

except requests.exceptions.RequestException as e:
    print(f"An error occurred during the API call: {e}")

# Note: Before running, ensure you have set your API key:
# export GEMINI_API_KEY="YOUR_API_KEY"
# and installed the library:
# pip install requests

