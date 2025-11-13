# ENVIRONMENT VARIABLES REFERENCE

## 🔐 Required Environment Variables

### Email Configuration (SendGrid)
```bash
export SENDGRID_API_KEY='your_sendgrid_api_key_here'
export MAIL_SENDER='your_email@example.com'
```

**What they do:**
- `SENDGRID_API_KEY` → Used as `MAIL_PASSWORD` in app.py's configure_mail() function
- `MAIL_SENDER` → Used as `MAIL_DEFAULT_SENDER` for sending emails

**How they're used in code:**
```python
# In app.py configure_mail() function:
MAIL_PASSWORD=os.getenv('SENDGRID_API_KEY', '')
MAIL_DEFAULT_SENDER=os.getenv('MAIL_SENDER', 'noreply@studyplanner.com')
```

### AI Schedule Generation (Google Gemini)
```bash
export GEMINI_API_KEY='your_gemini_api_key_here'
```

**What it does:**
- Generates study schedules based on user's subjects and topics

### Flask Session Encryption
```bash
export FLASK_SECRET_KEY='your_secret_key_here'
```

**What it does:**
- Encrypts session data for user login persistence
- Should be a strong, random string

---

## 🛠️ How to Set Environment Variables

### Option 1: Command Line (Temporary - Per Session)
```bash
# Linux/Mac - in your terminal
export SENDGRID_API_KEY='your_api_key'
export MAIL_SENDER='your_email@gmail.com'
export GEMINI_API_KEY='your_api_key'
export FLASK_SECRET_KEY='your_secret_key'

# Then run your app
python3 app.py
```

### Option 2: Create .env File (Recommended - Persistent)
1. Create a file named `.env` in your project root directory
2. Add these lines:
```
SENDGRID_API_KEY=your_sendgrid_api_key_here
MAIL_SENDER=your_email@example.com
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
```

3. Install python-dotenv:
```bash
pip install python-dotenv
```

4. Add to top of app.py (after imports):
```python
from dotenv import load_dotenv
load_dotenv()
```

### Option 3: Windows (.bat file)
Create `run.bat`:
```batch
@echo off
set SENDGRID_API_KEY=your_api_key
set MAIL_SENDER=your_email@gmail.com
set GEMINI_API_KEY=your_api_key
set FLASK_SECRET_KEY=your_secret_key
python app.py
```

Then run: `run.bat`

---

## 📝 Where to Get API Keys

### SendGrid API Key
1. Go to https://sendgrid.com/
2. Sign up for free account
3. Go to Settings → API Keys
4. Create new API Key (Full Access)
5. Copy and paste the key

### Google Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create new API key
4. Copy and paste the key

### Flask Secret Key
Generate a strong random key:
```python
import secrets
print(secrets.token_hex(32))
```

---

## ⚠️ Important Security Notes

1. **Never commit .env file to GitHub**
   - It's already in .gitignore
   - Only commit to private repositories if you must

2. **Never share your API keys**
   - They're like passwords - keep them secret
   - If you accidentally share, regenerate them

3. **Use different keys for production vs development**
   - Create separate keys for deployed app
   - Keep development keys for testing

4. **The app.py code uses:**
   - `os.getenv('SENDGRID_API_KEY', '')` for email password
   - `os.getenv('MAIL_SENDER', 'noreply@studyplanner.com')` for sender email
   - These read from your environment variables automatically

---

## ✅ Testing Your Setup

Run this Python command to verify variables are set:

```python
import os
print("SENDGRID_API_KEY:", os.getenv('SENDGRID_API_KEY', 'NOT SET'))
print("MAIL_SENDER:", os.getenv('MAIL_SENDER', 'NOT SET'))
print("GEMINI_API_KEY:", os.getenv('GEMINI_API_KEY', 'NOT SET'))
print("FLASK_SECRET_KEY:", os.getenv('FLASK_SECRET_KEY', 'NOT SET'))
```

All should show your actual values, not "NOT SET".

---

## 🔍 Troubleshooting

### Emails not sending?
- Check SENDGRID_API_KEY is correct
- Verify MAIL_SENDER is a valid email
- Check app logs for errors

### Schedule generation failing?
- Verify GEMINI_API_KEY is valid
- Check API quota isn't exceeded
- Review API response in app logs

### Login sessions not persisting?
- Ensure FLASK_SECRET_KEY is set
- Key must be consistent across restarts
- Browser must have cookies enabled

---

**Remember:** These environment variables must be set BEFORE running `python3 app.py`

