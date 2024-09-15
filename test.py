
import csv

users={}
with open('Data/users.csv', mode='r', newline='') as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) == 3:  # Ensure there are three elements in the row
            emailid ,username, password = row
            users[username] = {'emailid': emailid, 'username': username, 'password':password}

print(users[session['username']]["emailid"])
print(users)