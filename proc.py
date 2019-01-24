from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug import secure_filename
import MySQLdb
import pandas as pd
import shutil
import os
import csv
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
APP_ROOT=os.path.dirname(os.path.abspath(__file__))

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct

app = Flask(__name__, template_folder='template')
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/reg", methods=['POST','GET'])
def registration():
	if request.method=='POST':
		uname=request.form['username']
		pwd=request.form['password']
		conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "root",
                           db = "bucketlist")
		c = conn.cursor()
		register=("Insert into reg(uname,pwd) values(%s,%s)")
		c.execute(register,(uname,pwd))
		data=uname
		conn.commit()
		conn.close()	
		return render_template("login.html", data=data)

@app.route("/login",methods=['POST','GET'])
def login():
	if request.method=='POST':
		uname=request.form['username']
		pwd=request.form['password']
		if(uname=='admin' and pwd=='admin'):
			return render_template('adminlogin.html')
		else:
			conn = MySQLdb.connect(host="localhost",
	                           user = "root",
	                           passwd = "root",
        	                   db = "bucketlist")
			c = conn.cursor()
			c.execute("SELECT * FROM reg WHERE uname =%s", [uname])
			data1=c.fetchone()				
			try:			
				pas=data1[2]
			except:
				return render_template('home.html')
			if pwd.encode('utf-8')==pas.encode('utf-8'):
				app.logger.info('PassWord Matched')
				data=uname
				c.close()
				return render_template("login.html",data=data)
			else:
				return render_template("home.html")	
			

@app.route("/form",methods=['POST','GET'])
def fileaccess():
	if request.method=='POST':
		file = request.files['csv_info']
		file.filename="hello.csv"
		file.save(secure_filename(file.filename))
		f=open(file.filename)
		data=[{k:v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]
		return render_template('data.html',
                           title='CSV to table',
                           # df to list format
                           data = data)

@app.route('/services', methods=['GET', 'POST'])
def services():
	file=pd.read_csv("hello.csv")    
	new_id=[]
	for k,v in file['id'].value_counts().items():
		if v>50:
			new_id.append(k)
	file= file.loc[file['id'].isin(new_id)]
	file= file.drop_duplicates(subset=['id','reviews.username'], keep=False)
	file=file.dropna()
	name=file['reviews.username']
	l=[]
	for i in name:
		l.append(not(i[0].isdigit()))
	file=file[l]		
	file.to_csv("hello1.csv")	
	f=open("hello1.csv")
	data=[{k:v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]	
	return render_template("review.html",data=data)

@app.route('/presents',methods=['GET','POST'])
def presents():
	data=os.listdir('./static')
	return render_template("graph1.html",data=data)

@app.route('/identify', methods=['GET', 'POST'])
def identify	():
	file=pd.read_csv("hello.csv")    
	new_id=[]
	spam_id=[]
	for k,v in file['id'].value_counts().items():
		if v>50:
			new_id.append(k)
		else:
			spam_id.append(k)
	spam_file=file.loc[file['id'].isin(spam_id)]
	file= file.loc[file['id'].isin(new_id)]
	sp=file.duplicated(subset=['id','reviews.username'], keep=False)
	sp=file[sp]
	file= file.drop_duplicates(subset=['id','reviews.username'], keep=False)
	file=file.dropna()	
	name=file['reviews.username']
	l=[]
	for i in name:
		l.append(i[0].isdigit())
	file=file[l]
	file=file.dropna()	
	frames=[spam_file,sp,file]
	res=pd.concat(frames)		
	res.to_csv("hello2.csv")	
	f=open("hello2.csv")
	data=[{k:v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]	
	return render_template("Spam.html",data=data)

@app.route('/service', methods=['GET', 'POST'])
def service():
	file=pd.read_csv("hello.csv")    
	new_id=[]
	for k,v in file['id'].value_counts().items():
		if v>50:
			new_id.append(k)
	file= file.loc[file['id'].isin(new_id)]
	file= file.drop_duplicates(subset=['id','reviews.username'], keep=False)
	file=file.dropna()
	name=file['reviews.username']
	l=[]
	for i in name:
		l.append(not(i[0].isdigit()))
	file=file[l]		
	file.to_csv("hello1.csv")	
	f=open("hello1.csv")
	data=[{k:v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]	
	return render_template("service.html",data=data)


@app.route('/present',methods=['GET','POST'])
def present():
	target=os.path.join(APP_ROOT,'static/')
	#if os.path.isdir(target):
	#	shutil.rmtree(target,ignore_errors=True)
	if not os.path.isdir(target):
		os.mkdir(target)
	data=pd.read_csv("hello1.csv")
	d=data.loc[:,['dateAdded','name','reviews.date','reviews.rating']]
	d=d.sort_values(by=['name','reviews.date'])
	names=[]
	for i in data['name']:
		if i not in names:
			names.append(i)
	count=0	
	for i in names:
		g=d['name']==i		
		for k in g:
			if k:
				count+=1
	print(count)
	early=int(count*0.16)
	print(early)
	majority=int(count*0.84-count*0.16)
	print(majority)
	laggards=int(count-count*0.84)
	print(laggards)
	list1=['Early','Majority','laggards']
	list2=[early,majority,laggards]
	print(list2)
	width=1/1.5
	plt.bar(list1, list2, width, alpha=0.75)
	name="Bar.jpg"
	destination="/".join([target,name])
	#print (destination)
	plt.savefig(destination)
	labels = 'Early', 'Mojority', 'laggards'
	sizes = list2
	print(sizes)
	explode = (0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
	fig1, ax1 = plt.subplots()
	ax1.pie(sizes, explode=explode, labels=labels,autopct=make_autopct(sizes),
        shadow=True, startangle=90)
	ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
	name1="Pie.jpg"
	destination="/".join([target,name1])
	#print (destination)
	plt.savefig(destination)
	data=os.listdir('./static')
	return render_template("graph.html",data=data)	
		

if __name__ == "__main__":
    app.run(debug=True)

