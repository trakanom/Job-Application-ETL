from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
import email
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re

class Listener:
    def __init__(self):
        ...
    def connect(self):
        ...
    # import the required libraries


# Define the SCOPES. If modifying it, delete the token.pickle file.



# def add_to_cached_data(key,value):
#     if key not in cached_data.keys():
#         cached_data[key]=[]
#     cached_data[key].append(value)
    
def getEmails(credpath, filters = None, maxRequests = None, query=None, nextPage=None, maxResults=None):
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    maxResults=500 if maxResults is None else maxResults
    cached_data = {}
    duplicates = {}
    rejected_values = []
    # Variable creds will store the user access token.
    # If no valid token found, we will create one.
    creds = None
    pickle_path = '.\\models\\config\\token.pickle'
    pickle_path = re.search(r"(\.(\\\w+)+)\\\w+.json", credpath).group(1)+r"\\token.pickle"
    # The file token.pickle contains the user access token.
    # Check if it exists
    if os.path.exists(pickle_path):

        # Read the token from the file and store it in the variable creds
        with open(pickle_path, 'rb') as token:
            creds = pickle.load(token)

    # If credentials are not available or are invalid, ask the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  #TODO Fix this
        else:
            flow = InstalledAppFlow.from_client_secrets_file(f'{credpath}', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the access token in token.pickle file for the next run
        with open(pickle_path, 'wb') as token:
            pickle.dump(creds, token)

    # Connect to the Gmail API
    service = build('gmail', 'v1', credentials=creds)

    # request a list of all the messages
    if nextPage==None:
        result = service.users().messages().list(userId='me', maxResults=maxResults, q=query).execute()
    else:
        result = service.users().messages().list(userId='me', maxResults=maxResults, q=query, pageToken=nextPage).execute()
    
    # We can also pass maxResults to get any number of emails. Like this:
    # result = service.users().messages().list(maxResults=200, userId='me').execute()
    messages = result.get('messages')
    number_messages = len(messages)
    print("Number of messages for this round: ", number_messages)
    # messages is a list of dictionaries where each dictionary contains a message id.

            
    # iterate through all the messages
    for msg in messages:
        # Get the message from its id
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        # Use try-except to avoid any Errors
        # try:
        # Get value of 'payload' from dictionary 'txt'
        payload = txt['payload']
        headers = payload['headers']
        headers = {item['name']:item['value'] for item in headers}
        filter_stuff = 'X-LinkedIn-Template' in headers.keys() #eventually call all email classification methods
        target_values = ['jobs_applicant_applied', 'email_jobs_job_application_viewed_01', 'email_jobs_application_rejected_01']
        if filter_stuff: # Checks if.
            if headers['X-LinkedIn-Template'] not in target_values:
                rejected_values.append(headers['X-LinkedIn-Template'])
                continue
            # print("FILTER RESULT", headers['X-LinkedIn-Template'])
            pass
        else:
            continue
        subject = headers['Subject']
        sender = headers['From']
        
        parts = payload.get('parts')[0]
        data = parts['body']['data']
        data = data.replace("-","+").replace("_","/")
        decoded_data = base64.b64decode(data)
        
        soup = BeautifulSoup(decoded_data , "lxml")
        body = soup.body()

        # if debug|self.debug:
            # print("Headers: ", headers)
            # print("Subject: ", subject)
            # print("From: ", sender)
            # print("Message: ", body)
            # print('\n')
        data = {
            "subject":subject,
            "headers":headers,
            "body":body,
            "from":sender,
        }
        
        if subject not in cached_data.keys():
            cached_data.update({subject:data})
        else:
            duplicates.update({subject:data})
    # except Exception as e:
    # 	print(e,'"EXCEPTION')
    rejected_values = set(rejected_values)
    # print(cached_data)
    print("Duplicates", duplicates)
    print("Unfiltered Emails", rejected_values)
    if number_messages == maxResults: #capped query; need to rerun until all messages are parsed.
        print("Next round of parsing!")
        cached_data |= getEmails(credpath=credpath, filters=filters, query=query, nextPage=result['nextPageToken'], maxResults=maxResults) # Creating a union between these sets. Allows for recursion.
    
    return cached_data
if __name__=='__main__':
    print(os.getcwd())
    # credential_path = ".\\models\\config\\mikanometrics_gmail_credentials.json"
    credential_path = ".\\models\\config\\mika_wisener_gmail_credentials.json"
    query=r'from:jobs-noreply@linkedin.com|jobs-listings@linkedin.com -"apply now|to" -"new job|jobs" -"don\'t forget"'
    getEmails(credpath=credential_path, query=query, maxResults=500)
    # print(len(cached_data.keys()))
