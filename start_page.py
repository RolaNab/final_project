import datetime
import time
from datetime import date
from datetime import time
import requests
import json
from flask import Flask,render_template
import jinja2
import mariadb


############ connection mariadb #########
try:
    conn = mariadb.connect(
        user="root",
        password="123456",
        host="localhost",
        port=3306,
        database="final_project"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")

# Get Cursor
cur = conn.cursor()

############ Register New Student ###########
def register_new_student():
    student_name = input("Enter Student Name : ")
    student_birthday = input("Enter Date of birth (yyyy-mm-dd) : ")
    level = input("Select Level (A , B or C) : ")
    mobile_num = input("Enter Mobile Number : ")
    email = input("Enter Email : ")
    address = input("Enter Address : ")
    data =  {
        "Student Name" : student_name,
        "Student Birthdate" : student_birthday,
        "Level" : level,
        "Mobile Number" : mobile_num,
        "Email" : email,
        "Address" : address
    }
    print(data)

    insert_to_contact = f"insert into contacts (mobile_number, email) values ('{mobile_num}' , '{email}');"
    select_contact = "Select LAST_INSERT_ID()"
    select_level = f"Select levels.level_id  from levels where level_name='Level {level}'"
    insert_address = f"insert into addresses (address) values ('{address}');"
    select_add = "Select LAST_INSERT_ID()"

    cur.execute(insert_to_contact)
    cur.execute(select_contact)
    for cont_id in cur:
        print(cont_id[0])
    cur.execute(insert_address)
    cur.execute(select_add)
    for add_id in cur:
        print(add_id[0])
    cur.execute(select_level)
    for levl_id in cur:
        print(levl_id[0])
    insert_student = f"""insert into students (student_name, contact_id,address_id,level_id,BOD)
                             values ('{student_name}','{cont_id[0]}','{add_id[0]}','{levl_id[0]}'
                             ,'{student_birthday}');"""
    cur.execute(insert_student)
    conn.commit()
    print("Successfully added entry to database")

############ Enroll Courses ###########


def enroll_course():
    student_id = input("Enter Student ID : ")
    course_id = input("Enter Course ID : ")
    total_hours = input("Enter Total Hours : ")
    date = datetime.datetime.today()

    student_level = f"select level_id from students where student_id={student_id}"
    course_level = f"select level_id from courses where course_id={course_id}"
    print(course_level)
    cur.execute(student_level)

    data_fetched = cur.fetchall()  # (1,)
    if not data_fetched:
        print('No Data')
        return
    std_level = data_fetched[0]

    print('std_level :', std_level)
    if not std_level:
        print(f'No student level found {std_level}')
        return

    cur.execute(course_level)

    data_fetched = cur.fetchall()  # (1,)
    if not data_fetched:
        print('No Courses Level Exist')
        return
    crs_level = data_fetched[0]

    print('crs_level :', crs_level)
    if not crs_level:
        print(f'No Course level found {crs_level}')
        return

    if std_level == crs_level:
        print("Levels are Matched ")
    else:
        print('Sorry, Levels are NOT Matched.')
        return

    capacity_length = f"select max_capacity from courses where course_id={course_id}"
    cur.execute(capacity_length)

    data_fetched = cur.fetchall()  # (1,)
    if not data_fetched:
        print('No capacity_length Exist')
        return
    max_capacity = data_fetched[0]

    print('max_capacity :', max_capacity)
    if not max_capacity:
        print(f'No max_capacity found')
        return

    current_capacity = f"select count(*) from enrollment_histories where course_id = {course_id}"
    cur.execute(current_capacity)
    data_fetched = cur.fetchall()  # (1,)
    if not data_fetched:
        print('No Exist')
        return
    current_capacity = data_fetched[0]

    print('current_capacity :', current_capacity)
    if not current_capacity:
        print(f'No current_capacity found')
        return

    if max_capacity <= current_capacity:
        print("Sorry, Max Capacity Reached")
        return

    select_std_id = f"SELECT * from enrollment_histories where student_id={student_id} and course_id={course_id}"
    cur.execute(select_std_id)
    data_fetched = cur.fetchall()  # (1,)
    if data_fetched:
        print('Sorry, This Student enrolled this Course before')
        return

    try:
        insert_enroll_course = f"""insert into enrollment_histories (student_id, course_id, enroll_date, total_hours
                                        , total)values('{student_id}','{course_id}','{date}','{total_hours}','0')"""
        cur.execute(insert_enroll_course)
        total = f"""UPDATE enrollment_histories
                       join courses c on c.course_id = enrollment_histories.course_id
                       SET total = total_hours * c.rate_per_hour;"""
        cur.execute(total)
        conn.commit()
        print("Successfully added entry to database")
    except:
        print("not added entry to database")


# ########### Crete New Course ###########


def create_new_course():
    course_id = input("Enter Course ID  : ")
    course_name = input("Enter Course Name : ")
    max_capacity = input("Enter Max capacity : ")
    hour_rate = input("Enter Hour Rate (price) : ")
    level = input("Select Level (A , B or C) : ")

    data = {
        "Course ID": course_id,
        "Course Name": course_name,
        "Max Capacity": max_capacity,
        "Hour Rate": hour_rate,
        "Level" : level
    }
    print(data)
    select_level = f"Select levels.level_id  from levels where level_name='Level {level}'"
    cur.execute(select_level)
    for levl_id in cur:
        print(levl_id[0])

    select_course_id = f"SELECT * from courses where course_id={course_id}"
    cur.execute(select_course_id)
    data_fetched = cur.fetchall()  # (1,)
    if data_fetched:
        print('Sorry, Course ID already Exist !')
        return

    insert_to_course =f"""insert into courses (course_id, level_id, course_name, max_capacity, rate_per_hour)
                        values('{course_id}','{levl_id[0]}','{course_name}','{max_capacity}','{hour_rate}')"""
    cur.execute(insert_to_course)
    conn.commit()
    print("Successfully added entry to database")


#  ############### Create Course Schedules ################


def create_course_schedule():

    week_day = input("Enter Day of the Week  : ")
    course_id = input("Enter Course ID : ")  # 10:30:0 --> datetime.time
    start_time = input("Enter Start Time(%H,%M,%S))  : ")  # 2
    times = start_time.format('%H:%M:%S')

    duration = input("Enter The  duration of the course : ")

    course_level = f"select level_id from courses where course_id={course_id}"
    cur.execute(course_level)
    data_fetched = cur.fetchall()  # (1,)
    if not data_fetched:
        print('No Courses Level Exist')
        return
    crs_level = data_fetched[0]
    print('crs_level :', crs_level)
    if not crs_level:
        print(f'No Course level found {crs_level}')
        return
    all_courses_id = f"select course_id from courses where level_id = {crs_level[0]} "
    print(all_courses_id)
    cur.execute(all_courses_id)
    all_curses_id = cur.fetchall()
    old_list = all_curses_id
    new_list = [str(tpl[0]) for tpl in old_list]
    new_list_str = ','.join(new_list)
    print("old list" , all_curses_id)
    print("new list",new_list_str)
    if not all_curses_id:
        print('No Courses  Exist')
        return
    # all_curses_id =
    check_conflict = f"SELECT * from course_schedules where course_id in({new_list_str}) and day='{week_day}' and duration='{duration}' and start_time ='{times}' "
    cur.execute(check_conflict)
    data_fetched = cur.fetchall()
    if data_fetched:
        print('Sorry..! Conflict day and time .. ')
        return

    insert_schedule_course = f"""insert into course_schedules (course_id, day, duration,start_time)values('{course_id}','{week_day}','{duration}','{times}')"""

    cur.execute(insert_schedule_course)
    conn.commit()
    print("Successfully added entry to database")


# ################# display_student_schedule ############


def display_student_schedule():

    student_id = input("Enter Student ID :")

    display_schedule = f"""select student_id , 
                        cs.course_id, cs.day, cs.duration, cs.start_time from enrollment_histories
                        join courses c on c.course_id = enrollment_histories.course_id
                        join course_schedules cs on enrollment_histories.course_id = cs.course_id
                        where student_id = {student_id}"""

    cur.execute(display_schedule)
    data_fetched = cur.fetchone()
    if not data_fetched:
        print('Student ID does Not Exist')
        return
    print("Student ID \t Course ID \t Day \t Duration \t Start Time")
    print("--------------------------------------------------------")
    for sel in cur:
        print(f"\t{sel[0]}\t\t\t{sel[1]}\t\t{sel[2]}\t\t{sel[3]}\t\t{sel[4]}")


    conn.commit()
    print("Successfully added entry to database")

# ########### Start Menu ###########


while(True):
    student = """
        Select :
        1. Register New Student
        2. Enroll Course
        3. Create New Course
        4. Create New Schedule
        5. Display Student Course Schedule
        6.Exit :)
        """
    print(student)

    userInput = int(input("Please Select An Above Option: "))

    if userInput == 1:
        register_new_student()
    elif userInput == 2:
        enroll_course()
    elif userInput == 3:
        create_new_course()
    elif userInput == 4:
        create_course_schedule()
    elif userInput == 5:
        display_student_schedule()
    elif userInput == 6:
        exit("Thank You :)")
    else:
        exit("\nOops! That's Not A Number")