# Email Rules Manager

A Python application that manages Gmail emails using custom rules to automatically organize, mark as read/unread, and move messages to specific labels.

## Features

- Connect to Gmail using OAuth 2.0 authentication
- Store email metadata in PostgreSQL database
- Apply custom rules based on sender and subject conditions
- Actions supported:
  - Mark emails as read/unread
  - Move emails to specified labels
- Rule conditions can check:
  - Email sender (equals or contains)
  - Subject line (equals or contains)

## Prerequisites

- Python 3.7+
- PostgreSQL database
- Gmail account
- Google Cloud project with Gmail API enabled

## Setup Instructions

1. Clone this repository

2. Install required Python packages:
```pip install -r requirements.txt```

3. Create Postgres DB:
```CREATE DATABASE <dbname>;```
```CREATE USER <dbuser> WITH PASSWORD <dbpass>;```
```GRANT ALL PRIVILEGES ON DATABASE <dbname> TO <dbuser>;```

4. Setup Gmail API:
Step 1: Go to Google Cloud Console
Step 2: Create a New Project
Step 3: Enable Gmail API
- In the left menu, go to "APIs & Services" > "Library"
- Search for "Gmail API"
- Click on it and click "Enable"
Step 4: Create Service Account
- Go to "APIs & Services" > "Credentials"
Step 5: Add scopes
Step 6: Add Test users
Step 7: Create and Download JSON Key

5. How to run:
```python3 main.py```