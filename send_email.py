import pandas as pd
from config import *
from email.message import EmailMessage
import smtplib
from datetime import date

username = EMAIL
password = PASSWORD


def send_email(email_id, xl_data, xl_old_data):
    result_str = xl_data[["Name", "Result"]].to_string()
    li = []


    for i in range(len(xl_data)):
        if xl_data.iloc[i]['Result'] == "Positive" and xl_old_data.iloc[i]['Result'] == "Negative":
            li.append(xl_data.iloc[i]['Name'])
        
    #try:
    s = smtplib.SMTP('smtp.gmail.com', 587) #smtp.gmail.com, 587
    s.starttls()
    stmp_response = s.login(username,password)
    print("Login response: " + str(stmp_response[0]))
    print("Smtp Status: " + str(s.ehlo()[0]))
    print("Authenticated")
    # except Exception as e:
    #     print("Error in authenticating. \n\n")
    #     print(e)
    #     return stmp_response
    
    msg = EmailMessage()
    msg["Subject"] = "Operator Releases - " + str(date.today())
    msg["From"] = "Arpan Bid <arpan.bid.1993@gmail.com>"
    msg["To"] = str(email_id)


    if len(li)==0:
        message = "Hi there,\nNo new releases.\n"
    else:
        message = "Hi there,\nThe following operators have released the results:\n"
        for item in li:
            message = message + str(item+"\n")

    message = message +"\n\n" + result_str + "\n\nWebAlertify"

    msg.set_content(message)
    print(message)
    
    try:
        smtp_email_status = s.send_message(msg)            # Uncheck this before using this to email contacts
        print("Send email ststus: " + str(smtp_email_status))   
    except Exception as e:
        print("Error in sending email. \n\n")
        print(e)
        return
    
    if smtp_email_status == {}:
        print("Email sent successfully to " + email_id)
    else:
        print("Error in sending email to " + smtp_email_status)
    
    smtp_quit_status = s.quit()
    print("Quit status: " + str(smtp_quit_status[0]))
    return smtp_quit_status