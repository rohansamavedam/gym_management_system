from app.analytics.analytics import getAnalHoursSpentInGymByDay
from flask import jsonify, render_template, url_for, flash, redirect, request, session
from app import app
# from app.analytics.analytics import getAnalHoursSpentInGym
from app.analytics.analytics import getAnalNumberEnrollements
from app.analytics.analytics import getAnalNumberOfClasses
from app.analytics.analytics import getAnalNumberOfMembers
from app.analytics.analytics import getAnalNumberOfVisitors
from app.analytics.analytics import getAnalHoursSpentInGymByDay
from app.analytics.analytics import getAnalHoursSpentInGymByWeek
from app.analytics.analytics import getAnalHoursSpentInGymByMonth
from app.gym_management_api import *
from passlib.hash import sha256_crypt
from functools import wraps
from app.forms import *
import re
from dateutil.relativedelta import relativedelta
import datetime

db_gym = DBConnect()
connection = db_gym.connect()
cursor = db_gym.get_cursor()

# Run this periodically in production
removeExpiredMemberships(connection=connection, cursor=cursor)

def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			print("is logged in value", args, kwargs)
			return f(*args, **kwargs)
		else:
			flash('Try to login')
			return redirect(url_for('login'))
	return wrap

#Check if the login person is an admin

def is_admin(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		print(session['perm'], "perm")
		if session['perm'] == 1:
			print("is admin value", *args, **kwargs)
			return f(*args, **kwargs)
		elif session['perm'] == 2:
			print("is member value", *args, **kwargs)
			return f(*args, **kwargs)
		else:
			flash('You are not authorised to view this page!!')
			return redirect(url_for('login'))
	return wrap

def is_member(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		print(session['perm'], "perm is")
		if session['perm'] == 2:
			return f(*args, **kwargs)
		else:
			flash('You are not authorised to view this page!!')
			return redirect(url_for('login'))
	return wrap

@app.route('/login', methods = ['GET', 'POST'])
def login():
	message = ''
	gym_info = getGymInformation(cursor)
	form = LoginForm()
	if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
		print('post')
		email = request.form['email']
		password_candidate = request.form['password']
		result = checkUser(cursor, email)
		print(result)
	
		if result:
			data = result
			print("data", data)
			password = data[0][3]
			print(password, password_candidate, sha256_crypt.hash(password_candidate))

            #Password will be stored as hash value to maintain confidentiality.
			if sha256_crypt.verify(password_candidate, password): # sha256_crypt is used to compare input password with db stored password.
				session['logged_in'] = True
				session['email'] = email
				session['perm'] = data[0][4]
				session['hash'] = sha256_crypt.hash(email)
				if session['perm'] == 1:  # In admin table, pigermission is set to 1.
					return redirect(url_for('adminDash'))
				elif session['perm'] == 2:
					account = memberInfo(cursor, email)
					print(account)
					enddate = account[0][4]
					currdate = datetime.date.today()
					#print(enddate)
					if enddate < currdate:
						flash('Your Membership Expired!', 'danger')
						changeStatus(connection, cursor, email, status = 'IN-ACTIVE')
						changePermission(connection, cursor, email, perm = 404)
						return render_template('layout.html', form=form, Result_Value=gym_info)
					else:
						return redirect(url_for('memberDash'))
				elif session['perm'] == 404:
					flash('Your account expired, Renew your Memebership!', 'danger')
					return render_template('layout.html', form=form, Result_Value=gym_info)
			else:
				flash('Login Unsuccessful. Please check email and password', 'danger')

				return render_template('layout.html', form=form, Result_Value=gym_info)

			cursor.close();
		else:
			flash('Login Unsuccessful. Please check email, password and usertype', 'danger')
			return render_template('layout.html', form=form, Result_Value=gym_info)

	return render_template('layout.html', form=form, Result_Value=gym_info)

#route to admin Dashboard
@app.route('/adminDash')
@is_logged_in
@is_admin
def adminDash():
	location = getGymLocations(cursor)
	print("location is", location)
	dropdown = request.args.get('location')
	print(dropdown, "dropdown")
	return render_template('adminDash.html', location = location, dropdown=dropdown)

#route to member Dashboard
@app.route('/memberDash')
@is_logged_in
@is_member
def memberDash():
	location = getGymLocations(cursor)
	print("location is", location)
	dropdown = request.args.get('location')
	print(dropdown, "dropdown")
	return render_template('memberDash.html', location = location, dropdown=dropdown)

#route to add member
@app.route('/addMember', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def addMember():

	form = MemberForm() # Send emails list for validating member email

	if request.method == 'POST':
		#result = choosePlan(cursor)
		#print(result)
		name = form.name.data
		username = form.username.data
		email = form.email.data
		password = form.password.data
		confirmPassword = form.confirm.data
		address = form.address.data
		city = form.city.data
		phone = form.phone.data
		plan = form.plan.data
		startdate = form.startdate.data
		perm = 2 # permission set to 2 for member

		account = memberInfo(cursor, email)
		print(account)

		if account:
			flash('Email already exists', 'danger')
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			flash('Enter a valid Email Id', 'danger')
		else:
			if password != confirmPassword:
				flash('Passwords Mismatch!', 'danger')
			else:
				password = sha256_crypt.encrypt(str(form.password.data))
				plan_to_months = {'Month-to-Month' : 1, '6-Month' : 6, 'Yearly' : 12}  # Map plans to numbers to calculate enddate
				enddate = startdate + relativedelta(months = plan_to_months.get(plan))
				addtoProfiles(connection, cursor, name, username, email, password, 2, address, city, phone) #add member info to info table
				addtoMember(connection, cursor, email, username, plan, startdate, enddate) # Add username and plan to members table
				flash('New Memeber is added successfully!', 'success')
			return render_template('addMember.html', form = form)
	return render_template('addMember.html', form = form)

@app.route('/deactivateMember', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def deactivate():
	form = DeactivateForm()

	if request.method == 'POST':
		email = form.email.data

		#Deactivate only if account exists
		account = memberInfo(cursor, email)
		status = account[0][5]

		if account and status == "ACTIVE":
			changePermission(connection, cursor, email, perm = 404)
			changeStatus(connection, cursor, email, status = 'IN-ACTIVE')
			flash('Deactivated Member successfully!', 'success')
		elif account and status == 'IN-ACTIVE':
			flash('This account is already deactivated!', 'danger')
		else:
			flash('This account does not exist', 'danger')
		return render_template('deactivateMember.html', form = form)
	return render_template('deactivateMember.html', form = form)

@app.route('/renewMember', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def renewMembership():
	form = RenewMembership()

	if request.method == 'POST':
		email = form.email.data
		plan = form.plan.data
		startdate = form.startdate.data

		plan_to_months = {'Month-to-Month' : 1, '6-Month' : 6, 'Yearly' : 12}  # Map plans to numbers to calculate enddate
		enddate = startdate + relativedelta(months = plan_to_months.get(plan))

		#Renew only if account exists
		account = memberInfo(cursor, email)
		print(account)

		if not account:
			flash('This account does not exist', 'danger')
			return render_template('renewMember.html', form = form)

		status = account[0][5]

		print(status)

		if account and status == "IN-ACTIVE":
			changePermission(connection, cursor, email, perm = 2)
			changeStatus(connection, cursor, email, status = 'ACTIVE')
			updateMember(connection, cursor, email, plan, startdate, enddate)
			flash('Renewed Membership successfully!', 'success')
		elif account and status == 'ACTIVE':
			flash('Membership is still active!', 'danger')
		else:
			flash('This account does not exist', 'danger')
		return render_template('renewMember.html', form = form)
	return render_template('renewMember.html', form = form)

@app.route('/checkInMember', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def checkInMember():
	if request.method == 'POST':
		email = request.form['email']
		if(email == ""):
			flash('Please enter an email before submitting', 'danger')
		else:
			account = checkUser(cursor, email)
			if account:
				if account[0][4] == 1:
					flash('Member is an admin, cannot checkin', 'danger')
				else:
					member_email = account[0][2]
					checked = checkIfMemberIsCheckedIn(connection, cursor, email)
					if checked:					
						checkOutMember(connection, cursor, email)
					else:
						checkMemberIn(connection, cursor, email)
			else:
				flash('Member does not exist, check email', 'danger')

	all_checked_members = getAllCheckedInMembers(connection, cursor)
	print(all_checked_members)
	return render_template('checkInMember.html',all_checked_members = all_checked_members)

#route to admin Dashboard
@app.route('/freeTrial', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def signUp():

	form = FreetrialForm() # Send emails list for validating member email

	if request.method == 'POST':
		name = form.name.data
		username = form.username.data
		email = form.email.data
		password = form.password.data
		confirmPassword = form.confirm.data
		address = form.address.data
		city = form.city.data
		phone = form.phone.data
		startdate = form.startdate.data
		perm = 2 # permission set to 2 for member

		account = memberInfo(cursor, email)
		#print(account)

		if account:
			flash('You can enroll in Free-Trail only Once', 'danger')
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			flash('Enter a valid Email Id', 'danger')
		else:
			if password != confirmPassword:
				flash('Passwords Mismatch!', 'danger')
			else:
				password = sha256_crypt.encrypt(str(form.password.data))
				enddate = startdate + datetime.timedelta(days = 7) # 7-day free trail
				addtoProfiles(connection, cursor, name, username, email, password, 2, address, city, phone) #add member info to info table
				addtoMember(connection, cursor, email, username, '7-day Free-trial', startdate, enddate) # Add username and plan to members table
				flash('New Memeber is added successfully!', 'success')
			return render_template('freeTrial.html', form = form)
	return render_template('freeTrial.html', form = form)

@app.route('/viewMember', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def viewMember():
	#return redirect(url_for('adminDash'))
	result = getMembers(cursor)
	print("result  is", result)
	return render_template('view_members.html', result=result)
		

@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	gym_info = getGymInformation(cursor)
	form = LoginForm()
	#flash('You are now logged out', 'success')
	return render_template('layout.html', form=form, Result_Value=gym_info)

@app.route("/gym_info", methods=['GET'])
def get_gym_info():
	gym_info = getGymInformation(cursor)
	return jsonify(gym_info)


@app.route("/",methods=['GET', 'POST'])
def home():
    gym_info = getGymInformation(cursor)
    form = LoginForm()
    #if form.is_submitted():
	    #return redirect(url_for('login'))
    return render_template('layout.html', form=form, Result_Value=gym_info)

@app.route("/gym_schedule/<location>", methods=['GET'])
def get_gym_schedule(location):
	gymSchedule = getGymScheduleInfo(cursor, location)
	return jsonify(gymSchedule)

@app.route("/gym_enrollment_schedule/<location>", methods=['GET', 'POST'])
@is_logged_in
@is_member
def get_gym_enrollment_schedule(location):
	gymSchedule = getGymScheduleInfo(cursor, location, username=session['email'])
	print(gymSchedule)
	return jsonify(gymSchedule)

	
@app.route("/show_gym_schedule_membership/<location>", methods=['GET', 'POST'])
def get_gym_schedule_membership(location):
    result = getGymPrice(cursor, location)
    equipments = getEquipments(cursor)
    #employees = result.query.filter_by(Employee_Name=Employee_Name).all()
    return render_template('show_gym_schedule_membership.html', location = location, result=result, equipments=equipments)


@app.route('/signUpforClass/<location>', methods = ['GET', 'POST'])
@is_logged_in
@is_member
def signUpforClass(location):
	print("getting location", location)
	result = getGymScheduleDetails(cursor, location, username=session['email'])
	print("result  is", result)
	return render_template('sign_up_for classes.html', location=location, result=result, enrolled="None")


@app.route('/viewSignedUpClasses', methods = ['GET', 'POST'])
@is_logged_in
@is_member
def viewSignedUpClasses():
	#return redirect(url_for('adminDash'))
	result = getEnrolledClasses(cursor, username=session['email'])
	print("result  is", result)
	return render_template('view_signed_up_classes.html', result=result)


@app.route('/enrollInClass/<location>/<class_name>', methods = ['GET', 'POST'])
@is_logged_in
@is_member
def enrollInClass(location, class_name):
	print("location, class_name", location, class_name)
	print("Email", session['email'])

	if not isAlreadyEnrolled(cursor=cursor, username=session['email'], class_name=class_name, location=location):
		result = enrollMember(connection=connection, cursor=cursor, username=session['email'], class_name=class_name, location=location)
		print("result  is", result)
		return render_template('sign_up_for classes.html', location=location, result=None, enrolled="False")
		#return redirect(url_for('signUpforClass',location=location))
	else:
		print("Already enrolled")

@app.route('/unenrollClass/<location>/<class_name>', methods = ['GET', 'POST'])
@is_logged_in
@is_member
def unenrollClass(location, class_name):
	if isAlreadyEnrolled(cursor=cursor, username=session['email'], class_name=class_name, location=location):
		result = unenrollMember(
			connection=connection, 
			cursor=cursor, 
			username=session['email'], 
			class_name=class_name, 
			location=location
		)
		print("result  is", result)
		return render_template('sign_up_for classes.html', location=location, result=None, enrolled="True")
	else:
		print("Member not enrolled to class. Nothing to do")
		print("Already enrolled")


# Analytics related APIs



@app.route('/analytics/', methods = ['GET'])
# @is_logged_in
def getClasses():
	print("Get classes called")
	result = dict()
	result["classes"] = getAnalNumberOfClasses(cursor)[:5]
	result["enrollments"] = getAnalNumberEnrollements(cursor)
	result["hours_in_gym_day"]= getAnalHoursSpentInGymByDay(cursor)[:30] #recent 30 records
	result["hours_in_gym_week"]= getAnalHoursSpentInGymByWeek(cursor)[:30]  #recent 30 records
	result["hours_in_gym_month"]= getAnalHoursSpentInGymByMonth(cursor)[:30]  #recent 30 records
	result["no_of_members"]= getAnalNumberOfMembers(cursor)
	result["no_of_visitors"] = getAnalNumberOfVisitors(cursor)[:30]  #recent 30 records
	#print(result)
	return render_template('analytics_dashboard.html', result=result, already_enrolled="True")	# Placeholder, should be removed later


# @app.route('/analytics/enrollments', methods = ['GET'])
# # @is_logged_in
# def getEnrollements():
# 	print("Get enrollments called")
# 	getAnalNumberEnrollements(cursor)
# 	return render_template('login.html', result=None, already_enrolled="True")	# Placeholder, should be removed later


# @app.route('/analytics/hoursSpentInGym', methods = ['GET'])
# # @is_logged_in
# def getHoursSpentInGym():
# 	print("Get hoursSpentInGym called")
# 	getAnalHoursSpentInGym(cursor)
# 	return render_template('login.html', result=None, already_enrolled="True")	# Placeholder, should be removed later


# @app.route('/analytics/numberOfVisitors', methods = ['GET'])
# # @is_logged_in
# def getNumberOfVisitors():
# 	print("Get numberOfVisitors called")
# 	getAnalNumberOfVisitors(cursor)
# 	return render_template('login.html', result=None, already_enrolled="True")	# Placeholder, should be removed later


# @app.route('/analytics/numberOfMembers', methods = ['GET'])
# # @is_logged_in
# def getNumberOfMembers():
# 	print("Get numberOfMembers called")
# 	getAnalNumberOfMembers(cursor)
# 	return render_template('login.html', result=None, already_enrolled="True")	# Placeholder, should be removed later


# @app.route('/analytics/numberOfMembers/<location>', methods = ['GET'])
# # @is_logged_in
# def getNumberOfMembersByLocation(location):
# 	print("Get numberOfMembers for a location called")
# 	getAnalNumberOfMembersByLocation(cursor)
# 	return render_template('login.html', result=None, already_enrolled="True")	# Placeholder, should be removed later


@app.route('/logHours', methods = ['GET', 'POST'])
@is_logged_in
@is_member
def logHours():
	#return redirect(url_for('adminDash'))
	result = getGymEquipments(cursor)
	loc = getGymLocations(cursor)
	log = getLoggedHours(cursor, username=session['email'])
	print("class and equipment is", result)
	return render_template('log_hours.html', result=result, loc=loc, log=log, submit="None")

@app.route('/addMemberLog/<location>/<classname>/<time>/<date>', methods = ['GET', 'POST'])
@is_logged_in
@is_member
def addMemberLog(location, classname, time, date):
	insertMemberLog(connection = connection, cursor=cursor, username=session['email'], class_name=classname, time=time, date=date, location=location)
	result = getGymEquipments(cursor)
	loc = getGymLocations(cursor)
	log = getLoggedHours(cursor, username=session['email'])
	#return render_template('log_hours.html', result=result)
	return render_template('log_hours.html', result=result, loc=loc, log=log, submit="True")

@app.route('/userActivity/<timeperiod>', methods = ['GET', 'POST'])
@is_logged_in
@is_member
def getUserActivity(timeperiod):
	if timeperiod == "pastweek":
		member_logs = pastWeekStats(cursor, username=session['email'], json_format=True)
	elif timeperiod == "pastmonth":
		member_logs = pastMonthStats(cursor, username=session['email'], json_format=True)
	elif timeperiod == "90days":
		member_logs = ninetyDayStats(cursor, username=session['email'], json_format=True)
	else:
		member_logs = getLoggedHours(cursor, username=session['email'], json_format=True)
	
	return jsonify(member_logs)
	

@app.route('/workoutSummary', methods = ['GET', 'POST'])
@is_logged_in
@is_member
def getWorkoutSummary():
	workoutSummary = getMinutes(cursor, username=session['email'],json_format=True)
	return jsonify(workoutSummary)

@app.route('/viewActivity', methods = ['GET', 'POST'])
@is_logged_in
@is_member
def viewActivity():
	result = getGymEquipments(cursor)
	loc = getGymLocations(cursor)
	return render_template('view_my_activity.html', result=result, loc=loc, submit="None")
