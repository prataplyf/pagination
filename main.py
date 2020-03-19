from flask import Flask, render_template, request, url_for, redirect
from flask_table import Table, Col
import pymongo # for connect with database
import datetime
import time
import pytz
import tzlocal
import sys
from flask_paginate import Pagination, get_page_args
########### datetime
current = datetime.datetime.now()
utc= datetime.datetime.utcnow()
local_timezone = tzlocal.get_localzone()
tt = utc.replace(tzinfo=pytz.utc).astimezone(local_timezone)

myclient = pymongo.MongoClient("mongodb+srv://prataplyf:Ashish12@ashish-hbjy0.mongodb.net/test?retryWrites=true&w=majority")
mydb = myclient["Employee"]
mycol = mydb["data"]

app = Flask(__name__)
# app.template_folder = ''
# users = list(range(100))
global endline
endline = 0


# def get_users(offset=0, per_page=10):
#     return users[offset: offset + per_page]

@app.route('/',methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        cnum = int(request.form.get('cnum'))
        TimeStamp = tt
        empid = mycol.find().count() + 1

        mycol.insert_one({"_id":empid , "Email": email, "Name":name, "Contact Number":cnum, "TimeStamp": TimeStamp })
        message = "Successfully saved data"
        return render_template('index.html', message=message)
    
    return render_template('index.html')

  
@app.route('/search', methods=['POST', 'GET'])
def search():
    count = 0
    if request.method == 'POST':
        data = request.form.get('search')
        if data in (temp['Name'] for temp in mycol.find({'Name':{'$regex': data}})):
            namelist = []
            for entry in mycol.find({'Name':{'$regex': data}},{"Name":1, "Email":1, "Contact Number":1, "_id":1, "TimeStamp":1}):
                count += 1
                empid = entry['_id']
                namelist.append({"id":empid, "name": entry['Name'], "email": entry["Email"], "contact": entry['Contact Number'], "time": entry['TimeStamp']})
            
            msg = data
            text = "Users Found with Name:"
            limit = 2
            return render_template('search.html', data = namelist, count = count, message=msg, text=text, limit=limit)


        # checking for Email
        elif data in [temp['Email'] for temp in mycol.find({'Email':{'$regex': data}})]:
            emaillist = []
            for entry in mycol.find({'Email':{'$regex': data}},{"Name":1, "Email":1, "Contact Number":1, "_id":1, "TimeStamp":1}):
                count += 1
                empid = entry['_id']
                emaillist.append({"id":empid, "name": entry['Name'], "email": entry["Email"], "contact": entry['Contact Number'], "time": entry['TimeStamp']})
            msg = data
            text = "Users Found with Email:"
            limit = 2
            return render_template('search.html', data = emaillist, count = count, message=msg,  text = text, limit=limit)
        
        else: # if search data didn't found
            count = 0
            msg = data
            text = 'No Records Found with Name/Email: '
            return render_template('search.html', message = msg, count = count, text=text)
    
    # Get All Records to show on the Dashboard
    
    global endline
    limit = 5
    alldata = []
    for entry in mycol.find({},{"Name":1, "Email":1, "Contact Number":1, "_id":1, "TimeStamp":1}):            
        empid = entry['_id']
        if count < limit:
            count += 1
            endline = empid
            alldata.append({"id":empid, "name": entry['Name'], "email": entry["Email"], "contact": entry['Contact Number'], "time": entry['TimeStamp']})
        else:
            pass              
    msg = ' Records'
    print('Last EmpID: ', endline) 
    return render_template('search.html', data = alldata, count = count, message=msg)
    

@app.route('/search/nextpage', methods=['POST', 'GET'])
def nextpage():
    global endline
    alldata = []
    count = 0
    limit = 5
    row = mycol.find().count()
    if endline != row:
        for entry in mycol.find({"_id":{ '$gt': endline }},{"Name":1, "Email":1, "Contact Number":1, "_id":1, "TimeStamp":1}):            
            empid = entry['_id']
            if count < limit:
                count += 1
                endline = empid
                alldata.append({"id":empid, "name": entry['Name'], "email": entry["Email"], "contact": entry['Contact Number'], "time": entry['TimeStamp']})
            else:
                pass              
        msg = ' Records'
        print('Last EmpID: ', endline) 
        return render_template('search.html', data = alldata, count = count, message=msg)
    else:
        return lastpage()


@app.route('/search/prevpage', methods=['POST', 'GET'])
def prevpage():
    global endline
    alldata = []
    count = 0
    limit = 5
    if endline % 5 != 0:
        endline -= endline % 5
        endline -= limit
    else:
        endline -= limit * 2   
    
    # print('Last EmpID: ', endline) 
    for entry in mycol.find({"_id":{ '$gt': endline } },{"Name":1, "Email":1, "Contact Number":1, "_id":1, "TimeStamp":1}):
        empid = entry['_id']
        if count < limit:
            count += 1
            endline = empid
            # print('Last EmpID: ', endline) 
            alldata.append({"id":empid, "name": entry['Name'], "email": entry["Email"], "contact": entry['Contact Number'], "time": entry['TimeStamp']})
        else:
            pass
    msg = ' Records'
    print('Last EmpID: ', endline) 
    return render_template('search.html', data = alldata, count = count, message=msg)


@app.route('/search/last', methods=['POST', 'GET'])
def lastpage():
    global endline
    alldata = []
    count = 0
    limit = 5
    endline = mycol.find().count()
    endline -= endline % 5 
    
    # print('Last EmpID: ', endline) 
    for entry in mycol.find({"_id":{ '$gt': endline } },{"Name":1, "Email":1, "Contact Number":1, "_id":1, "TimeStamp":1}):
        empid = entry['_id']
        if count < limit:
            count += 1
            endline = empid
            # print('Last EmpID: ', endline) 
            alldata.append({"id":empid, "name": entry['Name'], "email": entry["Email"], "contact": entry['Contact Number'], "time": entry['TimeStamp']})
        else:
            pass
    msg = ' Records'
    print('Last EmpID: ', endline) 
    return render_template('search.html', data = alldata, count = count, message=msg)

if __name__== "__main__":
    app.run(debug=True)