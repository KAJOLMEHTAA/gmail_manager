# Gmail Manager

A Python application that manages Gmail emails using custom rules to automatically organize, mark as read/unread, and move messages to specific labels.

## Demo Video
[Watch the demo video here](https://www.loom.com/share/6f5575c0ca2c4bd5a4e896e3e25ee16c?sid=590eb28c-3953-48b2-a35a-e03e7a4dbe6d)

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

## Setup Instructions

### 1. Prerequisites
- Python 3.x
- PostgreSQL
- Google Cloud Account

### 2. Environment Setup
1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Database Setup
1. Install PostgreSQL:
   - For macOS: `brew install postgresql`
   - For Ubuntu: `sudo apt-get install postgresql`
   - For Windows: Download from [PostgreSQL website](https://www.postgresql.org/download/windows/)

2. Start PostgreSQL service:
   - macOS: `brew services start postgresql`
   - Ubuntu: `sudo service postgresql start`
   - Windows: Service should start automatically

3. Create database and user:
```sql
-- Connect to PostgreSQL
psql postgres

-- Create database
CREATE DATABASE <dbname>;

-- Create user with password
CREATE USER <dbuser> WITH PASSWORD '<dbpass>';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE <dbname> TO <dbuser>;

```

4. Set up environment variables in `.env`:
```bash
DB_NAME=<dbname>
DB_USER=<dbuser>
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 4. Gmail API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a New Project
3. Enable Gmail API:
   - In the left menu, go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click on it and click "Enable"
4. Create Service Account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the service account details
5. Add Scopes:
   - Add `https://www.googleapis.com/auth/gmail.modify` scope
6. Add Test Users:
   - Add your email as a test user
7. Create and Download JSON Key:
   - Save as `credentials.json` in project root

### 5. Configuration
1. Update `rules.json` with your email filtering rules
2. Run the application:
```bash
python3 main.py
```

## Troubleshooting
- Ensure all environment variables are set
- Verify Gmail API credentials
- Check database connection settings
- Ensure proper permissions for service account
- If database connection fails:
  - Verify PostgreSQL service is running
  - Check if user has correct permissions
  - Confirm database name and credentials