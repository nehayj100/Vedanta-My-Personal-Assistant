
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os, re, json, time
from pydantic import BaseModel, Field
import openai
import ollama
import chromadb
from langchain_community.document_loaders import PyPDFDirectoryLoader  # Importing PDF loader from Langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Importing text splitter from Langchain
from langchain.schema import Document  # Importing Document schema from Langchain
from chromadb.config import Settings
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
import requests
import os, re, json, time
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from string import Template


## apis for google search
# getting api and cx
search_api_path = "../confidential/search_api.txt"
search_cx_path = "../confidential/search_cx.txt"

with open(search_api_path, 'r') as file:
    API_KEY = file.read()  # Read the entire content of the file

with open(search_cx_path, 'r') as file:
    CX = file.read()  # Read the entire content of the file

calendar_creds = "../confidential/credentials.json"

ollama_client = openai.Client(
    base_url="http://127.0.0.1:11434/v1", api_key="EMPTY")

stop = ['Observation:', 'Observation ']
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def invoke_llm(prompt:str) -> str:
    try:
        response = ollama_client.completions.create(
            model="llama3.2",
            prompt=prompt,
            stop=stop,
        )
        output = response.choices[0].text
    except Exception as e:
        output = f"Exception: {e}"

    return output

def get_available_meeting_slots(meeting_date, minz):
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                calendar_creds, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        #print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return
        
        # tell the LLM to give us available slots 
        prompt = f"""Based on the following free time slots:\n{events}\nPlease suggest the best time slot for a meeting of {minz} minutes on {meeting_date}.
                    Return only one time slot in hh:mm:ss (hh should be between 8 and 18, mm and ss should be 00) format and no other text."""

        slots = invoke_llm(prompt)
        print(slots)

    except HttpError as error:
        print(f"An error occurred: {error}")   

get_available_meeting_slots("2024-12-12", 30)