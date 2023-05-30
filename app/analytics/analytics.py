
def getAnalNumberOfClasses(cursor):
    query = """SELECT member_name, COUNT(*) as num_classes
        FROM tbl_class_enrolled
        GROUP BY member_name;"""
    return executeQueryAndReturnResult(cursor, query)


def getAnalNumberEnrollements(cursor):
    query = """
        SELECT class_name, count(*) as enrollments
        FROM tbl_class_enrolled
        group by class_name;
    """
    return executeQueryAndReturnResult(cursor, query)

# def getAnalHoursSpentInGym(cursor):
#     query = """
#         SELECT user_name, SUM(num_of_minutes) as total_minutes
#         FROM tbl_member_log
#         GROUP BY user_name;
#     """
#     return executeQueryAndReturnResult(cursor, query)

def getAnalHoursSpentInGymByDay(cursor):
    query = """
        SELECT DATE(date_column) AS day, SUM(num_of_minutes)
        FROM tbl_member_log
        GROUP BY day;
    """
    # query = """
    #     SELECT user_name, SUM(num_of_minutes) as total_minutes
    #     FROM tbl_member_log
    #     GROUP BY user_name;
    # """
    return executeQueryAndReturnResult(cursor, query)

def getAnalHoursSpentInGymByWeek(cursor):
    query = """
        SELECT CONCAT(YEAR(date_column), '-', WEEK(date_column)) AS week, Location, SUM(num_of_minutes)
        FROM tbl_member_log
        GROUP BY week, Location;
    """
    return executeQueryAndReturnResult(cursor, query)

def getAnalHoursSpentInGymByMonth(cursor):

    query = """
        SELECT CONCAT(YEAR(date_column), '-', MONTH(date_column)) AS month, Location, SUM(num_of_minutes)
        FROM tbl_member_log
        GROUP BY month, Location;
    """
    return executeQueryAndReturnResult(cursor, query)


def getAnalNumberOfVisitors(cursor):
    query = """SELECT 
    DATE(date_column) AS date, 
    HOUR(date_column) AS hour,
    CASE 
        WHEN DAYOFWEEK(date_column) IN (1,7) THEN 'weekend'
        ELSE 'weekday'
    END AS day_type,
    COUNT(*) AS visitor_count
    FROM tbl_member_log
    GROUP BY date, hour, day_type
    ORDER BY date, hour, day_type;""" 
    return executeQueryAndReturnResult(cursor, query)


def getAnalNumberOfMembers(cursor):
    query = """
        SELECT COUNT(*) as member_count FROM tbl_gym_members1;
    """
    return executeQueryAndReturnResult(cursor, query)


# def getAnalNumberOfMembersByLocation(cursor):
#     query = "Write query here"  # Need to alter members table to fetch this information
#     return executeQueryAndReturnResult(cursor, query)

def executeQueryAndReturnResult(cursor, query):
    cursor.execute(query)
    result = cursor.fetchall()
    print(result)
    return result

