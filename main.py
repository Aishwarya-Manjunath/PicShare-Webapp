from flask import Flask,render_template,request,request,session,redirect,url_for
from flask_pymongo import PyMongo
import datetime
from werkzeug import secure_filename
import os

app=Flask(__name__)

app.config['MONGO_DBNAME']='ccbd'

mongo=PyMongo(app)

app.config['UPLOAD_FOLDER']=os.path.abspath('./static/pictures/')
ALLOWED_EXT=set(['.jpeg','.jpg','.png'])

@app.route('/',methods=['GET'])
def index():
	return render_template('index.html',exist=0,wpwd=0,nouser=0)

@app.route('/signup',methods=['POST','GET'])
def signup():
	user1=request.form['uname']
	email=request.form['email']
	pwd=request.form['pwd']
	fname=request.form['fname']
	dob=request.form['dob']
	#print(user,email,pwd)
	
	User=mongo.db.User
	#print(User)
	exist_user=User.find_one({'User_Name':user1})
	#print(exist_user)
	
	if exist_user is None:
		User.insert({'Full_Name':fname,'DOB':dob,'User_Name':user1,'Password':pwd,'Email_Id':email})
		Requests=mongo.db.requests
		Requests.insert({'User_Name':user1,'rqt_usr':[]})
		Friends=mongo.db.friends
		Friends.insert({'User_Name':user1,'frnd_usr':[]})
		mongo.db.pictures.insert({'usr_name':user1,'pics':[],'time':[]})
		mongo.db.sent_request.insert({'User_Name':user1,'request':[]})
		#session['User_Name']=user1
		global user
		user=user1
		return redirect(url_for('newsfeed'))
	
	return render_template('index.html',exist=1,wpwd=0,nouser=0)

@app.route('/login',methods=['POST','GET'])
def login():
	user1=request.form['uname']
	pwd=request.form['pwd']
	
	User=mongo.db.User
	exist_user=User.find_one({'User_Name':user1})
	
	if exist_user is None:
		
		return render_template('index.html',exist=0,wpwd=0,nouser=1)
	
	correct_pwd=User.find_one({'User_Name':user1})
	if(correct_pwd['Password']==pwd):
		global user
		user=user1
		return redirect(url_for('newsfeed'))
	else:
		return render_template('index.html',exist=0,wpwd=1,nouser=0)
		
@app.route('/newsfeed',methods=['POST','GET'])
def newsfeed():
	my_frnds=mongo.db.friends.find_one({'User_Name':user})['frnd_usr']
	l=[]
	for i in my_frnds:
		p=mongo.db.pictures.find_one({'usr_name':i})['pics']
		t=mongo.db.pictures.find_one({'usr_name':i})['time']
		if len(p)<3:
			for j in range(0,len(p)):
				y=[]
				y.append(i)
				y.append(p[j])
				y.append(t[j])
				l.append(y)
		else:
			for j in range(len(p)-3,len(p)):
				y=[]
				y.append(i)
				y.append(p[j])
				y.append(t[j])
				l.append(y)
	#print(l)
	for i in range(0,len(l)):
		for j in range(0,len(l)-1):
			if(l[j][2]<l[j+1][2]):
				temp=l[j]
				l[j]=l[j+1]
				l[j+1]=temp
	#print(l)
	likes=[]
	likes_by_user=[]
	for i in range(0,len(l)):
    		currl=mongo.db.liked_pic.find_one({'pic':l[i][1]})
    		print(currl)
    		if currl is not None:
    			likes.append(len(currl['liked_users']))
    			if user in currl['liked_users']:
    				print("hjj")
    				likes_by_user.append(1)
    			else:
    				likes_by_user.append(0)
    		else:
    			likes.append(0)
    			likes_by_user.append(0)
	return render_template('newsfeed.html',user=user,l=l,likes=likes,likes_by_user=likes_by_user)
	#return render_template('newsfeed.html',user=user,l=l)

@app.route('/gotohome',methods=['POST','GET'])
def homepage():
	rqt=mongo.db.requests.find_one({'User_Name':user})
	if(rqt is None):
		no_of_frnd_rqt=0
	else:
    		no_of_frnd_rqt=len(rqt['rqt_usr'])
    	#print('no_of_frnd_rqt=',no_of_frnd_rqt)
	curr_user = mongo.db.pictures.find_one({'usr_name':user})
	if curr_user is None:
		return render_template('home.html',user=user,online_users=[[]],count=no_of_frnd_rqt,flag=0,likes=[],likes_by_user=[])
	user_pics=curr_user['pics']
	time_pic=curr_user['time']
	online_user=[]
	for i in range(len(user_pics)):
		online_user.append([user_pics[i],time_pic[i]])
    	#print('curr_pics:',user_pics)
	likes=[]
	likes_by_user=[]
	for i in user_pics:
		currl=mongo.db.liked_pic.find_one({'pic':i})
		if currl is not None:
			likes.append(len(currl['liked_users']))
			if user in currl['liked_users']:
				likes_by_user.append(1)
			else:
				likes_by_user.append(0)
		else:
			likes.append(0)
			likes_by_user.append(0)
	return render_template('home.html',user=user,online_users=online_user,count=no_of_frnd_rqt,flag=0,likes=likes,likes_by_user=likes_by_user)
	
				
@app.route('/frndreq',methods=['POST','GET'])
def my_frnd_requests():
	rqt=mongo.db.requests.find_one({'User_Name':user})
	all_frnd_rqt=rqt['rqt_usr']
	return render_template('frnd_request.html',user=user,all_requests=all_frnd_rqt)
	
@app.route('/accept_frnd_req',methods=['POST','GET'])
def accept_frnd_req():
	req_user=request.form['accept']
	
	if(req_user[0:2]=='-1'):
		req_user1=req_user[2:]
		rqt=mongo.db.requests.find_one({'User_Name':user})
		frnd_rqt=rqt['rqt_usr']
		frnd_rqt.remove(req_user1)
		mongo.db.requests.update({'User_Name':user},{"$set":{'User_Name':user,'rqt_usr':frnd_rqt}})
		curr=mongo.db.sent_request.find_one({'User_Name':req_user1})
		if curr is not None:
			l=curr['request']
			l.remove(user)
			mongo.db.sent_request.update({'User_Name':req_user1},{"$set":{'User_Name':req_user1,'request':l}})
		return render_template('frnd_request.html',user=user,all_requests=frnd_rqt)
		
	curr=mongo.db.sent_request.find_one({'User_Name':req_user})
	l=curr['request']
	l.remove(user)
	mongo.db.sent_request.update({'User_Name':req_user},{"$set":{'User_Name':req_user,'request':l}})
	rqt=mongo.db.requests.find_one({'User_Name':user})
	frnd_rqt=rqt['rqt_usr']
	frnd_rqt.remove(req_user)
	mongo.db.requests.update({'User_Name':user},{"$set":{'User_Name':user,'rqt_usr':frnd_rqt}})
    	
	rqt=mongo.db.requests.find_one({'User_Name':user})
	all_frnd_rqt=rqt['rqt_usr']
  	
	curr_user = mongo.db.friends.find_one({'User_Name':user})
	if curr_user is None:
		mongo.db.friends.insert({"User_Name":user,'frnd_usr':[req_user]})
	else:
		old_frnd=curr_user['frnd_usr']
		old_frnd.append(req_user)
		mongo.db.friends.update({'User_Name':user},{"$set":{'User_Name':user,'frnd_usr':old_frnd}})
		
	curr1_user = mongo.db.friends.find_one({'User_Name':req_user})	
	if curr1_user is None:
		mongo.db.friends.insert({"User_Name":req_user,'frnd_usr':[user]})
	else:
		old_frnd1=curr1_user['frnd_usr']
		old_frnd1.append(user)
		mongo.db.friends.update({'User_Name':req_user},{"$set":{'User_Name':req_user,'frnd_usr':old_frnd1}})
	
	return render_template('frnd_request.html',user=user,all_requests=all_frnd_rqt)

@app.route('/uploadpage',methods=['POST','GET'])
def goto_uploadpage():
	return render_template('upload.html',flag=0)
	
	
@app.route('/myhome',methods=['POST','GET'])
def myhome():
	rqt=mongo.db.requests.find_one({'User_Name':user})
	no_of_frnd_rqt=len(rqt['rqt_usr'])
    	#print('no_of_frnd_rqt=',no_of_frnd_rqt)
	curr_user = mongo.db.pictures.find_one({'usr_name':user})
	if curr_user is None:
		return render_template('home.html',user=user,online_users=[[]],count=no_of_frnd_rqt,flag=0,likes=[],likes_by_user=[])
	user_pics=curr_user['pics']
	time_pic=curr_user['time']
	online_user=[]
	for i in range(len(user_pics)):
		online_user.append([user_pics[i],time_pic[i]])
    	#print('curr_pics:',user_pics)
	likes=[]
	likes_by_user=[]
	for i in user_pics:
		currl=mongo.db.liked_pic.find_one({'pic':i})
		print("images:",i)
		if currl is not None:
			likes.append(len(currl['liked_users']))
			if user in currl['liked_users']:
				likes_by_user.append(1)
			else:
				likes_by_user.append(0)
		else:
			likes.append(0)
			likes_by_user.append(0)
	print("jil:",likes,likes_by_user)
	return render_template('home.html',user=user,online_users=online_user,count=no_of_frnd_rqt,flag=0,likes=likes,likes_by_user=likes_by_user)
	
@app.route('/upload_now',methods=['POST','GET'])
def upload_now():
	f=request.files['file']
	fname=secure_filename(f.filename)
	#print("ext:",fname[-4:])
	now=datetime.datetime.now()
	t=now.strftime('%Y-%m-%d %H:%M:%S')
	if (fname[-4:] in ALLOWED_EXT) or (fname[-5:] in ALLOWED_EXT):
		ext=fname[-4:]
		f.save(app.config['UPLOAD_FOLDER']+'/'+fname)
		up=mongo.db.pictures.find_one({'usr_name':user})
		if up is None:	
			#print("hi1")
			mongo.db.pictures.insert({'usr_name':user,'pics':['static/pictures/'+fname],'time':[t]})
			
		else:
			#print("hi2")	
			pic=up['pics']
			pic.append('static/pictures/'+fname)
			#print('pics:',pic)
			ti=up['time']
			ti.append(t)
			mongo.db.pictures.update({'usr_name':user},{"$set":{'usr_name':user,'pics':pic,'time':ti}})
			
		return redirect(url_for('myhome'))
	return render_template('upload.html',flag=1)
	

@app.route('/find_friends',methods=['POST',"GET"])
def find_friends():
	Friends=mongo.db.friends
	usr_frnds=Friends.find_one({'User_Name':user})
	frnd_list=set(usr_frnds['frnd_usr'])
	User=mongo.db.User
	other_user=User.find()
	new_list=[]
	for x in other_user:
		new_list.append(x['User_Name'])
	new_list=set(new_list)
	new_list=new_list.difference({user})
	Requests=mongo.db.requests
	usr_rqt=set(Requests.find_one({'User_Name':user})['rqt_usr'])
	print("ki",user)
	sent_rqt=set(mongo.db.sent_request.find_one({'User_Name':user})['request'])
	new_friend=new_list.difference(frnd_list.union(usr_rqt.union(sent_rqt)))
	print(new_friend)
	return render_template('request(1).html',request_list=new_friend)
	
	
@app.route('/add_friend',methods=['POST','GET'])
def send_request():
	sent_rqt=request.form['Send']
	print(sent_rqt)
	Requests=mongo.db.requests
	curr_usr=Requests.find_one({'User_Name':sent_rqt})['rqt_usr']
	curr_usr.append(user)
	rqt=mongo.db.sent_request.find_one({'User_Name':user})['request']
	rqt.append(sent_rqt)
	mongo.db.sent_request.update({'User_Name':user},{'User_Name':user,'request':rqt})
	Requests.update({'User_Name':sent_rqt},{'User_Name':sent_rqt,'rqt_usr':curr_usr})
	return redirect(url_for('find_friends'))


@app.route('/my_friends',methods=['POST','GET'])
def my_friends():
	frnd=mongo.db.friends.find_one({'User_Name':user})['frnd_usr']
	return render_template('myfrnd.html',user=user,frnd=frnd)
	
	
@app.route('/viewprofile',methods=['POST','GET'])
def viewprofile():
	other_user=request.form['other_user']
	global ot
	ot=other_user
	rqt=mongo.db.requests.find_one({'User_Name':other_user})
	no_of_frnd_rqt=len(rqt['rqt_usr'])
    	#print('no_of_frnd_rqt=',no_of_frnd_rqt)
	curr_user = mongo.db.pictures.find_one({'usr_name':other_user})
	if curr_user is None:
		return render_template('home.html',user=other_user,online_users=[[]],count=no_of_frnd_rqt,flag=1,likes=[],likes_by_user=[])
	user_pics=curr_user['pics']
	time_pic=curr_user['time']
	online_user=[]
	for i in range(len(user_pics)):
		online_user.append([user_pics[i],time_pic[i]])
    	#print('curr_pics:',user_pics)
	likes=[]
	likes_by_user=[]
	for i in user_pics:
    		currl=mongo.db.liked_pic.find_one({'pic':i})
    		if currl is not None:
    			likes.append(len(currl['liked_users']))
    			if user in currl['liked_users']:
    				likes_by_user.append(1)
    			else:
    				likes_by_user.append(0)
    		else:
    			likes.append(0)
    			likes_by_user.append(0)
	return render_template('home.html',user=other_user,online_users=online_user,count=no_of_frnd_rqt,flag=1,likes=likes,likes_by_user=likes_by_user)
	
    	
    	
    	
@app.route('/like',methods=['POST','GET'])
def likes():
	liked_user_pic=request.form['like']
	x=liked_user_pic.split('_')
	vp=x[1]
	liked_pic=x[0]
	print("usrr:",user,"pib:",liked_pic)
	curr=mongo.db.liked_pic.find_one({'pic':liked_pic})
	if curr is None:
		mongo.db.liked_pic.insert({'pic':liked_pic,'liked_users':[user]})
	else:
		l=curr['liked_users']
		l.append(user)
		mongo.db.liked_pic.update({'pic':liked_pic},{'pic':liked_pic,'liked_users':l})
	if(vp=='0'):
		return redirect(url_for('myhome'))
	else:
		return redirect(url_for('viewprofile1'))
	
		
		
@app.route('/viewprofile1',methods=['POST','GET'])
def viewprofile1():
	other_user=ot
	print("other_us:",other_user)
	rqt=mongo.db.requests.find_one({'User_Name':other_user})
	no_of_frnd_rqt=len(rqt['rqt_usr'])
    	#print('no_of_frnd_rqt=',no_of_frnd_rqt)
	curr_user = mongo.db.pictures.find_one({'usr_name':other_user})
	if curr_user is None:
		return render_template('home.html',user=other_user,online_users=[[]],count=no_of_frnd_rqt,flag=1,likes=[],likes_by_user=[])
	user_pics=curr_user['pics']
	time_pic=curr_user['time']
	online_user=[]
	for i in range(len(user_pics)):
		online_user.append([user_pics[i],time_pic[i]])
    	#print('curr_pics:',user_pics)
	likes=[]
	likes_by_user=[]
	for i in user_pics:
    		currl=mongo.db.liked_pic.find_one({'pic':i})
    		if currl is not None:
    			likes.append(len(currl['liked_users']))
    			if user in currl['liked_users']:
    				likes_by_user.append(1)
    			else:
    				likes_by_user.append(0)
    		else:
    			likes.append(0)
    			likes_by_user.append(0)
	return render_template('home.html',user=other_user,online_users=online_user,count=no_of_frnd_rqt,flag=1,likes=likes,likes_by_user=likes_by_user)

		
@app.route('/liken',methods=['POST','GET'])
def liken():
	liked_pic=request.form['like']
	print("usrr:",user,"pib:",liked_pic)
	curr=mongo.db.liked_pic.find_one({'pic':liked_pic})
	if curr is None:
		mongo.db.liked_pic.insert({'pic':liked_pic,'liked_users':[user]})
	else:
		l=curr['liked_users']
		l.append(user)
		mongo.db.liked_pic.update({'pic':liked_pic},{'pic':liked_pic,'liked_users':l})
	return redirect(url_for('newsfeed'))
		
		
@app.route('/logout',methods=['POST','GET'])
def logout():
	return redirect('/')
	
	
if __name__=='__main__':
	app.secret_key='mysecret'
	app.run(host='127.0.0.1',port=2000,debug=True)
