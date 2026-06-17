from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, send_from_directory
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

def get_db():
    db = sqlite3.connect('database/student_mark.db')
    db.row_factory = sqlite3.Row
    return db

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/students')
def students():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('students.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        firstname = request. form['firstname' ]
        password = request. form['password' ]
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE firstname = ?', (firstname, )
            ).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id' ] = user['id'] 
            session['firstname'] = user['firstname']
            return redirect(url_for('index'))
        flash('Invalid firstname or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET' , 'POST'])
def register():
    if request.method == 'POST':
        firstname = request. form['firstname' ]
        password = request. form['password' ]
        
        db = get_db()
        try: 
            db.execute(
                'INSERT INTO users (firstname, password) VALUES (?, ?) ' ,
                (firstname, generate_password_hash(password))
            )
            db.commit()
            flash('Registration successful! Please log in. ', 'success') 
            return redirect(url_for('login'))
        except sqlite3. IntegrityError: 
            flash('Firstname already entered!', 'error') 
    return render_template('register.html')

@app.route('/logout')
def logout():
    session. clear()
    return redirect(url_for('login'))

#EDIT STUFF

@app.route('/offline') 
def offline():
    response = make_response(render_template('offline.html'))
    return response

@app.route('/service-worker.js') 
def sw():
    response = make_response(
        send_from_directory(os.path.join(app.root_path, 'static/js'), 
                            'service-worker.js')
                            ) 
    return response

@app.route('/manifest.json') 
def manifest():
    response = make_response(
        send_from_directory(os.path.join(app.root_path, 'static'), 
                            'manifest.json') 
                            ) 
    return response

#MORE STUFF



if __name__ == '__main__': 
    app.run(debug=True)
