import os

EMAIL = os.environ.get('gmail_id')
PASSWORD = os.environ.get('gmail_password')

WEBDRIVER_PATH_EDGE = "C:/Users/BidA/Documents/PY/WebDrivers/msedgedriver.exe"

WEBDRIVER_PATH_CHROME = "/home/ubuntu/MyApps/PeopleStrongPunchInOut/ChromeDriver/chromedriver-linux64/chromedriver"
CHROME_BINARY_LOCATION = "/usr/bin/google-chrome"

WHICHDRIVER = "edge" # or "chrome" or "requests"

INPUT_PATH = "Data/DateCheck.xlsx"