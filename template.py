import requests
import json
from flask import Flask, request, url_for, redirect, render_template
import requests
from flask import jsonify
import jinja2
import mariadb
from collections import defaultdict
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

cur = conn.cursor()
# Get Cursor
def get_student_details():
    query="""select student_id, student_name, c.mobile_number , c.email , a.address from students s
            join contacts c on c.contact_id = s.contact_id
            join addresses a on a.address_id = s.address_id"""

    cur.execute(query)
    data = cur.fetchall()
    res = defaultdict(list)
    for i in range(len(data)):
        for a in data[i]:
            res[i].append(a)

    students_dic = dict(res)



    return students_dic

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/courses')
def courses():
    cur.execute("select * from courses")
    data = cur.fetchall()
    for i in cur:
        print("dataaa",i)
    context = {'data': data}
    return render_template('courses.html', **context)


@app.route('/students')
def students():
    cur.execute("""select student_id,student_name, c.mobile_number, c.email ,a.address from students
                    join contacts c on c.contact_id = students.contact_id
                    join addresses a on a.address_id = students.address_id""")
    data = cur.fetchall()
    print(data)
    context = {'data': data}
    return render_template('students.html', **context)

@app.route('/all_schedules')
def all_schedules():
    cur.execute("SELECT * from course_schedules")
    data = cur.fetchall()
    print(data)
    context = {'data': data}
    return render_template('all_schedules.html', **context)

@app.route('/api/all_students')
def students_details():
    students = get_student_details()
    return json.dumps(students,sort_keys=True,indent=3)

@app.route('/api/all_students/')
def emp_details(std_id):
    try:
        cur.execute("""select student_id,student_name, c.mobile_number, c.email ,a.address from students
                                    join contacts c on c.contact_id = students.contact_id
                                    join addresses a on a.address_id = students.address_id WHERE id =%s""", std_id)
        empRow = cur.fetchone()
        respone = jsonify(empRow)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
app.run(debug=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1',port='5000')