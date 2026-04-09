from flask import session
from flask import Flask, render_template, request, redirect
import mysql.connector
from config import DB_CONFIG

app = Flask(__name__)

app.secret_key = "secret123"

db = mysql.connector.connect(**DB_CONFIG)
cursor = db.cursor()

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            session['user'] = username
            return redirect('/dashboard')
        else:
            return "Invalid Credentials"

    return render_template('login.html')

# HOME
@app.route('/')
def home():
    return render_template('index.html')

# ABOUT
@app.route('/about')
def about():
    return render_template('about.html')

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()

    # Total Employees
    cursor.execute("SELECT COUNT(*) FROM employees")
    total = cursor.fetchone()[0]

    # Average Salary
    cursor.execute("SELECT AVG(salary) FROM employees")
    avg_salary = cursor.fetchone()[0]

    # Department Count
    cursor.execute("SELECT COUNT(DISTINCT department) FROM employees")
    dept_count = cursor.fetchone()[0]

    # Department-wise count
    cursor.execute("SELECT department, COUNT(*) FROM employees GROUP BY department")
    dept_data = cursor.fetchall()

    dept_labels = [row[0] for row in dept_data]
    dept_values = [row[1] for row in dept_data]

    return render_template(
        'dashboard.html',
        employees=employees,
        total=total,
        avg_salary=round(avg_salary, 2),
        dept_count=dept_count,
        dept_labels=dept_labels,
        dept_values=dept_values
    )
    
# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')
    
# ADD EMPLOYEE
@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['email'],
            request.form['department'],
            request.form['salary'],
            request.form['joining_date']
        )
        cursor.execute(
            "INSERT INTO employees (name,email,department,salary,joining_date) VALUES (%s,%s,%s,%s,%s)",
            data
        )
        db.commit()
        return redirect('/dashboard')

    return render_template('add_employee.html')

# DELETE
@app.route('/delete/<int:id>')
def delete_employee(id):
    cursor.execute("DELETE FROM employees WHERE emp_id=%s", (id,))
    db.commit()
    return redirect('/dashboard')

# UPDATE
@app.route('/update/<int:id>', methods=['GET','POST'])
def update_employee(id):
    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['email'],
            request.form['department'],
            request.form['salary'],
            id
        )
        cursor.execute(
            "UPDATE employees SET name=%s,email=%s,department=%s,salary=%s WHERE emp_id=%s",
            data
        )
        db.commit()
        return redirect('/dashboard')

    cursor.execute("SELECT * FROM employees WHERE emp_id=%s", (id,))
    emp = cursor.fetchone()
    return render_template('update_employee.html', emp=emp)

# VIEW SINGLE
@app.route('/view/<int:id>')
def view_employee(id):
    cursor.execute("SELECT * FROM employees WHERE emp_id=%s", (id,))
    emp = cursor.fetchone()
    return render_template('view_employee.html', emp=emp)

if __name__ == '__main__':
    app.run(debug=True)