from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import re
import md5
import os
import binascii

app = Flask(__name__)
mysql = MySQLConnector(app, 'login-registration')
app.secret_key = 'ThisIsSecret'

emailRegex = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
r = re.compile(r'[a-zA-Z]+')

dev = True

@app.route('/')
def my_portfolio():
    session['id'] = 0
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def register():
    for key in request.form.keys():
        print request.form[key]
        if len(request.form[key]) < 2:
            flash("All fields are required")
            break
        elif not request.form['first_name'].isalpha(): 
            flash("Invalid  first name!")
            break
        elif not request.form['last_name'].isalpha():
            flash("Invalid Last Name!")
            break
        elif not emailRegex.match(request.form['email']):
            flash("Invalid email...")
            break
        elif len(request.form['password']) < 9:
            flash("Password must be at least 8 char!")
            break
        elif request.form['confirm_password'] != request.form['password']: 
            flash("Passwords do not match!")
            break
        else:
            session['email'] = request.form['email']
            salt = binascii.b2a_hex(os.urandom(15))
            password = request.form['password']
            hashed_pw = md5.new(password + salt).hexdigest()
            print hashed_pw
            query = "INSERT INTO user (first_name, last_name, email, password, salt, created_at, updated_at) VALUES (:first_name, :last_name, :email, :hashed_pw, :salt, NOW(), NOW())"
            data = {
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'email': request.form['email'],
                'hashed_pw': hashed_pw,
                'salt': salt
            }
            print query
            mysql.query_db(query, data)
            return redirect('/about')
    return redirect('/')


@app.route('/signIn', methods=['POST'])
def sign_in():
    email = request.form['email']
    password = request.form['password']
    user_query = "SELECT * FROM user WHERE email = :email LIMIT 1"
    query_data = {'email': email}
    user = mysql.query_db(user_query, query_data)
    print user
    if len(user) != 0:
        encrypted_password = md5.new(password + user[0]['salt']).hexdigest()
        if user[0]['password'] == encrypted_password:
            return redirect('/about')
        else:
            flash("Wrong password or username!")
    return redirect('/')

@app.route('/about' )
def show_user():
    if 'id' not in session:
    	return redirect('/')
    return render_template('about.html')


@app.route('/sign_out', methods=['GET'])
def back():
    return render_template('index.html')

app.run(debug=dev)
