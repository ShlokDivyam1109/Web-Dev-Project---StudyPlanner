from flask import Flask, request, render_template, redirect, url_for, session, jsonify, flash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
import mysql.connector
import bcrypt
from db_config import *
import os
import json
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Initialize mail (use environment variables for sensitive data)
mail = Mail()
def configure_mail(app):
    app.config.update(
        MAIL_SERVER='smtp.sendgrid.net',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_USERNAME='apikey',
        MAIL_PASSWORD=os.getenv('SENDGRID_API_KEY', ''),
        MAIL_DEFAULT_SENDER=os.getenv('MAIL_SENDER', 'noreply@studyplanner.com')
    )
    mail.init_app(app)
configure_mail(app)

# Initialize serializer
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# MySQL setup
mydb = get_db_connection()

#======================================================
#                       Landing Page
#======================================================
@app.route('/')
def landing():
    return render_template('landing.html')

# =======================================================
#                  SIGNUP ROUTE (Now with email verify)
# =======================================================
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first = request.form['first_name']
        last = request.form['last_name']
        email = request.form['email_id']
        password = request.form['password']

        # Check if user already exists
        cursor = mydb.cursor()
        cursor.execute("SELECT email_id FROM User_Data WHERE email_id = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            return "⚠️ Account already exists! Please log in."

        # Hash password but don’t store yet
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Generate verification token
        token = s.dumps({'email': email, 'first': first, 'last': last, 'password': hashed}, salt='email-verify')
        verify_link = url_for('verify_email', token=token, _external=True)
        msg = Message('Verify Your Email - Flask App', recipients=[email])
        msg.html = f"""
	<!DOCTYPE html>
	<html>
	  <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
	    <div style="max-width: 600px; background-color: white; margin: auto; border-radius: 8px; padding: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
	      <h2 style="color: #333; text-align: center;">Welcome, {first}!</h2>
	      <p style="color: #555; font-size: 16px;">
		Thank you for signing up to our platform. To complete your registration, please verify your email by clicking the button below:
	      </p>

	      <div style="text-align: center; margin: 30px 0;">
		<a href="{verify_link}" 
		   style="background-color: #007BFF; color: white; text-decoration: none; 
		          padding: 12px 25px; border-radius: 6px; display: inline-block; 
		          font-size: 16px; font-weight: bold;">
		  Verify My Email
		</a>
	      </div>

	      <p style="color: #666; font-size: 14px;">
		If the button above doesn’t work, copy and paste this link into your browser:<br>
		<a href="{verify_link}" style="color: #007BFF;">{verify_link}</a>
	      </p>

	      <hr style="border: none; border-top: 1px solid #ddd; margin: 25px 0;">
	      <p style="color: #999; font-size: 12px; text-align: center;">
		This link will expire in 1 hour for security reasons.<br>
		© 2025 Study Planner. All rights reserved.
	      </p>
	    </div>
	  </body>
	</html>
	"""
        mail.send(msg)
        flash(f"📧 Verification email sent to {email}! Please check your inbox to verify your account.", "success")
        return redirect(url_for('landing'))
    return render_template('signup.html')


# =======================================================
#              VERIFY EMAIL (New route)
# =======================================================
@app.route('/verify/<token>')
def verify_email(token):
    try:
        data = s.loads(token, salt='email-verify', max_age=3600)
    except SignatureExpired:
        return "<h3>❌ Verification link expired!</h3>"
    except BadTimeSignature:
        return "<h3>❌ Invalid or tampered token!</h3>"

    email = data['email']
    first = data['first']
    last = data['last']
    hashed = data['password']

    # Store verified user in DB
    cursor = mydb.cursor()
    cursor.execute(
        "INSERT INTO User_Data (First_Name, Last_Name, email_id, password) VALUES (%s, %s, %s, %s)",
        (first, last, email, hashed)
    )
    mydb.commit()
    cursor.close()

    return f"<h3>✅ Email verified and account created for {email}!</h3>"


# =======================================================
#                  LOGIN ROUTE
# =======================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email_id']
        password = request.form['password']

        cursor = mydb.cursor()
        cursor.execute("SELECT password FROM User_Data WHERE email_id = %s", (email,))
        record = cursor.fetchone()
        cursor.close()

        if record and bcrypt.checkpw(password.encode('utf-8'), record[0].encode('utf-8')):
            session['user_email'] = email
            return redirect(url_for('dashboard'))
        else:
            return "❌ Invalid credentials!"
    return render_template('login.html')


# =======================================================
#               FORGOT PASSWORD ROUTE (Improved)
# =======================================================
@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email_id']

        # Check if user exists first
        cursor = mydb.cursor()
        cursor.execute("SELECT email_id FROM User_Data WHERE email_id = %s", (email,))
        record = cursor.fetchone()
        cursor.execute("SELECT password FROM User_Data WHERE email_id = %s", (email,))
        first = cursor.fetchone()
        cursor.close()

        if not record:
            return "⚠️ No account found for this email. Please sign up first!"

        # Generate secure reset token
        token = s.dumps(email, salt='email-confirm')
        reset_link = url_for('reset_with_token', token=token, _external=True)

        msg = Message('Password Reset Request', recipients=[email])
        msg.html = f"""
	<!DOCTYPE html>
	<html>
	  <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
	    <div style="max-width: 600px; background-color: white; margin: auto; border-radius: 8px; padding: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
	      <h2 style="color: #333; text-align: center;">Reset Your Study Planner password</h2>
	      <p style="color: #555; font-size: 16px;">
		We heard that you have lost your Study Planner password. Sorry about that! <br> But don't worry, you can reset your password here:
	      </p>

	      <div style="text-align: center; margin: 30px 0;">
		<a href="{reset_link}" 
		   style="background-color: #007BFF; color: white; text-decoration: none; 
		          padding: 12px 25px; border-radius: 6px; display: inline-block; 
		          font-size: 16px; font-weight: bold;">
		  Reset your password
		</a>
	      </div>

	      <p style="color: #666; font-size: 14px;">
		If the button above doesn’t work, copy and paste this link into your browser:<br>
		<a href="{reset_link}" style="color: #007BFF;">{reset_link}</a>
	      </p>

	      <hr style="border: none; border-top: 1px solid #ddd; margin: 25px 0;">
	      <p style="color: #999; font-size: 12px; text-align: center;">
		This link will expire in 1 hour for security reasons.<br>
		© 2025 Study Planner. All rights reserved.
	      </p>
	    </div>
	  </body>
	</html>
	"""
        mail.send(msg)

        return f"📧 Reset link sent to {email}!"

    return render_template('forgot_password.html')


# =======================================================
#               RESET PASSWORD ROUTE
# =======================================================
@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return '<h1>❌ The reset link has expired!</h1>'
    except BadTimeSignature:
        return '<h1>❌ Invalid or tampered token!</h1>'

    if request.method == 'POST':
        new_pass = request.form['new_password']
        confirm_pass = request.form['confirm_password']

        if new_pass != confirm_pass:
            return "<h3>⚠️ Passwords do not match!</h3>"

        hashed = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor = mydb.cursor()
        cursor.execute("UPDATE User_Data SET password = %s WHERE email_id = %s", (hashed, email))
        mydb.commit()
        cursor.close()

        return f"<h3>✅ Password reset successful for {email}!</h3>"

    return render_template('reset_form.html', token=token)


# =======================================================
#            SCHEDULE PLANNER ROUTES
# =======================================================

def get_user_id_from_session(email):
    """Retrieve user_id from database by email."""
    cursor = mydb.cursor()
    cursor.execute("SELECT id FROM User_Data WHERE email_id = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None


@app.route('/schedule', methods=['GET', 'POST'])
def schedule_planner():
    """Main schedule planner page - collect plan metadata and preferred days."""
    email = session.get('user_email')
    if not email:
        return redirect(url_for('login'))
    
    user_id = get_user_id_from_session(email)
    if not user_id:
        return redirect(url_for('login'))
    
    # Fetch user name
    cursor = mydb.cursor()
    cursor.execute("SELECT First_Name FROM User_Data WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    user_name = result[0] if result else 'Student'
    cursor.close()
    
    if request.method == 'POST':
        plan_name = request.form.get('plan_name', 'My Study Plan')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        preferred_days = request.form.get('preferred_days', '')  # e.g., "Mon,Tue,Wed,Sat"
        
        # Store the plan
        cursor = mydb.cursor()
        cursor.execute(
            """INSERT INTO Study_Plans (user_id, plan_name, start_date, end_date, preferred_days, status)
               VALUES (%s, %s, %s, %s, %s, 'draft')""",
            (user_id, plan_name, start_date, end_date, preferred_days)
        )
        mydb.commit()
        plan_id = cursor.lastrowid
        cursor.close()
        
        # Redirect to add subjects/topics
        return redirect(url_for('add_subjects', plan_id=plan_id))
    
    return render_template('schedule_planner.html', 
                          user_name=user_name,
                          active_page='schedule')


@app.route('/add_subjects', methods=['GET', 'POST'])
def add_subjects():
    """Add subjects and topics to the study plan."""
    plan_id = request.args.get('plan_id') or request.form.get('plan_id')
    email = session.get('user_email')
    
    if not plan_id or not email:
        return redirect(url_for('login'))
    
    user_id = get_user_id_from_session(email)
    if not user_id:
        return redirect(url_for('login'))
    
    # Fetch user name
    cursor = mydb.cursor()
    cursor.execute("SELECT First_Name FROM User_Data WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    user_name = result[0] if result else 'Student'
    
    # Fetch plan to show in UI
    cursor.execute(
        """SELECT plan_name, start_date, end_date, preferred_days FROM Study_Plans 
           WHERE id = %s AND user_id = %s""",
        (plan_id, user_id)
    )
    plan = cursor.fetchone()
    cursor.close()
    
    if not plan:
        return redirect(url_for('schedule_planner'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_subject':
            subject_name = request.form.get('subject_name')
            if subject_name:
                cursor = mydb.cursor()
                cursor.execute(
                    """INSERT INTO Study_Subjects (user_id, plan_id, subject_name)
                       VALUES (%s, %s, %s)""",
                    (user_id, plan_id, subject_name)
                )
                mydb.commit()
                cursor.close()
        
        elif action == 'add_topic':
            subject_id = request.form.get('subject_id')
            topic_name = request.form.get('topic_name')
            initial_weightage = request.form.get('initial_weightage', 0)
            
            if subject_id and topic_name:
                cursor = mydb.cursor()
                cursor.execute(
                    """INSERT INTO Study_Topics (subject_id, topic_name, initial_weightage)
                       VALUES (%s, %s, %s)""",
                    (subject_id, topic_name, float(initial_weightage))
                )
                mydb.commit()
                cursor.close()
        
        elif action == 'submit_plan':
            # Generate schedule using Gemini API
            return redirect(url_for('generate_schedule', plan_id=plan_id))
    
    # Fetch subjects and their topics
    cursor = mydb.cursor()
    cursor.execute(
        "SELECT id, subject_name FROM Study_Subjects WHERE plan_id = %s ORDER BY id",
        (plan_id,)
    )
    subjects = cursor.fetchall()
    
    subjects_with_topics = []
    for subject_id, subject_name in subjects:
        cursor.execute(
            """SELECT id, topic_name, initial_weightage FROM Study_Topics 
               WHERE subject_id = %s ORDER BY id""",
            (subject_id,)
        )
        topics = cursor.fetchall()
        subjects_with_topics.append({
            'id': subject_id,
            'name': subject_name,
            'topics': [{'id': t[0], 'name': t[1], 'weightage': t[2]} for t in topics]
        })
    cursor.close()
    
    return render_template('add_subjects.html', 
                          plan_id=plan_id, 
                          email=email,
                          plan=plan,
                          user_name=user_name,
                          active_page='schedule',
                          subjects=subjects_with_topics)


@app.route('/generate_schedule', methods=['GET', 'POST'])
def generate_schedule():
    """Call Gemini API to generate personalized study schedule."""
    plan_id = request.args.get('plan_id') or request.form.get('plan_id')
    email = session.get('user_email')
    
    if not plan_id or not email:
        return redirect(url_for('login'))
    
    user_id = get_user_id_from_session(email)
    if not user_id:
        return redirect(url_for('login'))
    
    # Fetch plan and subjects/topics
    cursor = mydb.cursor()
    cursor.execute(
        """SELECT plan_name, start_date, end_date, preferred_days FROM Study_Plans 
           WHERE id = %s AND user_id = %s""",
        (plan_id, user_id)
    )
    plan = cursor.fetchone()
    
    if not plan:
        cursor.close()
        return "❌ Plan not found."
    
    plan_name, start_date, end_date, preferred_days = plan
    
    # Fetch all subjects and topics for this plan
    cursor.execute(
        """SELECT s.id, s.subject_name, GROUP_CONCAT(CONCAT(t.topic_name,'|',t.initial_weightage) SEPARATOR ';')
           FROM Study_Subjects s
           LEFT JOIN Study_Topics t ON s.id = t.subject_id
           WHERE s.plan_id = %s
           GROUP BY s.id, s.subject_name""",
        (plan_id,)
    )
    subjects_data = cursor.fetchall()
    cursor.close()
    
    # Build prompt for Gemini
    subjects_info = []
    for subject_id, subject_name, topics_str in subjects_data:
        if topics_str:
            topics = [{'name': t.split('|')[0], 'weightage': float(t.split('|')[1])} for t in topics_str.split(';')]
        else:
            topics = []
        subjects_info.append({'subject': subject_name, 'topics': topics})
    
    prompt = f"""
    Create a personalized study schedule with the following details:
    - Plan Name: {plan_name}
    - Start Date: {start_date}
    - End Date: {end_date}
    - Preferred Study Days per Week: {preferred_days if preferred_days else 'All days'}
    - Subjects and Topics (with initial weightages):
    {json.dumps(subjects_info, indent=2)}

    Please generate a timetable with:
    1. Subject and topic for each entry
    2. From date and to date (normalized across the plan period)
    3. Normalized weightages that sum to 100% (adjust based on preferred study days)
    4. Consider the preferred days when distributing the schedule

    Return the response as a JSON array with entries like:
    [
      {{"subject": "Math", "topic": "Calculus", "from_date": "2025-01-01", "to_date": "2025-01-15", "normalized_weightage": 25}},
      ...
    ]
    """
    
    # Call Gemini API
    api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDMcEA1fkvZ-x8AoI0HTGpKBR2pt-BXu6M')
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        print(f"[DEBUG] API Response Status: {response.status_code}")
        print(f"[DEBUG] API Response: {json.dumps(result, indent=2)}")
        
        # Extract the generated schedule from response
        # Note: Gemini API uses 'candidates' not 'contents'
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content'] and len(candidate['content']['parts']) > 0:
                content = candidate['content']['parts'][0].get('text', '')
                print(f"[DEBUG] Extracted content: {content[:500]}...")
                
                # Parse JSON from response (may be wrapped in ```json ... ```)
                import re
                # First try to extract JSON from markdown code blocks
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
                if not json_match:
                    # If no markdown, try direct JSON array
                    json_match = re.search(r'\[[\s\S]*\]', content)
                
                if json_match:
                    try:
                        json_str = json_match.group(1) if '```' in content else json_match.group(0)
                        schedule = json.loads(json_str)
                        print(f"[DEBUG] Parsed schedule successfully: {len(schedule)} entries")
                        
                        # Store schedule entries in database
                        cursor = mydb.cursor()
                        for entry in schedule:
                            cursor.execute(
                                """INSERT INTO Study_Schedule (user_id, subject, topic, from_date, to_date, normalized_weightage, status)
                                   VALUES (%s, %s, %s, %s, %s, %s, 'scheduled')""",
                                (user_id, entry['subject'], entry['topic'], entry['from_date'], 
                                 entry['to_date'], entry.get('normalized_weightage', 0))
                            )
                        mydb.commit()
                        cursor.close()
                        
                        # Mark plan as submitted
                        cursor = mydb.cursor()
                        cursor.execute(
                            "UPDATE Study_Plans SET status = 'submitted' WHERE id = %s",
                            (plan_id,)
                        )
                        mydb.commit()
                        cursor.close()

                        # After generating the schedule, redirect to the schedule editor for this plan
                        return redirect(url_for('edit_plan', plan_id=plan_id))
                    except json.JSONDecodeError as je:
                        print(f"[DEBUG] JSON Parse Error: {je}")
                        print(f"[DEBUG] Extracted string: {json_str[:200] if 'json_str' in locals() else 'N/A'}")
                        return f"❌ Error parsing JSON from API response: {str(je)}"
                else:
                    print("[DEBUG] No JSON array found in response")
                    return f"❌ Could not parse schedule from API response. Content: {content[:200]}"
            else:
                print(f"[DEBUG] No proper content structure in candidate")
                print(f"[DEBUG] Candidate keys: {candidate.keys()}")
                return "❌ API response missing proper content structure."
        else:
            print(f"[DEBUG] Response structure issue - candidates: {result.get('candidates', [])}")
            return "❌ API returned empty response or unexpected format."
    
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Request Exception: {str(e)}")
        return f"❌ Error calling Gemini API: {str(e)}"
    except Exception as e:
        print(f"[DEBUG] General Exception: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return f"❌ Error: {str(e)}"


# =======================================================
#                   LOGOUT ROUTE
# =======================================================
@app.route('/logout')
def logout():
    """Log out user by clearing session."""
    session.clear()
    return redirect(url_for('landing'))


# =======================================================
#                   DASHBOARD ROUTE
# =======================================================
@app.route('/dashboard')
def dashboard():
    """Main dashboard page with greeting, motivation quote, and graphs."""
    email = session.get('user_email')
    if not email:
        return redirect(url_for('login'))
    
    user_id = get_user_id_from_session(email)
    if not user_id:
        return redirect(url_for('login'))
    
    # Fetch user name
    cursor = mydb.cursor()
    cursor.execute("SELECT First_Name FROM User_Data WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    user_name = result[0] if result else 'Student'
    
    # Fetch all scheduled tasks for this user
    cursor.execute(
        "SELECT subject, topic, from_date, to_date, normalized_weightage, status FROM Study_Schedule WHERE user_id = %s ORDER BY from_date DESC LIMIT 2",
        (user_id,)
    )
    top_tasks = cursor.fetchall()
    
    # Convert to list of dicts
    top_tasks_list = []
    for task in top_tasks:
        top_tasks_list.append({
            'subject': task[0],
            'topic': task[1],
            'from_date': task[2],
            'to_date': task[3],
            'weightage': task[4],
            'status': task[5]
        })
    
    # Fetch today's completion stats (sample data for now - to be updated by todo list dev)
    from datetime import datetime, timedelta
    today = datetime.now().date()
    cursor.execute(
        "SELECT total_tasks, completed_tasks FROM Daily_Progress WHERE user_id = %s AND day_date = %s",
        (user_id, today)
    )
    today_progress = cursor.fetchone()
    
    if today_progress:
        total_today = today_progress[0]
        completed_today = today_progress[1]
    else:
        total_today = 0
        completed_today = 0
    
    # Calculate percentages
    today_completion_pct = int((completed_today / total_today * 100)) if total_today > 0 else 0
    
    # Fetch last 7 days progress for chart
    daily_data = []
    for i in range(6, -1, -1):  # Last 7 days
        day = today - timedelta(days=i)
        cursor.execute(
            "SELECT day_date, total_tasks, completed_tasks, pending_from_previous FROM Daily_Progress WHERE user_id = %s AND day_date = %s",
            (user_id, day)
        )
        record = cursor.fetchone()
        if record:
            day_date, total, completed, pending = record
            daily_pct = int((completed / total * 100)) if total > 0 else 0
            pending_pct = int((pending / total * 100)) if total > 0 else 0
        else:
            day_date = day
            daily_pct = 0
            pending_pct = 0
        
        daily_data.append({
            'date': str(day_date),
            'completed_pct': daily_pct,
            'pending_pct': pending_pct
        })
    
    # Fetch overall stats
    cursor.execute(
        """SELECT COUNT(*) as total_tasks, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
           SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_tasks
           FROM Study_Schedule WHERE user_id = %s""",
        (user_id,)
    )
    stats = cursor.fetchone()
    total_tasks = stats[0] if stats[0] else 0
    completed_tasks = stats[1] if stats[1] else 0
    pending_tasks = stats[2] if stats[2] else 0
    
    cursor.close()
    
    return render_template('dashboard.html', 
                          user_name=user_name,
                          top_tasks=top_tasks_list,
                          today_completion_pct=today_completion_pct,
                          completed_today=completed_today,
                          total_today=total_today,
                          daily_data=daily_data,
                          total_tasks=total_tasks,
                          completed_tasks=completed_tasks,
                          pending_tasks=pending_tasks,
                          active_page='dashboard')


# =======================================================
#                    PLANS ROUTE (View all plans)
# =======================================================
@app.route('/plans')
def view_plans():
    """View all study plans with their schedules."""
    email = session.get('user_email')
    if not email:
        return redirect(url_for('login'))
    
    user_id = get_user_id_from_session(email)
    if not user_id:
        return redirect(url_for('login'))
    
    # Fetch user name
    cursor = mydb.cursor()
    cursor.execute("SELECT First_Name FROM User_Data WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    user_name = result[0] if result else 'Student'
    
    # Fetch all plans for this user
    cursor.execute(
        """SELECT id, plan_name, start_date, end_date, preferred_days, status, created_at 
           FROM Study_Plans WHERE user_id = %s ORDER BY created_at DESC""",
        (user_id,)
    )
    plans = cursor.fetchall()
    
    # For each plan, fetch subjects, topics, and schedule entries
    plans_with_details = []
    for plan_id, plan_name, start_date, end_date, preferred_days, status, created_at in plans:
        # Fetch subjects for this plan
        cursor.execute(
            "SELECT id, subject_name FROM Study_Subjects WHERE plan_id = %s ORDER BY id",
            (plan_id,)
        )
        subjects = cursor.fetchall()
        
        # Fetch schedule entries for this plan
        cursor.execute(
            """SELECT subject, topic, from_date, to_date, normalized_weightage, status 
               FROM Study_Schedule WHERE user_id = %s AND subject IN (
                   SELECT subject_name FROM Study_Subjects WHERE plan_id = %s
               ) ORDER BY from_date""",
            (user_id, plan_id)
        )
        schedule = cursor.fetchall()
        
        plans_with_details.append({
            'id': plan_id,
            'name': plan_name,
            'start_date': start_date,
            'end_date': end_date,
            'preferred_days': preferred_days,
            'status': status,
            'created_at': created_at,
            'subjects': [{'id': s[0], 'name': s[1]} for s in subjects],
            'schedule': [{'subject': s[0], 'topic': s[1], 'from_date': s[2], 'to_date': s[3], 'weightage': s[4], 'status': s[5]} for s in schedule]
        })
    
    cursor.close()
    
    return render_template('plans.html', 
                          user_name=user_name,
                          plans=plans_with_details,
                          active_page='plans')


@app.route('/edit_plan/<int:plan_id>', methods=['GET', 'POST'])
def edit_plan(plan_id):
    """Edit an existing plan and its generated schedule."""
    email = session.get('user_email')
    if not email:
        return redirect(url_for('login'))

    user_id = get_user_id_from_session(email)
    if not user_id:
        return redirect(url_for('login'))

    cursor = mydb.cursor()
    # Fetch plan
    cursor.execute(
        "SELECT id, plan_name, start_date, end_date, preferred_days, status FROM Study_Plans WHERE id = %s AND user_id = %s",
        (plan_id, user_id)
    )
    plan = cursor.fetchone()
    if not plan:
        cursor.close()
        return "Plan not found or you don't have permission to edit it."

    # Handle updates
    if request.method == 'POST':
        # Expecting fields like from_<id>, to_<id>
        updates = []
        for key, value in request.form.items():
            if key.startswith('from_'):
                sid = key.split('_', 1)[1]
                from_date = value
                to_date = request.form.get(f'to_{sid}')
                if from_date and to_date:
                    updates.append((from_date, to_date, sid))

        # Apply updates
        for upd in updates:
            cursor.execute(
                "UPDATE Study_Schedule SET from_date = %s, to_date = %s WHERE id = %s AND user_id = %s",
                (upd[0], upd[1], upd[2], user_id)
            )
        mydb.commit()

    # Fetch subjects and schedule entries
    cursor.execute("SELECT id, subject_name FROM Study_Subjects WHERE plan_id = %s", (plan_id,))
    subjects = cursor.fetchall()

    cursor.execute(
        "SELECT id, subject, topic, from_date, to_date, normalized_weightage, status FROM Study_Schedule WHERE user_id = %s AND subject IN (SELECT subject_name FROM Study_Subjects WHERE plan_id = %s) ORDER BY from_date",
        (user_id, plan_id)
    )
    schedule = cursor.fetchall()
    cursor.close()

    # Convert to dicts
    schedule_list = []
    for s in schedule:
        schedule_list.append({
            'id': s[0], 'subject': s[1], 'topic': s[2], 'from_date': s[3], 'to_date': s[4], 'weightage': s[5], 'status': s[6]
        })

    plan_dict = {
        'id': plan[0], 'name': plan[1], 'start_date': plan[2], 'end_date': plan[3], 'preferred_days': plan[4], 'status': plan[5]
    }

    # Fetch full user name for display
    cursor = mydb.cursor()
    cursor.execute("SELECT First_Name, Last_Name FROM User_Data WHERE id = %s", (user_id,))
    u = cursor.fetchone()
    cursor.close()
    user_name = f"{u[0]} {u[1]}" if u else 'Student'

    return render_template('edit_plan.html', user_name=user_name, plan=plan_dict, subjects=subjects, schedule=schedule_list, active_page='plans')


# =======================================================
#                   ACCOUNT ROUTE
# =======================================================
@app.route('/account', methods=['GET', 'POST'])
def account():
    """Account page for viewing and updating user info."""
    email = session.get('user_email')
    if not email:
        return redirect(url_for('login'))
    
    user_id = get_user_id_from_session(email)
    if not user_id:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_phone':
            phone = request.form.get('phone')
            cursor = mydb.cursor()
            cursor.execute("UPDATE User_Data SET phone = %s WHERE id = %s", (phone, user_id))
            mydb.commit()
            cursor.close()
            message = "✅ Phone number updated successfully!"
            
        elif action == 'change_email':
            new_email = request.form.get('new_email')
            # Check if email already exists
            cursor = mydb.cursor()
            cursor.execute("SELECT id FROM User_Data WHERE email_id = %s", (new_email,))
            if cursor.fetchone():
                cursor.close()
                message = "⚠️ This email is already in use. Please choose a different email."
            else:
                # Generate verification token for email change
                token = s.dumps({'old_email': email, 'new_email': new_email, 'user_id': user_id}, salt='email-change')
                verify_link = url_for('verify_email_change', token=token, _external=True)
                
                msg = Message('Verify Your New Email - Study Planner', recipients=[new_email])
                msg.html = f"""
                <!DOCTYPE html>
                <html>
                  <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                    <div style="max-width: 600px; background-color: white; margin: auto; border-radius: 8px; padding: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                      <h2 style="color: #333; text-align: center;">Verify Your New Email</h2>
                      <p style="color: #555; font-size: 16px;">
                        You requested to change your email address. Click the button below to verify your new email:
                      </p>
                      <div style="text-align: center; margin: 30px 0;">
                        <a href="{verify_link}" 
                           style="background-color: #667eea; color: white; text-decoration: none; 
                                  padding: 12px 25px; border-radius: 6px; display: inline-block; 
                                  font-size: 16px; font-weight: bold;">
                          Verify New Email
                        </a>
                      </div>
                      <p style="color: #666; font-size: 14px;">
                        If the button above doesn't work, copy and paste this link into your browser:<br>
                        <a href="{verify_link}" style="color: #667eea;">{verify_link}</a>
                      </p>
                      <hr style="border: none; border-top: 1px solid #ddd; margin: 25px 0;">
                      <p style="color: #999; font-size: 12px; text-align: center;">
                        This link will expire in 1 hour for security reasons.<br>
                        © 2025 Study Planner. All rights reserved.
                      </p>
                    </div>
                  </body>
                </html>
                """
                mail.send(msg)
                cursor.close()
                message = f"📧 Verification email sent to {new_email}! Please check your inbox."
        
        # Fetch updated user info
        cursor = mydb.cursor()
        cursor.execute("SELECT First_Name, Last_Name, email_id, phone FROM User_Data WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        
        user_name = f"{user_data[0]} {user_data[1]}" if user_data else 'Student'
        
        return render_template('account.html', 
                              user_data=user_data,
                              user_name=user_name,
                              message=message,
                              active_page='account')
    
    # GET request - fetch user info
    cursor = mydb.cursor()
    cursor.execute("SELECT First_Name, Last_Name, email_id, phone FROM User_Data WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    
    user_name = f"{user_data[0]} {user_data[1]}" if user_data else 'Student'
    
    return render_template('account.html', 
                          user_data=user_data,
                          user_name=user_name,
                          active_page='account')


# =======================================================
#              VERIFY EMAIL CHANGE ROUTE
# =======================================================
@app.route('/verify_email_change/<token>')
def verify_email_change(token):
    """Verify and apply the email change."""
    try:
        data = s.loads(token, salt='email-change', max_age=3600)
    except SignatureExpired:
        return "<h3>❌ Verification link expired!</h3>"
    except BadTimeSignature:
        return "<h3>❌ Invalid or tampered token!</h3>"
    
    old_email = data['old_email']
    new_email = data['new_email']
    user_id = data['user_id']
    
    # Update email in database
    cursor = mydb.cursor()
    cursor.execute("UPDATE User_Data SET email_id = %s WHERE id = %s", (new_email, user_id))
    mydb.commit()
    cursor.close()
    
    # Update session
    session['user_email'] = new_email
    
    return f"<h3>✅ Email changed successfully from {old_email} to {new_email}!</h3><a href='/account'><button>Go to Account</button></a>"


# =======================================================
#                   TODO ROUTE
# =======================================================
@app.route('/todo', methods=['GET', 'POST'])
def todo():
    """To-do list page - Shows daily topics from study schedule."""
    email = session.get('user_email')
    if not email:
        return redirect(url_for('login'))
    
    user_id = get_user_id_from_session(email)
    if not user_id:
        return redirect(url_for('login'))
    
    from datetime import datetime
    today = datetime.now().date()
    
    # Fetch user name
    cursor = mydb.cursor()
    cursor.execute("SELECT First_Name, Last_Name FROM User_Data WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    user_name = f"{result[0]} {result[1]}" if result else 'Student'
    
    # Fetch today's topics from Study_Schedule and related plan id (via Study_Subjects)
    cursor.execute("""
        SELECT s.id, s.subject, s.topic, s.from_date, s.to_date, s.normalized_weightage, s.status, sub.plan_id
        FROM Study_Schedule s
        LEFT JOIN Study_Subjects sub ON s.subject = sub.subject_name AND sub.user_id = s.user_id
        WHERE s.user_id = %s AND s.from_date <= %s AND s.to_date >= %s
        ORDER BY s.subject, s.topic
    """, (user_id, today, today))
    
    today_topics = []
    for row in cursor.fetchall():
        today_topics.append({
            'id': row[0],
            'subject': row[1],
            'topic': row[2],
            'from_date': row[3],
            'to_date': row[4],
            'weightage': row[5],
            'status': row[6],
            'plan_id': row[7]
        })
    
    # Handle mark as done/skip actions
    if request.method == 'POST':
        action = request.form.get('action')
        topic_id = request.form.get('topic_id')
        
        if action == 'mark_done':
            cursor.execute(
                "UPDATE Study_Schedule SET status = 'completed' WHERE id = %s AND user_id = %s",
                (topic_id, user_id)
            )
        elif action == 'skip':
            cursor.execute(
                "UPDATE Study_Schedule SET status = 'skipped' WHERE id = %s AND user_id = %s",
                (topic_id, user_id)
            )
        
        mydb.commit()
        cursor.close()
        
        # Refresh today's topics
        cursor = mydb.cursor()
        cursor.execute("""
            SELECT id, subject, topic, from_date, to_date, normalized_weightage, status 
            FROM Study_Schedule 
            WHERE user_id = %s AND from_date <= %s AND to_date >= %s 
            ORDER BY subject, topic
        """, (user_id, today, today))
        
        today_topics = []
        for row in cursor.fetchall():
            today_topics.append({
                'id': row[0],
                'subject': row[1],
                'topic': row[2],
                'from_date': row[3],
                'to_date': row[4],
                'weightage': row[5],
                'status': row[6]
            })
    
    cursor.close()
    
    # Calculate today's stats
    total_topics = len(today_topics)
    completed_topics = len([t for t in today_topics if t['status'] == 'completed'])
    pending_topics = len([t for t in today_topics if t['status'] not in ['completed', 'skipped']])
    skipped_topics = len([t for t in today_topics if t['status'] == 'skipped'])
    
    completion_pct = int((completed_topics / total_topics * 100)) if total_topics > 0 else 0
    
    return render_template('todo.html', 
                          user_name=user_name,
                          today_topics=today_topics,
                          total_topics=total_topics,
                          completed_topics=completed_topics,
                          pending_topics=pending_topics,
                          skipped_topics=skipped_topics,
                          completion_pct=completion_pct,
                          today_date=str(today),
                          active_page='todo')


# =======================================================
#                   MAIN RUN
# =======================================================
if __name__ == '__main__':
    app.run(debug=True)

