import pandas as pd
from flask import Flask, render_template, redirect, url_for, request

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

@app.route('/')
def index():
    global xl_data
    xl_data = pd.read_excel(path, sheet_name="Sheet1")  #read excel
    unique_index = xl_data.iloc[:, 0].tolist()
    dropdown_options=[]
    for item in unique_index:
        dropdown_options.append((item, item))
    return render_template('table.html', tables=[xl_data.to_html(classes='data')], titles=xl_data.columns.values, dropdown_options = dropdown_options)

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
    app.run(debug=True)









#def lambda_handler(event, context):
#    return awsgi.response(app, event, context)