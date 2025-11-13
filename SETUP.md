# Study Planner Configuration

This file should be renamed to match your setup. Use environment variables for sensitive information.

## Required Environment Variables

Set these before running the application:

```bash
# SendGrid Email API
export SENDGRID_API_KEY='your_sendgrid_api_key_here'
export MAIL_SENDER='your_email@example.com'

# Google Gemini API
export GEMINI_API_KEY='your_gemini_api_key_here'

# Flask Settings
export FLASK_SECRET_KEY='your_secret_key_here'
export FLASK_ENV='production'  # or 'development'
```

## Database Configuration

Edit `db_config.py` with your MySQL credentials:

```python
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="your_mysql_user",
    passwd="your_mysql_password",
    db="User_Logins"
)
```

## Setup Instructions

1. Create MySQL database:
```sql
CREATE DATABASE User_Logins;
```

2. Initialize database tables:
```bash
python3 init_db.py
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables in your shell or in a `.env` file

5. Run the application:
```bash
python3 app.py
```

The app will be available at `http://localhost:5000`
