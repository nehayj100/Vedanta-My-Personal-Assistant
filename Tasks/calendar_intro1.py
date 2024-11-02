import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# keys for calendar
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]



# print(start_date_time)


def main():
  # variables for meeting details
  summary = 'Data Science Discusion'
  location = 'Zoom'
  description = 'Meeting for basic DS concepts dicsussion'
  start_date = '2024-10-30'
  start_time = '09:00:00'
  start_date_time = start_date+'T'+start_time
  end_date = '2024-10-30'
  end_time = '10:00:00'
  end_date_time = end_date+'T'+end_time
  time_zone = 'America/Los_Angeles'
  attendee_email = 'nehayj100@gmail.com'
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
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
          "../confidential/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
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
        {'email': attendee_email},
        
    ],
    'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
    },
    }
  print(event)
  event = service.events().insert(calendarId='primary', body=event).execute()
  print('Event created: %s' % (event.get('htmlLink')))


if __name__ == "__main__":
  main()


# pt1  {'summary': 'team', 'location': 'Zoom', 
# 'description': 'team', 'start': {'dateTime': '2024-12-12T10:00:00', 'timeZone': 'America/Los_Angeles'}, 
# 'end': {'dateTime': '2024-12-12T10:00:0001:00:00-07:00', 'timeZone': 'America/Los_Angeles'}, 
# 'recurrence': ['RRULE:FREQ=DAILY;COUNT=1'], 'attendees': [{'email': 'nehayj100@gmail.com'}], 
# 'reminders': {'useDefault': False, 'overrides': [{'method': 'email', 'minutes': 1440}, 
# {'method': 'popup', 'minutes': 10}]}}

# {'summary': 'Data Science Discusion', 'location': 'Zoom', 
# 'description': 'Meeting for basic DS concepts dicsussion', 
# 'start': {'dateTime': '2024-10-30T09:00:00', 'timeZone': 'America/Los_Angeles'}, 
# 'end': {'dateTime': '2024-10-30T10:00:00', 'timeZone': 
# 'America/Los_Angeles'}, 
# 'recurrence': ['RRULE:FREQ=DAILY;COUNT=1'], 
# 'attendees': [{'email': 'nehayj100@gmail.com'}], 
# 'reminders': {'useDefault': False, 
# 'overrides': [{'method': 'email', 'minutes': 1440}, {'method': 'popup', 'minutes': 10}]}}