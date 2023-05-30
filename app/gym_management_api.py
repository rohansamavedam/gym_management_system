import json
import mysql.connector
from mysql.connector import Error
import datetime
from datetime import date

class DBConnect:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(host='127.0.0.1',
                                                      database='db_gym_management',
                                                      user='root',
                                                      port=3307,
                                                      password='password')

            if self.connection.is_connected():
                db_Info = self.connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                self.cursor = self.connection.cursor()
                self.cursor.execute("select database();")
                record = self.cursor.fetchone()
                print("You're connected to database: ", record)
                return self.connection

        except Error as e:
            print("Error while connecting to MySQL", e)

    def close(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("MySQL connection is closed")

    def get_cursor(self):
        return self.cursor

    def get_connection(self):
        return self.connection

def getJsonFromDbResult(cursor, result):
    data = []
    for row in result:
        record = {}
        for i, col in enumerate(cursor.description):
            record[col[0]] = row[i]
        data.append(record)
        
    # If there is only one json item, don't put that in a list
    return data[0] if len(data) == 1 else data

# Get information about gyms
def getGymInformation(cursor):
    query = """SELECT id, gym_name, location, address, phone, hours FROM tbl_gym_information"""
    cursor.execute(query)
    result = cursor.fetchall()
    return getJsonFromDbResult(cursor, result)

def checkUser(cursor, email):
    query = """SELECT * FROM tbl_gym_profiles WHERE email = %s"""
    values = [email]
    cursor.execute(query, values)

    result = cursor.fetchall()

    return result

#Return email if account exists
def memberInfo(cursor, email):
    query = """SELECT * FROM tbl_gym_members1 WHERE email = %s"""
    values = [email]

    cursor.execute(query, values)
    result = cursor.fetchall()
    return result

#Get plan details
def choosePlan(cursor):
    query = """SELECT DISTINCT name FROM tbl_gym_plans"""
    cursor.execute(query)

    result = cursor.fetchall()

    return result

# add newly added person info to gym_info table
def addtoProfiles(connection, cursor, name, username, email, password, perm, address, city, phone):
    values = [name, username, email, password, perm, address, city, phone]

    print(values)

    query = """INSERT INTO tbl_gym_profiles (name, username, email, password, perm, address, city, phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

    #query = """SELECT * FROM tbl_gym_profiles"""

    cursor.execute(query, values)
    connection.commit()
    print(cursor.rowcount, "record(s) affected")

#add username and plan to members table
def addtoMember(connection, cursor, email, username, plan, startdate, enddate):
    values = [email, username, plan, startdate, enddate, 'ACTIVE']
    query = """INSERT INTO tbl_gym_members1 (email, username, plan, start_date, end_date, status) VALUES (%s, %s, %s, %s, %s, %s)"""

    cursor.execute(query, values)
    connection.commit()
    print(cursor.rowcount, "record(s) affected")

# Modify status
def changeStatus(connection, cursor, email, status):
    values = [status, email]
    query = """UPDATE tbl_gym_members1 SET status = %s WHERE email = %s"""

    cursor.execute(query, values)
    connection.commit()

# Update members table
def updateMember(connection, cursor, email, plan, startdate, enddate):
    values = [plan, startdate, enddate, email]

    query = """UPDATE tbl_gym_members1 SET plan = %s, start_date = %s, end_date = %s WHERE email = %s"""

    cursor.execute(query, values)
    connection.commit()

def checkIfMemberIsCheckedIn(connection, cursor, email):
    values = [email]
    query = """SELECT * FROM tbl_checked_in WHERE email = %s AND is_checked_in = 1"""
    cursor.execute(query, values)
    result = cursor.fetchall()
    return result

def checkMemberIn(connection, cursor, email):
    check_in_time = str(datetime.datetime.now())
    values = [email, check_in_time]

    query = """INSERT INTO tbl_checked_in (email, check_in_timestamp, check_out_timestamp, is_checked_in) VALUES (%s, %s, NULL, 1)"""

    cursor.execute(query, values)
    connection.commit()

def checkOutMember(connection, cursor, email):
    check_out_time = str(datetime.datetime.now())
    values = [check_out_time, email]
    query = """UPDATE tbl_checked_in SET check_out_timestamp = %s, is_checked_in = 0  WHERE email = %s AND is_checked_in = 1"""
    cursor.execute(query, values)
    connection.commit()

def getAllCheckedInMembers(connection, cursor):
    query = """SELECT * FROM tbl_checked_in WHERE check_out_timestamp IS NULL"""
    cursor.execute(query)
    result = cursor.fetchall()
    return result

#Change permission of a member account when deactivated
def changePermission(connection, cursor, email, perm):
    print(perm)
    values = [perm, email]
    query = """UPDATE tbl_gym_profiles SET perm = %s WHERE email = %s"""

    cursor.execute(query, values)
    connection.commit()

# Get the status of an account
def getStatus(cursor, email):
    value = [email]
    query = """SELECT status FROM tbl_gym_members1 WHERE email = %s"""

    cursor.execute(query, value)
    result = cursor.fetchone()
    return result

def getGymLocations(cursor):
    query = "select distinct location from tbl_class_schedule"
    cursor.execute(query)
    result = cursor.fetchall()
    return result

#get membership and class schedule details of gym based on location 
def getGymScheduleDetails(cursor, location, username):
    membership_query = """SELECT membership_price, duration FROM tbl_gym_membership WHERE location=%s"""
    values = [location]
    cursor.execute(membership_query, values)

    membership_result = cursor.fetchall()

    #class schedule details
    schedule_query = """SELECT class_name, class_timing, class_days, group_size, no_enrolled, instructor FROM tbl_class_schedule WHERE location=%s"""
    values = [location]
    cursor.execute(schedule_query, values)

    schedule_result = cursor.fetchall()
    for i in range(len(schedule_result)):
        schedule_result[i] = list(schedule_result[i])
        class_name = schedule_result[i][0]
        schedule_result[i].append(isUserEnrolledToClass(cursor, location, username, class_name))

    result = []
    result.append(membership_result) 
    result.append(schedule_result) 
    print(result)
    return result

def isUserEnrolledToClass(cursor, location, username, class_name):
    if not username:
        return False
    
    query = """SELECT member_name FROM tbl_class_enrolled where member_name=%s and class_name=%s and location=%s"""
    values = [username, class_name, location]
    cursor.execute(query, values)

    result = cursor.fetchall()
    return True if len(result) else False

#get membership and class schedule info of gym based on location 
def getGymScheduleInfo(cursor, location, username=""):
    membership_query = """SELECT membership_price, duration FROM tbl_gym_membership WHERE location=%s"""
    values = [location]

    cursor.execute(membership_query, values)

    membership_result = cursor.fetchall()
    membership_result = getJsonFromDbResult(cursor, membership_result)

    #class schedule details

    schedule_query = """SELECT class_name, class_timing, class_days, group_size, no_enrolled, instructor FROM tbl_class_schedule WHERE location=%s"""
    values = [location]

    cursor.execute(schedule_query, values)

    schedule_result = cursor.fetchall()
    schedule_result = getJsonFromDbResult(cursor, schedule_result)

    for schedule_info in schedule_result:
        class_name = schedule_info["class_name"]
        schedule_info["is_enrolled"] = isUserEnrolledToClass(cursor, location, username, class_name)

    result = {
        "membership": membership_result,
        "schedule": schedule_result
    }
    return result

def isAlreadyEnrolled(cursor, username, class_name, location) -> bool:
    schedule_query = """SELECT * FROM tbl_class_enrolled WHERE location=%s and class_name=%s and member_name=%s"""
    values = [location, class_name, username]

    cursor.execute(schedule_query, values)
    schedule_result = cursor.fetchall()
    print(schedule_result)
    return True if schedule_result else False


def getEnrolledClasses(cursor, username):
    class_query = """SELECT cr.member_name, cr.class_name, cr.location, cs.class_timing, cs.class_days, cs.instructor FROM tbl_class_enrolled cr INNER JOIN tbl_class_schedule cs ON cs.class_name = cr.class_name and cs.location = cr.location WHERE cr.member_name=%s"""
    values = [username]

    cursor.execute(class_query, values)
    class_result = cursor.fetchall()
    print("view my class:", class_result)
    return class_result

def getMembers(cursor):
    members_query = """SELECT * FROM tbl_gym_members1 where status='Active'"""

    cursor.execute(members_query)
    members_result = cursor.fetchall()
    print(members_result)
    return members_result
    

#add username and plan to members table
def enrollMember(connection, cursor, username, class_name, location):
    query_update = "UPDATE tbl_class_schedule SET no_enrolled = no_enrolled+1 WHERE class_name=%s and location=%s"
    cursor.execute(query_update, [class_name, location])
    connection.commit()

    query = """INSERT INTO tbl_class_enrolled (member_name, class_name, location) VALUES (%s, %s, %s)"""
    cursor.execute(query, [username, class_name, location])
    connection.commit()
    print(cursor.rowcount, "record(s) affected")

#Remove username and plan to members table
def unenrollMember(connection, cursor, username, class_name, location):
    query_update = "UPDATE tbl_class_schedule SET no_enrolled = no_enrolled-1 WHERE class_name=%s and location=%s"
    cursor.execute(query_update, [class_name, location])
    connection.commit()

    query = """DELETE FROM tbl_class_enrolled WHERE member_name=%s and class_name=%s and location=%s"""
    cursor.execute(query, [username, class_name, location])
    connection.commit()
    print(cursor.rowcount, "record(s) affected")


def getExpiredMembers(cursor):
    current_date = date.today()
    query = """SELECT email from tbl_gym_members1 where end_date < %s"""
    values = [current_date]
    cursor.execute(query, values)

    result = cursor.fetchall()
    return result

def removeExpiredMemberships(connection, cursor):
	"""
	Unenroll classes that users with expired memberships had enrolled.
	"""
	members_with_expired_memberships = getExpiredMembers(cursor=cursor)
	for member in members_with_expired_memberships:
		classes_enrolled = getEnrolledClasses(cursor, username=member[0])
		for class_enrolled in classes_enrolled:
			unenrollMember(
				connection=connection, 
				cursor=cursor, 
				username=member[0], 
				class_name=class_enrolled[1], 
				location=class_enrolled[2]
			)


def getEquipments(cursor):
    query = """select equipment_name from tbl_equipments"""
    cursor.execute(query)
    result_equipment = cursor.fetchall()
    return result_equipment


def getGymEquipments(cursor):
    query = """select equipment_name from tbl_equipments"""
    cursor.execute(query)
    result_equipment = cursor.fetchall()
    query = """select distinct class_name from tbl_class_schedule"""
    cursor.execute(query)
    result_class = cursor.fetchall()
    result = result_equipment + result_class
    return result

def insertMemberLog(connection, cursor, username, class_name, time, date, location):
    query = """INSERT INTO tbl_member_log (user_name, equipment_name, num_of_minutes, date_column, Location) VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(query, [username, class_name, time, date, location])
    connection.commit()
    print(cursor.rowcount, "record(s) affected")

def getLoggedHours(cursor, username, json_format=False):
    class_query = """SELECT equipment_name, num_of_minutes, date_column, Location FROM tbl_member_log WHERE user_name=%s order by date_column"""
    values = [username]

    cursor.execute(class_query, values)
    class_result = cursor.fetchall()
    print("view my log:", class_result)
    return getJsonFromDbResult(cursor, class_result) if json_format else class_result

def getMinutes(cursor, username, json_format=False):
    min_query = """SELECT sum(num_of_minutes) FROM tbl_member_log WHERE user_name=%s"""
    values = [username]

    cursor.execute(min_query, values)
    min_result = cursor.fetchall()

    min_week_query = """SELECT SUM(num_of_minutes) FROM tbl_member_log WHERE user_name = %s AND date_column >= DATE_SUB(NOW(), INTERVAL 1 WEEK)"""
    values = [username]

    cursor.execute(min_week_query, values)
    min_week_result = cursor.fetchall()

    min_month_query = """SELECT SUM(num_of_minutes) FROM tbl_member_log WHERE user_name = %s AND date_column >= DATE_SUB(NOW(), INTERVAL 1 MONTH)"""
    values = [username]

    cursor.execute(min_month_query, values)
    min_month_result = cursor.fetchall()

    ninety_query = """SELECT SUM(num_of_minutes) FROM tbl_member_log WHERE user_name = %s AND date_column >= DATE_SUB(NOW(), INTERVAL 90 DAY)"""
    values = [username]

    cursor.execute(ninety_query, values)
    ninety_result = cursor.fetchall()

    if not json_format:
        result = min_result + min_week_result + min_month_result + ninety_result
        print("view my minutes:", result)
        return result

    if not min_result or not min_result[0]:
        min_result = [[0]]
    if not ninety_result or not ninety_result[0]:
        ninety_result = [[0]]
    if not min_week_result or not min_week_result[0]:
        min_week_result = [[0]]
    if not min_month_result or not min_month_result[0]:
        min_month_result = [[0]]

    result = {
        "all": str(min_result[0][0]),
        "90days": str(ninety_result[0][0]),
        "pastweek": str(min_week_result[0][0]),
        "pastmonth": str(min_month_result[0][0]),
    }
    return result

def getGymPrice(cursor, location):
    query = """SELECT membership_price, duration FROM tbl_gym_membership WHERE location=%s"""
    values = [location]

    cursor.execute(query, values)
    result = cursor.fetchall()
    print("view gym details:", result)
    return result


def pastWeekStats(cursor, username, json_format=False):
    week_query = """SELECT equipment_name, num_of_minutes, date_column, Location FROM tbl_member_log WHERE user_name=%s AND date_column >= DATE_SUB(NOW(), INTERVAL 1 WEEK) order by date_column"""
    values = [username]

    cursor.execute(week_query, values)
    week_result = cursor.fetchall()
    return getJsonFromDbResult(cursor, week_result) if json_format else week_result

def pastMonthStats(cursor, username, json_format=False):
    month_query = """SELECT equipment_name, num_of_minutes, date_column, Location FROM tbl_member_log WHERE user_name=%s AND date_column >= DATE_SUB(NOW(), INTERVAL 1 MONTH) order by date_column"""
    values = [username]

    cursor.execute(month_query, values)
    month_result = cursor.fetchall()
    return getJsonFromDbResult(cursor, month_result) if json_format else month_result

def ninetyDayStats(cursor, username, json_format=False):
    ninety_query = """SELECT equipment_name, num_of_minutes, date_column, Location FROM tbl_member_log WHERE user_name = %s AND date_column >= DATE_SUB(NOW(), INTERVAL 90 DAY) ORDER BY date_column"""

    values = [username]

    cursor.execute(ninety_query, values)
    ninety_result = cursor.fetchall()
    return getJsonFromDbResult(cursor, ninety_result) if json_format else ninety_result

def main():
    db = DBConnect()
    connection = db.connect()
    cursor = db.get_cursor()

    # Get general information about the gym - for home page
    print("Gym information: ")
    gym_details = getGymInformation(cursor)
    print(gym_details)

    # Get information about the gym membership and class schedule- for home page
    print("Gym membership and schedule: ")
    gym_details = getGymScheduleDetails(cursor, location='San Francisco')
    print(gym_details)

if __name__ == "__main__":
    main()