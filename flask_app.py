import pandas as pd
import csv
from flask import Flask, render_template, redirect, url_for, request, session
from werkzeug.security import check_password_hash, generate_password_hash

with open('path.txt', 'r') as file:
    path = file.readline().strip()

xl_data = None

action=None
link = None
name = None
currentQ = None
lastQ = None
email = None
delete_row = None

app = Flask(__name__)


users = {}

def read_user_credentials():    
    with open('Data/users.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:  # Ensure there are two elements in the row
                username, password = row
                users[username] = {'username': username, 'password': generate_password_hash(password)}
    


def is_authenticated(username, password):
    read_user_credentials()
    user = users.get(username)
    if user and check_password_hash(user['password'], password):
        return True
    return False

@app.route("/")
def home():
    if 'username' in session:
        return f'Hello, {session["username"]}! <a href="/dashboard">Dashboard</a> | <a href="/logout">Logout</a>'
    return 'Welcome! Please <a href="/login">login</a>.'

@app.route('/login', methods=['GET', 'POST'])
def login():
    read_user_credentials()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if is_authenticated(username, password):
            session['username'] = username
            return redirect('/dashboard')
        return 'Login failed. <a href="/login">Try again</a>'
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with open('Data/users.csv', mode='a', newline='') as file:  #save user credentials in a csv file
            writer = csv.writer(file)
            writer.writerow([username, password])
        
        return 'Registration Success. <a href="/login">Login</a>'  #success page after registration
    return render_template('signup.html')

@app.route('/dashboard')
def index():
    if 'username' in session:
        global xl_data
        xl_data = pd.read_excel(path, sheet_name="Sheet1")  #read excel
        unique_index = xl_data.iloc[:, 0].tolist()
        dropdown_options=[]
        for item in unique_index:
            dropdown_options.append((item, item))
        return render_template('table.html', tables=[xl_data.to_html(classes='data')], titles=xl_data.columns.values, dropdown_options = dropdown_options)
    return render_template('login.html')

@app.route('/checklink')
def checklink():
    from main import check
    result = check(link, currentQ, lastQ)
    return "Result: " + result 


@app.route('/add')
def add():
    new_row = {"Link":link, "Name":name, "CurrentQ":currentQ ,"LastQ":lastQ, "Result":"Negative", "Email":email }
    xl_data.loc[len(xl_data)] = new_row
    xl_data.to_excel(path, sheet_name="Sheet1", index=False)
    return "Added " + name

@app.route('/delete')
def delete():
    global xl_data
    xl_data = xl_data[xl_data["Link"] != delete_row]
    xl_data.to_excel(path, sheet_name="Sheet1", index=False)
    return "Deleted " + delete_row

@app.route('/handle_form', methods=['POST'])
def handle_form():
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
        return redirect(url_for('checklink'))
    elif action == 'Add':    
        return redirect(url_for('add'))
    elif action == 'delete':    
        return redirect(url_for('delete'))
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = 'secretivekey'
    app.run(debug=True) #use (host='0.0.0.0', port=3000) while using this on AWS EC2









#def lambda_handler(event, context):
#    return awsgi.response(app, event, context)