import requests
import os, re, json, time
from pydantic import BaseModel, Field

# getting api and cx
search_api_path = "confidential/search_api.txt"
search_cx_path = "confidential/search_cx.txt"

with open(search_api_path, 'r') as file:
    API_KEY = file.read()  # Read the entire content of the file

cx_path = "confidential/search_cx.txt"
with open(search_cx_path, 'r') as file:
    CX = file.read()  # Read the entire content of the file

query = 'Where is Texas A&M'

# Construct the request URL
url = f'https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CX}&q={query}'

# Make the request
response = requests.get(url)

# Check for a successful response
if response.status_code == 200:
    results = response.json()
    for item in results.get('items', []):
        print(f"Title: {item['title']}")
        print(f"Link: {item['link']}")
        print(f"Snippet: {item['snippet']}\n")
else:
    print(f"Error: {response.status_code} - {response.text}")
