# Study Planner - Web Application

A modern, feature-rich study planning application built with Flask and MySQL that helps students organize their studies, generate personalized schedules using AI, and track daily progress.

> ⚠️ **Important**: This application requires environment variables for email and AI services. See [Configuration](#installation) section for setup instructions. Refer to **ENV_VARIABLES_GUIDE.md** for detailed environment variable configuration.

## Features

### Authentication & Security
- **User Registration & Email Verification**: Secure signup with email verification links
- **Password Management**: Hashed passwords using bcrypt, forgot password flow with secure reset tokens
- **Session Management**: Secure session-based authentication
- **Email Change Verification**: Verify email changes through verification links

### Study Planning
- **Multi-Step Schedule Planner**: 
  - Step 1: Define plan metadata (name, dates, preferred study days)
  - Step 2: Add subjects and topics with weightages
  - Step 3: AI-powered schedule generation via Google Gemini API
- **Plan Management**: View all your study plans with detailed metadata and generated schedules
- **Schedule Editor**: Edit generated schedules by adjusting topic dates and rearranging assignments

### Daily Task Management
- **Daily To-Do List**: View topics assigned for today based on your schedule
- **Task Actions**: Mark topics as done or skip them
- **Daily Statistics**: Track completed, pending, and skipped topics with visual progress bar
- **Plan Integration**: Easily jump from to-do items to edit their parent plan

### Dashboard
- **Progress Overview**: Real-time stats on completed, pending, and total tasks
- **7-Day History Chart**: Visualize your study progress over the past week
- **Top Tasks Display**: See your next 2 scheduled tasks at a glance
- **Daily Completion Rate**: Visual progress bar showing today's completion percentage

### Account Management
- **Profile Information**: View and edit your name, email, and phone number
- **Email Updates**: Change email with verification
- **Phone Management**: Update contact information
- **Theme Toggle**: Switch between light and dark modes (persistent across sessions)

### User Experience
- **Responsive Design**: Works on desktop and tablet devices
- **Dark Mode**: Professional dark theme with persistent preference storage
- **Professional UI**: Clean, modern interface with smooth transitions
- **Sidebar Navigation**: Easy access to all major features
- **Profile Quick Access**: Click profile name or initial to go to account settings

## Technology Stack

### Backend
- **Framework**: Flask 3.0.0 (Python web framework)
- **Database**: MySQL 8.0+ with mysql-connector-python
- **Authentication**: bcrypt for password hashing, itsdangerous for tokens
- **Email**: Flask-Mail with SendGrid integration
- **External API**: Google Gemini 2.0 Flash for AI schedule generation
- **Data**: pandas for data processing

### Frontend
- **Templating**: Jinja2 (Flask built-in)
- **Styling**: CSS3 with responsive design
- **Dark Mode**: CSS custom properties and JavaScript toggle
- **Charting**: Plotly (optional, for future graph enhancements)

### Additional Libraries
- requests (API calls)
- Werkzeug (WSGI utilities)
- click (CLI utilities)

## Installation

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Git

### Setup Steps

1. **Clone the Repository**
```bash
git clone https://github.com/ShlokDivyam1109/Web-Dev-Project---StudyPlanner.git
cd Web_Application
```

2. **Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Database**
Edit `db_config.py` and set your MySQL credentials:
```python
mydb = mysql.connector.connect(
    host="localhost",
    user="your_username",
    passwd="your_password",
    db="User_Logins"
)
```

5. **Initialize Database**
```bash
python3 init_db.py
```
This creates all necessary tables (User_Data, Study_Plans, Study_Subjects, Study_Topics, Study_Schedule, Daily_Progress, Account_Changes).

6. **Configure Environment Variables**
Set the following environment variables before running the app:

```bash
export SENDGRID_API_KEY='your_sendgrid_api_key'
export MAIL_SENDER='your_email@example.com'
export GEMINI_API_KEY='your_gemini_api_key'
export FLASK_SECRET_KEY='your_secret_key'
```

Or create a `.env` file in the project root:
```
SENDGRID_API_KEY=your_sendgrid_api_key
MAIL_SENDER=your_email@example.com
GEMINI_API_KEY=your_gemini_api_key
FLASK_SECRET_KEY=your_secret_key
```

**Important**: `MAIL_PASSWORD` and `MAIL_DEFAULT_SENDER` in `app.py` use these environment variables:
- `MAIL_PASSWORD` uses `SENDGRID_API_KEY` environment variable
- `MAIL_DEFAULT_SENDER` uses `MAIL_SENDER` environment variable

If these environment variables are not set, the app will use fallback values (not recommended for production).

7. **Run the Application**
```bash
python3 app.py
```
The app will be available at `http://localhost:5000`

## Project Structure

```
Web_Application/
├── app.py                 # Main Flask application with all routes
├── db_config.py           # Database configuration
├── init_db.py             # Database initialization script
├── email_utils.py         # Email sending utilities
├── requirements.txt       # Python dependencies
├── test_api.py            # API testing script
├── static/
│   └── style.css         # Global styles
├── templates/
│   ├── base.html          # Base template with sidebar/topbar
│   ├── landing.html       # Landing page
│   ├── signup.html        # Signup page
│   ├── login.html         # Login page
│   ├── dashboard.html     # Main dashboard
│   ├── schedule_planner.html    # Step 1: Plan metadata
│   ├── add_subjects.html        # Step 2: Add subjects/topics
│   ├── plans.html         # View all plans
│   ├── edit_plan.html     # Edit plan schedule
│   ├── todo.html          # Daily to-do list
│   ├── account.html       # Account settings
│   ├── forgot_password.html    # Forgot password
│   ├── reset_form.html         # Password reset form
│   └── reset_success.html      # Password reset success
└── README.md              # This file
```

## Database Schema

### User_Data
- Stores user account information with hashed passwords
- Columns: id, First_Name, Last_Name, email_id, password, phone, created_at

### Study_Plans
- Stores study plan metadata and status
- Columns: id, user_id, plan_name, start_date, end_date, preferred_days, status, created_at

### Study_Subjects
- Stores subjects for each plan
- Columns: id, user_id, plan_id, subject_name, created_at

### Study_Topics
- Stores topics within subjects (may be superseded by Study_Schedule)
- Columns: id, subject_id, topic_name, initial_weightage, normalized_weightage, from_date, to_date, skipped_days, completed, created_at

### Study_Schedule
- AI-generated schedule with topics and their assigned dates
- Columns: id, user_id, subject, topic, from_date, to_date, normalized_weightage, skipped_days, status, created_at

### Daily_Progress
- Tracks daily task completion statistics
- Columns: id, user_id, day_date, total_tasks, completed_tasks, pending_from_previous, created_at

### Account_Changes
- Audit trail for email changes with verification tokens
- Columns: id, user_id, field_changed, old_value, new_value, verification_token, token_expires_at, processed, created_at

## Routes

### Authentication
- `GET /` - Landing page
- `POST/GET /signup` - User registration
- `POST/GET /login` - User login
- `GET /verify/<token>` - Email verification
- `POST/GET /forgot` - Forgot password request
- `POST/GET /reset/<token>` - Password reset
- `GET /verify_email_change/<token>` - Verify email change
- `GET /logout` - Logout

### Core Features
- `GET /dashboard` - Main dashboard with stats and top tasks
- `POST/GET /schedule` - Create new study plan (step 1)
- `POST/GET /add_subjects` - Add subjects/topics to plan (step 2)
- `POST/GET /generate_schedule` - Generate AI schedule (step 3)
- `GET /plans` - View all study plans
- `GET /edit_plan/<plan_id>` - Edit a plan's schedule
- `POST/GET /todo` - Daily to-do list with task management
- `POST/GET /account` - Account settings and profile management

## Usage

### Creating a Study Plan

1. **Navigate to Schedule Your Study** from the sidebar
2. **Enter plan details**:
   - Plan name (e.g., "JEE Mains Prep")
   - Start and end dates
   - Preferred study days per week
3. **Click "Next: Add Subjects & Topics"**
4. **Add subjects** and their topics:
   - Enter subject name
   - Add multiple topics with weightages (importance %)
5. **Click "Generate Schedule"**
   - The AI will create a personalized schedule
   - You'll be redirected to the schedule editor
6. **Edit the schedule** if needed:
   - Adjust dates for each topic
   - Save changes individually or all at once

### Managing Daily Tasks

1. **Go to To Do List** from sidebar
2. **View today's assigned topics** with statistics
3. **Mark topics as done** or **skip** them
4. **Click Edit Plan** to adjust the schedule if needed
5. **Track progress** with the completion bar

### Viewing Your Plans

1. **Click My Plans** from sidebar
2. **View all created plans** with metadata
3. **See generated schedules** for each plan
4. **Click Edit Plan** to modify schedule dates
5. **Draft plans** show no schedule until submitted

## Features in Detail

### AI Schedule Generation
The app uses Google Gemini 2.0 Flash API to generate intelligent study schedules based on:
- Subject importance (weightages)
- Total plan duration
- Preferred study days
- Normalized scheduling across the plan period

### Dark Mode
- Toggle dark mode from the topbar or account page
- Preference persists across sessions using localStorage
- Professional dark color scheme with good contrast

### Email Verification
- Secure tokens generated using itsdangerous
- Tokens expire after 1 hour
- Used for signup verification and email changes

### Password Security
- All passwords hashed with bcrypt (salt rounds: 12)
- Never stored in plain text
- Secure reset flow with temporary tokens

## Future Enhancements

- Drag-and-drop interface for rearranging topics
- Mobile app (React Native)
- Advanced analytics and performance tracking
- Collaborative study planning
- Notifications and reminders
- Integration with calendar apps (Google Calendar, Outlook)
- Multiple schedule templates
- Study resource recommendations

## Troubleshooting

### Database Connection Issues
- Verify MySQL is running: `sudo service mysql status`
- Check credentials in `db_config.py`
- Ensure database `User_Logins` exists

### Gemini API Errors
- Verify API key is valid: `echo $GEMINI_API_KEY`
- Check API quotas on Google Cloud Console
- Review API response format in `test_api.py`

### Email Not Sending
- Verify SendGrid API key is valid
- Check email configuration in `app.py`
- Review Flask-Mail settings

### Dark Mode Not Persisting
- Clear browser localStorage: Dev Tools → Application → Local Storage
- Verify browser supports localStorage

## Testing

Run the API test script to verify Gemini integration:
```bash
python3 test_api.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Author

**Shlok Divyam**
- GitHub: [@ShlokDivyam1109](https://github.com/ShlokDivyam1109)
- Repository: [Web-Dev-Project---StudyPlanner](https://github.com/ShlokDivyam1109/Web-Dev-Project---StudyPlanner)

## Support

For issues, questions, or suggestions, please open an issue on the [GitHub repository](https://github.com/ShlokDivyam1109/Web-Dev-Project---StudyPlanner/issues).

## Acknowledgments

- Google Gemini API for AI-powered schedule generation
- Flask community for the excellent web framework
- SendGrid for reliable email delivery
- MySQL for robust database management

---

**Last Updated**: November 2025
**Version**: 1.0.0
