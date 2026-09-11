import os

import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PEXELS_API_KEY")

url = "https://api.pexels.com/v1/search"

headers = {
    "Authorization": api_key
}

params = {
    "query": "coffee with chatgpt open",
    "per_page": 5
}

response = requests.get(
    url,
    headers=headers,
    params=params
)

data = response.json()

print(data)

print("Status:", response.status_code)
print("Total results:", data["total_results"])

for photo in data["photos"]:
    print("Photo Details")
    print("ID:", photo["id"])
    print("Photographer:", photo["photographer"])
    print("Width:", photo["width"])
    print("Height:", photo["height"])
    print("Image URL:", photo["src"]["original"])