import smtplib

# Email and SMTP settings
smtp_server = 'smtpout.secureserver.net'
smtp_port = 465
email_address = 'alerts@webalertify.com'  # Replace with your email
email_password = 'Zxcvbnm@1993'  # Replace with your password
recipient_email = 'arpanbid1@yahoo.com'  # Replace with the recipient's email

# Email content
subject = 'Test Email from Python'
body = 'This is a test email sent from Python!'

# Create the email
email_message = f"Subject: {subject}\n\n{body}"

# Establish a secure connection with the SMTP server and send the email
try:
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(email_address, email_password)
        server.sendmail(email_address, recipient_email, email_message)
        print('Email sent successfully!')
except Exception as e:
    print(f'Failed to send email: {e}')
