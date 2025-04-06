import os
import json
import psycopg2
import base64
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

# Configuration
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}
LABEL_NAME = "Jobs"  # Label to move messages

# Gmail API Setup
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CLIENT_SECRETS_FILE = "credentials.json"
TOKEN_PICKLE_FILE = "token.pickle"


def get_gmail_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, "rb") as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(TOKEN_PICKLE_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


def create_db():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS emails (
                    id TEXT PRIMARY KEY,
                    sender TEXT,
                    subject TEXT,
                    message TEXT,
                    received TIMESTAMP,
                    read BOOLEAN)"""
    )
    conn.commit()
    cur.close()
    conn.close()


def get_label_id(service, label_name):
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for label in labels:
        if label["name"].lower() == label_name.lower():
            return label["id"]
    # Create if not exists
    new_label = (
        service.users()
        .labels()
        .create(userId="me", body={"name": label_name})
        .execute()
    )
    return new_label["id"]


def fetch_emails():
    service = get_gmail_service()
    results = service.users().messages().list(userId="me", maxResults=100).execute()
    messages = results.get("messages", [])

    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = {h["name"]: h["value"] for h in msg_data["payload"]["headers"]}
        payload = msg_data["payload"].get("body", {}).get("data")
        decoded_message = base64.urlsafe_b64decode(payload).decode() if payload else ""

        sender = headers.get("From", "")
        subject = headers.get("Subject", "")
        received = datetime.fromtimestamp(int(msg_data["internalDate"]) / 1000)
        read = "UNREAD" not in msg_data.get("labelIds", [])

        cur.execute(
            """INSERT INTO emails (id, sender, subject, message, received, read)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ON CONFLICT (id) DO NOTHING""",
            (msg["id"], sender, subject, decoded_message, received, read),
        )

    conn.commit()
    cur.close()
    conn.close()


def check_from_condition(email_from, condition):
    sender_list = [s.strip().lower() for s in condition["value"].split(",")]
    email_from = email_from.lower()
    predicate = condition["predicate"].lower()

    if predicate == "equals":
        return any(sender == email_from for sender in sender_list)
    elif predicate == "contains":
        return any(sender in email_from for sender in sender_list)
    return False


def check_subject_condition(email_subject, condition):
    subject_terms = [term.strip().lower() for term in condition["value"].split(",")]
    email_subject = email_subject.lower()
    predicate = condition["predicate"].lower()

    if predicate == "contains":
        return any(term in email_subject for term in subject_terms)
    elif predicate == "equals":
        return any(term == email_subject for term in subject_terms)
    return False


def check_conditions(email, rule):
    from_match = False
    subject_match = False

    for condition in rule["conditions"]:
        field = condition["field"].lower()

        if field == "from":
            from_match = check_from_condition(email[1], condition)
        elif field == "subject" and from_match:
            subject_match = check_subject_condition(email[2], condition)

    return from_match and subject_match


def apply_rules():
    with open("rules.json", "r") as file:
        rules_data = json.load(file)

    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("SELECT * FROM emails")
    emails = cur.fetchall()
    cur.close()
    conn.close()

    service = get_gmail_service()
    label_id = get_label_id(service, LABEL_NAME)

    for rule in rules_data["rules"]:
        for email in emails:
            if check_conditions(email, rule):
                print(f"Moving email - From: {email[1]}, Subject: {email[2]}")
                take_action(service, email[0], rule["action"], label_id)


def take_action(service, email_id, action, label_id):
    try:
        if action == "mark_as_read":
            service.users().messages().modify(
                userId="me", id=email_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            print(f"Marked email {email_id} as read")
        elif action == "mark_as_unread":
            service.users().messages().modify(
                userId="me", id=email_id, body={"addLabelIds": ["UNREAD"]}
            ).execute()
            print(f"Marked email {email_id} as unread")
        elif action == "move_message":
            service.users().messages().modify(
                userId="me", id=email_id, body={"addLabelIds": [label_id]}
            ).execute()
            print(f"Moved email {email_id} to specified label")
    except Exception as e:
        print(f"Error taking action on email {email_id}: {str(e)}")


if __name__ == "__main__":
    # create_db()
    # fetch_emails()
    apply_rules()
