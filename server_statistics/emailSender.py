import os.path
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage

my_email = "development.notify.me@gmail.com"
path_credentials = "D:\\implementations\\api_transport\\server_statistics\\credentials.json"
recipient_email = "development.notify.me@gmail.com"

# If modifying these scopes, delete the file token.json.
SCOPES_register = ['https://www.googleapis.com/auth/gmail.compose']
SCOPES_use = SCOPES_register #['https://www.googleapis.com/auth/gmail.compose']


def register_scopes():
    # do that for the first time to allow access to gmail account to send emails (or other SCOPES).
    # access information is stored in token.json

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES_register)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                path_credentials, SCOPES_register)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

def send_message(to=None, subject=None, message_text=None):
    """Create and send an email message
    Print the returned  message id
    Returns: Message object, including message id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    if to is None:
        to = recipient_email
    if subject is None:
        subject = "Automated draft"
    if message_text is None:
        message_text = "'This is automated draft mail'"

    #creds, _ = google.auth.default()
    creds = Credentials.from_authorized_user_file('token.json', SCOPES_use)

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()

        message.set_content(message_text)

        message['To'] = to
        message['From'] = my_email
        message['Subject'] = subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())

        print("Successfully sent email with subject:", message["Subject"])
    except HttpError as error:
        print("An error occurred:", error)
        send_message = None
    return send_message

# ------ tutorial ------

# do once for the first time.
register_scopes()

# send an email with subject and message
#subject = "Test-E-mail2"
#message_text = "Diese email wurde automatisch versendet."
#send_message(subject=subject, message_text=message_text)

