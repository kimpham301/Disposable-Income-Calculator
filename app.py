from flask import Flask, render_template, request, redirect, url_for, session
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

pymysql.install_as_MySQLdb()
from flaskext.mysql import MySQL

import re
import mysql.connector

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'Flask%Crud#Application'

mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = "localhost"
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Poochie@123'
app.config['MYSQL_DATABASE_DB'] = 'income_calculator'

# Intialize MySQL
mysql.init_app(app)

# Login: K12
# Password: kA12

@app.route('/', methods=['GET', 'POST'])
def login():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return redirect(url_for('calculator'))

    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if user exists using MySQL
        mydb = mysql.connect()
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        user = cursor.fetchone()
        print(user)
        # If user exists in users table in out database
        if user:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            # session['id'] = user[0]
            session['username'] = user[0]
            # Redirect to home page
            return redirect(url_for('calculator'))
        else:
            # user doesnt exist or username/password incorrect
            msg = 'Incorrect username/password! :/'

    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        expense = request.form['expense']
        salary = request.form['salary']
        username = request.form['username']
        password = request.form['password']
        pass_word = generate_password_hash(password)

        # Check if user exists using MySQL
        mydb = mysql.connect()
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        # If user exists show error and validation checks
        if user:
            msg = 'Username/user already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password:
            msg = 'Please fill out the form!'
        else:
            # user doesnt exists and the form data is valid, now insert new user into users table
            cursor.execute('INSERT INTO users (username, password, salary, expense) VALUES (%s, %s, %s, %s)',
                           (username, pass_word, salary, expense,))
            mydb.commit()
            msg = 'You have successfully registered!'
            return render_template('index.html')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    # Check if user is loggedin
    if 'loggedin' in session:

        data = mysql.connect()
        cursor = data.cursor()
        #Update the user's data
        if request.method == 'POST':
            expense = request.form['expense']
            salary = request.form['salary']
            cursor.execute('UPDATE users SET expense = %s WHERE username = %s',
                           (expense, (session['username'],)))
            cursor.execute('UPDATE users SET salary = %s WHERE username = %s',
                           (salary, (session['username'],)))
            data.commit()
        # Show the user's data
        cursor.execute('SELECT salary FROM users WHERE username = %s', (session['username'],))
        inputsal = cursor.fetchone()[0]
        cursor.execute('SELECT expense FROM users WHERE username = %s', (session['username'],))
        inputex = cursor.fetchone()[0]
        cursor.execute('SELECT un_exp FROM un_ex WHERE username = %s', (session['username'],))
        inputunexp = cursor.fetchall()[0]
        totalunexp = sum(inputunexp)
        totaleft = (inputsal/12) - inputex - totalunexp
        return render_template('calculator.html', salaryin=inputsal, expensein=inputex, total=totaleft)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/unexpected', methods=['GET', 'POST'])
def unexpected():
    if 'loggedin' in session:
        # We need all the user info for the user so we can display it on the profile page
        month_data = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]

        data = mysql.connect()
        cursor = data.cursor()

        if request.method == 'POST':
            unexpect = request.form['unex']
            day = request.form['inputDay']
            month = request.form.get('inputMonth')
            year = request.form['inputYear']
            cursor.execute('INSERT INTO un_ex (username, un_exp, day, year, month) VALUES (%s, %s, %s, %s,%s)',
                           (session['username'], unexpect, day, year, month,))
            data.commit()
        # Show the profile page with user info
        cursor.execute('SELECT un_exp FROM un_ex WHERE username = %s', (session['username'],))
        input_ue = [item[0] for item in cursor.fetchall()]
        cursor.execute('SELECT day FROM un_ex WHERE username = %s', (session['username'],))
        input_day = [item[0] for item in cursor.fetchall()]
        cursor.execute('SELECT month FROM un_ex WHERE username = %s', (session['username'],))
        input_month = [item[0] for item in cursor.fetchall()]
        cursor.execute('SELECT year FROM un_ex WHERE username = %s', (session['username'],))
        input_year = [item[0] for item in cursor.fetchall()]
        return render_template('unexpected.html', unexin=input_ue, inday=input_day, inmonth= input_month,inyear=input_year, month_data=month_data)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()
