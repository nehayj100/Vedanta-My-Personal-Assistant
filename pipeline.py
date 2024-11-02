# Tasks:
    # 1. Send emails
    # 2. Schedule meetings + if meeting time in events - ask for new time (repeat till no conflict)
    # 3. RAG from pdfs
    # 4. Search Internet
    # 5. Ask questions 

## IMPORT 

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


ollama_client = openai.Client(
    base_url="http://127.0.0.1:11434/v1", api_key="EMPTY")

stop = ['Observation:', 'Observation ']

# If modifying these scopes, delete the file token.json
# keys for calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# passowrd for emails
password_path = "confidential/email_pass.txt"
# Open and read the file for email password
with open(password_path, 'r') as file:
    passkey = file.read()  # Read the entire content of the file 

# Directory to your pdf files:
DATA_PATH = r"papers"

## apis for google search
# getting api and cx
search_api_path = "confidential/search_api.txt"
search_cx_path = "confidential/search_cx.txt"

with open(search_api_path, 'r') as file:
    API_KEY = file.read()  # Read the entire content of the file


with open(search_cx_path, 'r') as file:
    CX = file.read()  # Read the entire content of the file

calendar_creds = "confidential/credentials.json"

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

EMAIL_DB="""
NAME		EMAIL
VY Joshi: vedantjoshi370@gmail.com
Neha Joshi: nehayj100@gmail.com
"""

def find_email(query: str) -> str:
    s = "The following lists names and email addresses of my contacts:\n"+EMAIL_DB+"\n Please return email of "+query
    return invoke_llm(s)

def send_email_internal(to_addr: str, subject: str, body: str) -> str:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # SMTP server configuration
    smtp_server = "smtp.gmail.com"  # This might need to be updated
    smtp_port = 587  # or 465 for SSL or 587
    username = "nehayjoshi98@gmail.com"
    password = f"{passkey}"
    from_addr = "nehayjoshi98@gmail.com"

    cc_addr = "xxx"

    # Email content

    # Setting up the MIME
    message = MIMEMultipart()
    message["From"] = from_addr
    message["To"] = to_addr
    message["Subject"] = subject
    # message["Cc"] = cc_addr  # Add CC here
    message.attach(MIMEText(body, "plain"))

    recipients = [to_addr, cc_addr]  # List of all recipients

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(username, password)
            text = message.as_string()
            server.sendmail(from_addr, recipients, text)
            output = "Email successfully sent!"
    except Exception as e:
        output = f"Failed to send email: {e}"
    print(output)
    return output

def send_email(llm_json_str: str) -> str:
    try:
        patch_json_content = json.loads(llm_json_str)
        to_addr = patch_json_content["to_addr"]
        subject = patch_json_content["subject"]
        body = patch_json_content["body"]

    except Exception as e:
        error_str = f"Exception: {e}"

    print(f"To: {to_addr}\n{subject}\n==============================\n{body}\n=================================\n")
    approval = input("Is the above email good to go? (yes/no): ")
    if approval.lower() == 'yes' or approval.lower() == 'y':
        output = send_email_internal(to_addr, subject, body)
        # output = "email sent successfully"
    else:
        output = f"Email sending was not approved. Reason for disapproval: {approval}"

    return output

## defining functions for all tasks
def search_the_internet(query):
    # print(query)
    # Construct the request URL
    google_search_url = f'https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CX}&q={query}'

    # Make the request
    response = requests.get(google_search_url)
    flag = 0
    output = ""
    # Check for a successful response
    if response.status_code == 200:
        results = response.json()
        for item in results.get('items', []):
            print(f"Title: {item['title']}")
            print(f"Link: {item['link']}")
            print(f"Snippet: {item['snippet']}\n")
        flag = 1
    else:
        print(f"Error: {response.status_code} - {response.text}")
        output = "Did not fetch"
    if flag == 1:
        output = "Search results fetched successfully"
    return output

def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)  # Initialize PDF loader with specified directory
    return document_loader.load()  # Load PDF documents and return them as a list of Document objects


def split_text(documents: list[Document]):
    # Initialize text splitter with specified parameters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,  # Size of each chunk in characters
        chunk_overlap=100,  # Overlap between consecutive chunks
        length_function=len,  # Function to compute the length of the text
        add_start_index=True,  # Flag to add start index to each chunk
    )
    # Split documents into smaller chunks using text splitter
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # Print example of page content and metadata for a chunk
    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks  # Return the list of split text chunks

def perform_RAG(prompt):
    rag_client = chromadb.PersistentClient(
        path="chromadb",
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )

    # client = chromadb.Client(settings={"chromadb.storage": "sqlite", "chromadb.storage.path": "chromadb.db"})
    # Collection name
    collection_name = "docs"

    # Try to load the collection; if it doesn't exist, create it
    try:
        # Attempt to get the collection by name
        collection = rag_client.get_collection(name=collection_name)
        print(f"Collection '{collection_name}' loaded successfully.")
    except Exception as e:
        # If collection doesn't exist, create it
        print(f"Collection '{collection_name}' not found. Creating a new one.")
        collection = rag_client.create_collection(name=collection_name)

        documents = load_documents()  # Load documents from a source
        chunks = split_text(documents)  # Split documents into manageable chunks

        # store each document in a vector embedding database
        for i, chunk in enumerate(chunks):
            d = chunk.page_content
            print(f"Chunk {i}: {d}")
            response = ollama.embeddings(model="llama3.2", prompt=d)
            embedding = response["embedding"]
            # print(f"embedding: {embedding}")
            collection.add(
                ids=[str(i)],
                embeddings=[embedding],
                documents=[d]
            )

    # # an example prompt
    # prompt = "How does chain of thought prompting work?"

    # prompt = "What's the score of llama 3 8B on MATH (0-shot, CoT)?"

    # generate an embedding for the prompt and retrieve the most relevant doc
    embedding = ollama.embeddings(
    prompt=prompt,
    model="llama3.2"
    )["embedding"]
    # print(f"embedding: length {len(embedding)})\n{embedding}")

    results = collection.query(
    query_embeddings=[embedding],
    n_results=5
    )

    print(f"results:\n{results}")

    # data = results['documents'][0][0]
    # Extract the documents from the results
    data1 = results['documents'][0][0]
    data2 = results['documents'][0][1]
    data3 = results['documents'][0][2]
    data4 = results['documents'][0][3]
    data5 = results['documents'][0][4]

    # Combine the data into a single string
    combined_data = f"{data1}\n\n{data2}\n\n{data3}\n\n{data4}\n\n{data5}"

    prompt = f"Using this data: {combined_data}. Respond to this prompt: {prompt}"

    print(f"prompt: {prompt}")

    # generate a response combining the prompt and data we retrieved in step 2
    output = ollama.generate(
    model="llama3.2",
    prompt=prompt
    )

    print(f"response:\n{output['response']}")

    output = "Answer fetched successfully"
    return output

def clear_db():
    client = chromadb.PersistentClient(
        path="chromadb",
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )

    # Get all collections and delete them
    collections = client.list_collections()

    for collection in collections:
        client.delete_collection(name=collection.name)  # Deleting the collection by name

    print("All collections have been cleared.")

# def convert_date():
#     pass

# def convert_time():
#     pass

def extract_meeting_details() -> str:
    heads_up = False
    while not heads_up:
        summary = input("What is the meeting for?    ")
        description = input("Describe the meeting agenda:    ")
        attendee = input("Who is invited? give me the attendee's email:    ")
        start_date = input("Tell me Date of the meeting? Format should be yyyy-m-dd:    ")
        # start_date = convert_date(start_date)
        start_time = input("Tell me when should the meeting start? Format should be 24 hours hh:mm:ss:    ")
        minutes_in_meeting = input("how many minutes should the meeting last?")
        time_zone = 'America/Los_Angeles'
        location = 'Zoom'
        # start_time = convert_time(start_time)
        approval = input(f"""Is the following information correct?
            summary = {summary}
            desctiption = {description}
            attendee = {attendee}
            start date = {start_date}
            start time = {start_time}
            # minutes in meeting: {minutes_in_meeting}
            time zone = {time_zone}
            location = {location}
            Meeting will be scheduled for {minutes_in_meeting} minutes:  """)
      
        final_output = ""

        if approval.lower() == 'yes' or approval.lower() == 'y':
            output = schedule_meeting(start_date, start_time, minutes_in_meeting, attendee, summary, description, time_zone, location)
        else:
            output = f"Meeting scheduling sending was not approved. Reason for disapproval: {approval}"

        if output == "Meeting scheduled successfully":
            final_output = send_email_internal(str(attendee), str(summary), str(description))
            print("email sent to the attendee!")
            final_output = "Email successfully sent!"
        
        if final_output == "Email successfully sent!":
            final_output = "Meeting scheduled successfuly and email sent to the invitees!!"
            heads_up = True
            return final_output
        
            

def calculate_end_time(start_time_str, minutes_to_add):
    # Parse the start time
    start_time = datetime.strptime(start_time_str, "%H:%M:%S")
    
    # Add the given minutes to the start time
    end_time = start_time + timedelta(minutes=minutes_to_add)
    
    # Format the end time back to string
    end_time_str = end_time.strftime("%H:%M:%S")
    return end_time_str

def schedule_meeting(start_date, start_time, minutes_meeting, attendee, summary, description, time_zone, location):
    start_date_time = start_date + 'T' + start_time
    end_date = start_date
    end_time = calculate_end_time(start_time, int(minutes_meeting))
    end_date_time = end_date+'T'+end_time
    print("here ")
    output = schedule_meeting_internal(start_date_time, end_date_time, attendee, summary, description, time_zone, location)
    print("OUTPUT IS:", output)
    return output
    

def schedule_meeting_internal(start_date_time, end_date_time, attendee, summary, description, time_zone, location):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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
        print("Getting the upcoming 10 events")
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

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

    except HttpError as error:
        print(f"An error occurred: {error}")   
    
    print("creating event!!")

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_date_time,
            'timeZone': time_zone,
        },
        'end': {
            'dateTime': end_date_time,
            'timeZone': time_zone,
        },
        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=1'
        ],
        'attendees': [
            {'email': attendee},
            
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 10},
            ],
        },
        }
    print("pt1 ", event)
    event = service.events().insert(calendarId='primary', body=event).execute()
    print("pt2 ", event)
    print('Event created: %s' % (event.get('htmlLink')))

    output = "Meeting scheduled successfully"
    return output

def main():
    tao_template=Template("""
    My name is Neha Joshi. You are my Personal Assistant, Vedanta. You have access to the following tools:
                    
        FindEmail: "Find the email addresses of my contacts. Input is the contact info such as names."
        SendEmail: "Send email tool. Input is a json object with {"to_addr: str, "subject": str, "body": str"}."
        SearchInternet: "Search the internet tool. Input is a query which the user wants to search on the internet."
        AnswerUsingPdf: "Answer using pdf tool. Input is a query which needs to be answered using perform_RAG"
        ScheduleMeeting: "Schedule a meeting tool."

    To schedule a meeting you should use ExtractMeetingDetails.
    To craft an email, you should use FindEmail to find correct email addresses (to_addr) of my contacts.
    To search on the internet you should use search_the_internet. Do not send emails if action is search the internet.
    To answer using pdf you should use perform_RAG. Do not send emails or search internet if action is asnwer using pdf.
    
    Use the following format:
        
        Thought: you should always think about what to do
        Action: the action to take, should be one of [FindEmail, SendEmail, SearchInternet, AnswerUsingPdf, ExtractMeetingDetails]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I have now completed the task 
        Done: the final message to the task
        
    Always generate Action and Action Input. Missing them will produce an error!
        
        Begin!               
        
        Question:
        $question

        Thought:
    """)

    MAX_ITERATION = 10
    def llm_do_task(question: str):
        prompt=str(tao_template.substitute(question=question))
        iteration = 0
        while True:
            iteration =iteration+1
            if iteration>MAX_ITERATION:
                break
            llm_output = invoke_llm(prompt)
            regex = (
                    r"Action\s*\d*\s*:[\s]*(.*?)[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
                )
            action_match = re.search(regex, llm_output, re.DOTALL)
            if action_match:
                action = action_match.group(1).strip()
                action_input = action_match.group(2)
                tool_input = action_input.strip("\n")
                
                if llm_output.startswith("Thought:"):
                    prompt = prompt+llm_output[8:]
                else:
                    prompt = prompt+llm_output

                print(f"------- tool: {action} input: {tool_input}\n")

                if action=="SendEmail":
                    tool_output = send_email(tool_input)
                    if "Email successfully sent!" in tool_output:
                        return
                elif action=="FindEmail":
                    tool_output = find_email(tool_input)
                elif action=="SearchInternet":
                    tool_output = search_the_internet(tool_input)
                    if tool_output == "Search results fetched successfully":
                        return
                elif action=="AnswerUsingPdf":
                    tool_output = perform_RAG(tool_input)
                    if tool_output == "Answer fetched successfully":
                        return
                elif action == "ExtractMeetingDetails":
                    tool_output = extract_meeting_details()
                    if tool_output == "Meeting scheduled successfuly and email sent to the invitees!!":
                        return
                # elif action=="ScheduleMeeting":
                #     tool_output = schedule_meeting(tool_input)
                #     if tool_output == "Meeting scheduled successfully":
                #         return
                else:
                    tool_output = "Error: Action "+f"'{action}' is not a valid action!"

                print(f"------- tool_output ------- \n{tool_output}\n")

            elif 'Done:' in llm_output:
                print(f"\n\n{llm_output}")
                return
            else: 
                print(f"Error: wrong LLM response\n{llm_output}\n")

            prompt = prompt+"\nObservation: "+str(tool_output)+"\n"

    print(f"Namaskaar! I'm your Personal Assistant, Vedanta.")
    while True:
        try:
            user_input = input("Please enter a new task: ")
            tic = time.time()
            llm_do_task(user_input)
            latency = time.time() - tic
            print(f"\nLatency: {latency:.3f}s")
        except KeyboardInterrupt:
                print("\nExiting.\n")
                break
        
if __name__ == "__main__":
  main()