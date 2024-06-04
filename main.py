from bs4 import BeautifulSoup
import requests, openpyxl
import pandas as pd
import re

with open('path.txt', 'r') as file:
    path = file.readline().strip()

def check(link, currentQ, lastQ):    
    try:
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
        source = requests.get(link, headers=headers)
        soup = BeautifulSoup(source.text,'html.parser')

        #from time import sleep
        #from selenium import webdriver
        
        #edge_options = webdriver.EdgeOptions()
        #edge_options.add_argument('headless')
        #driver = webdriver.Edge(options=edge_options)
        
        #driver.get(link)
        #sleep(5)
        #soup = BeautifulSoup(driver.page_source,'html.parser')

        p = soup.find_all(string= re.compile(str(lastQ)))
        c = soup.find_all(string= re.compile(currentQ))

        if p == [] and lastQ != "nan":
            print("Error")
            return("Error")
        else:
            if c == []:
                print("Negative")
                return("Negative")
            else:
                print("Positive")
                return("Positive")
    except Exception as e:
        print("Error in fetching data from " + link + "\n\n" + str(e))
        return("FetchingError")


def send_email(email_id, xl_data, xl_old_data):
    from email.message import EmailMessage
    import smtplib
    from datetime import date

    result_str = xl_data[["Name", "Result"]].to_string()
    li = []


    for i in range(len(xl_data)):
        if xl_data.iloc[i]['Result'] == "Positive" and xl_old_data.iloc[i]['Result'] == "Negative":
            li.append(xl_data.iloc[i]['Name'])
        
    f= open("pass.txt","r") #pass.txt file should contain two lines - email id and password
    contents = f.readlines()
    f.close()

    username = contents[0].strip()
    password = contents[1].strip()


    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(username,password)

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

    message = message +"\n\n" + result_str + "\n\nRegards\nArpan"

    msg.set_content(message)
    print(message)
    s.send_message(msg)
    s.quit()





if __name__ == '__main__':

    xl_data = pd.read_excel(path, sheet_name="Sheet1")  #read excel
    xl_old_data = xl_data

    for i in range(0,len(xl_data)):
        current_result = xl_data.Result[i]
        link = xl_data.Link[i]
        name = xl_data.Name[i]
        #tag = xl_data.tag[i]
        currentQ = str(xl_data.CurrentQ[i])
        lastQ = str(xl_data.LastQ[i])

        if (((current_result == "Negative") or  (current_result == "Error")) and (currentQ != 'nan')):
            result = check(link, currentQ, lastQ)
            xl_data.at[i,'Result']=result

    xl_data.to_excel(path, sheet_name='Sheet1', index=False)  #Write excel      

    emails = xl_data["Email"].unique().tolist()

    for email in emails:
        send_email(email, xl_data.loc[xl_data['Email'] == email], xl_old_data.loc[xl_old_data['Email'] == email])
