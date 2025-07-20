import pandas as pd
import awsgi
import boto3
from flask import Flask, render_template, redirect, url_for, request, render_template_string, make_response
import hashlib
import os


xl_data = None

action=None
link = None
name = None
currentQ = None
lastQ = None
email = None
delete_row = None

app = Flask(__name__)


# Dummy credentials
password = os.environ.get("login_password")
USERNAME = os.environ.get("login_id")
PASSWORD_HASH = hashlib.sha256(password.encode()).hexdigest()

def is_logged_in(request):
    return request.cookies.get("auth") == PASSWORD_HASH

@app.route("/")
def home():
    return render_template('home.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == USERNAME and hashlib.sha256(password.encode()).hexdigest() == PASSWORD_HASH:
            resp = make_response(redirect("/dev/dashboard"))
            resp.set_cookie("auth", PASSWORD_HASH)
            return resp
        return "Invalid credentials", 401

    # HTML form for login
    return render_template("login.html")


@app.route('/dashboard', methods=['GET', 'POST'])
def index():
    if not is_logged_in(request):
        return redirect("/dev/login")
    global xl_data
    
    #Save File to /tmp/
    s3 = boto3.resource('s3')
    s3.meta.client.download_file("webalertify", "DateCheck.xlsx", "/tmp/DateCheck.xlsx" )
    xl_data = pd.read_excel("/tmp/DateCheck.xlsx")

    #xl_data = pd.read_excel(path, sheet_name="Sheet1")  #read excel
    
    if request.method == 'POST':
        global action 
        action= request.form.get('action')
        global link 
        link = request.form.get('link')
        global name 
        name = request.form.get('name')
        global currentQ
        currentQ = request.form.get('currentQ')
        global lastQ 
        lastQ = request.form.get('lastQ')
        global email 
        email = request.form.get('email')
        global delete_row 
        delete_row = request.form.get('dropdown')  
        
        if action == 'check_link':
            #return redirect(url_for('checklink'))
            from main import check
            result = check(link, currentQ, lastQ)
            return "Result: " + result 

        elif action == 'Add':
            #return redirect(url_for('add'))
            new_row = {"Link":link, "Name":name, "CurrentQ":currentQ ,"LastQ":lastQ, "Result":"Negative", "Email":email }
            xl_data.loc[len(xl_data)] = new_row
            xl_data.to_excel("/tmp/DateCheck.xlsx", sheet_name="Sheet1", index=False)
            
            #Upload file from /tmp/
            bucket = s3.Bucket('webalertify')
            bucket.upload_file("/tmp/DateCheck.xlsx", "DateCheck.xlsx")
            
            return "Added " + name


        elif action == 'delete':
            #global xl_data
            xl_data = xl_data[xl_data["Link"] != delete_row]
            xl_data.to_excel("/tmp/DateCheck.xlsx", sheet_name="Sheet1", index=False)
            
            #Upload file from /tmp/
            bucket = s3.Bucket('webalertify')
            bucket.upload_file("/tmp/DateCheck.xlsx", "DateCheck.xlsx")
            return "Deleted " + delete_row
            
            #return redirect(url_for('delete'))
            
        else:
            #return redirect(url_for('index'))
            return redirect('/dev/')
        

    unique_index = xl_data.iloc[:, 0].tolist()
    dropdown_options=[]
    for item in unique_index:
        dropdown_options.append((item, item))
    return render_template('table.html', tables=[xl_data.to_html(classes='data')], titles=xl_data.columns.values, dropdown_options = dropdown_options)



@app.route('/runnemail', methods=['GET'])
def runnemail():
    from main import runall
    runall()
    
    #with open('main.py', 'r') as file:
    #    code = file.read()
    #exec(code)
    return "Success. Check Email. " 

@app.route('/testurl', methods=['GET'])
def testurl():
    return "Test Success."

@app.route('/steps')
def steps():
    return render_template('steps.html')

@app.route("/logout")
def logout():
    resp = make_response(redirect("/dev/login"))
    resp.set_cookie("auth", "", expires=0)
    return resp

def lambda_handler(event, context):
    return awsgi.response(app, event, context)