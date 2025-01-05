from flask_mailman import EmailMessage

def send_email(recipient, subject, body):
    email = EmailMessage(
        to=recipient,
        subject=subject,
        body=body
    )

    email.send()

    
