from flask_mail import Message

def send_email_verification(app, email, token):
    from app import mail
    with app.app_context():
        msg = Message(
            subject="Verify Your Email - Study Planner",
            sender="shlok.divyam@gmail.com",   # ✅ match SendGrid verified sender
            recipients=[email],
            body=f"Click here to verify your email: http://localhost:5000/verify/{token}"
        )
        mail.send(msg)

def send_password_reset(app, email, token):
    from app import mail
    with app.app_context():
        msg = Message(
            subject="Password Reset - Study Planner",
            sender="shlok.divyam@gmail.com",   # ✅ same sender
            recipients=[email],
            body=f"Click here to reset your password: http://localhost:5000/reset/{token}"
        )
        mail.send(msg)

