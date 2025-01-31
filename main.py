from bs4 import BeautifulSoup
#import requests, openpyxl
import pandas as pd
import re
from config import *
from time import sleep
from datetime import datetime
from selenium import webdriver 
from send_email import send_email
import requests
from urllib.parse import urlparse
import logging
import os

path = INPUT_PATH      #path of input file

def init_driver(driver_type):
    if driver_type == "edge":
        from selenium.webdriver.edge.service import Service
        driver_path = WEBDRIVER_PATH_EDGE
        edge_options = webdriver.EdgeOptions()
        edge_options.add_argument('headless')
        edge_options.add_argument("--start-maximized")
        service = Service(executable_path=driver_path)
        driver = webdriver.Edge(service=service, options=edge_options)

    elif driver_type == "chrome":
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.chrome.options import Options
        chromedriver_path = WEBDRIVER_PATH_CHROME
        custom_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        chrome_options = Options()
        chrome_options.binary_location = CHROME_BINARY_LOCATION
        chrome_options.add_argument(f'user-agent={custom_user_agent}')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')  # Required for certain Linux environments
        chrome_options.add_argument('--disable-dev-shm-usage')  # Prevents shared memory issues
        service = ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)        

    return driver


def check(link, currentQ, lastQ, driver):    
    link_domain = urlparse(link).netloc
    try:
        if driver==None:
            print(f"Checking {link_domain} using requests and beautifulsoup")
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
            source = requests.get(link, headers=headers)
            soup = BeautifulSoup(source.text,'html.parser')
        else:
            print(f"Checking {link_domain} using selenium")
            driver.get(link)
            sleep(5)
            soup = BeautifulSoup(driver.page_source,'html.parser')

        try:
            p = soup.find_all(string= re.compile(str(lastQ)))
            c = soup.find_all(string= re.compile(currentQ))
        except Exception as e:
            print("Error in finding data from " + link_domain + "\n\n" + str(e))
            return("Error")

        if p == [] and lastQ != "nan":
            print(f"Error: {link_domain}")
            return("Error")
        else:
            if c == []:
                print(f"Negative {link_domain}")
                return("Negative")
            else:
                print(f"Positive {link_domain}")
                return("Positive")
    except Exception as e:
        print("Error in fetching data from " + link_domain + "\n\n" + str(e))
        return("FetchingError")


if __name__ == '__main__':
    if not os.path.exists('logs'):
        os.makedirs('logs')
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = f'logs/WebAlertify_log_{current_time}.log'
    logging.basicConfig(filename=log_filename, level=logging.INFO)
    logging.info('Started. Reading data.')
    xl_data = pd.read_excel(path, sheet_name="Sheet1")  #read excel
    xl_old_data = xl_data

    if WHICHDRIVER == "requests":
        logging.info('Checking using requests and beautifulsoup')
        driver = None
    else:
        driver = init_driver(WHICHDRIVER)
        logging.info(f'Checking using {WHICHDRIVER}. Starting Driver.')

    for i in range(0,len(xl_data)):
        current_result = xl_data.Result[i]
        link = xl_data.Link[i]
        name = xl_data.Name[i]
        #tag = xl_data.tag[i]
        currentQ = str(xl_data.CurrentQ[i])
        lastQ = str(xl_data.LastQ[i])

        if ((((current_result == "Negative") or  (current_result == "FetchingError")) or (current_result == "Error") ) and (currentQ != 'nan')):
            logging.info(f'Checking {name} at {link}')
            result = check(link, currentQ, lastQ, driver)
            xl_data.at[i,'Result']=result
        else:
            logging.info(f'Not checking {name} at {link}')
            print("Not Checking:" + name )

    if WHICHDRIVER != "requests":
        logging.info('Quitting driver')
        driver.quit()
    
    logging.info('Checking complete. Writing data to file')
    xl_data.to_excel(path, sheet_name='Sheet1', index=False)  #Write excel      
    logging.info('Writing complete. Sending emails')


    emails = xl_data["Email"].unique().tolist()

    for email in emails:
        response = send_email(email, xl_data.loc[xl_data['Email'] == email], xl_old_data.loc[xl_old_data['Email'] == email])

