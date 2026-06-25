from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, send_from_directory
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

def get_db():
    db = sqlite3.connect('database/student_mark.db')
    db.row_factory = sqlite3.Row
    return db

def column_exists(db, table, column):
    cur = db.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    return column in cols

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    students = db.execute('''
                          SELECT * FROM students
                          ORDER BY firstname ASC;
                          ''').fetchall()
    subjects = db.execute('''
                          SELECT * FROM subject
                          ORDER BY subject ASC;
                         ''').fetchall()
    return render_template('index.html', students=students, subjects=subjects)

@app.route('/student/<int:student_id>')
def student(student_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    students = db.execute('''
                          SELECT * FROM students
                          ORDER BY firstname ASC;
                          ''').fetchall()
    subjects = db.execute('''
                          SELECT * FROM subject
                          ORDER BY subject ASC;
                         ''').fetchall()
    student = db.execute(
        'SELECT * FROM students WHERE id = ?',
        (student_id,)).fetchone()
    marks = db.execute(
        'SELECT id, subject, marks as mark, last_updated FROM Marks WHERE student_id = ? ORDER BY marks DESC',
        (student_id,)).fetchall()
    edit_mark_id = request.args.get('edit')
    return render_template('student.html', students=students, subjects=subjects, student=student, marks=marks, edit_mark_id=edit_mark_id)

@app.route('/subject/<int:subject_id>')
def subject(subject_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    students = db.execute('''
                          SELECT * FROM students
                          ORDER BY firstname ASC;
                          ''').fetchall()
    subjects = db.execute('''
                          SELECT * FROM subject
                          ORDER BY subject ASC;
                         ''').fetchall()
    #Copilot's Code
    # Detect whether the subject table uses `name` or `subject` column
    try:
        subj_cols = [r[1] for r in db.execute("PRAGMA table_info(subject)").fetchall()]
    except sqlite3.OperationalError:
        subj_cols = []
    if 'name' in subj_cols:
        subject = db.execute('SELECT id, name as subject FROM subject WHERE id = ?', (subject_id,)).fetchone()
    elif 'subject' in subj_cols:
        subject = db.execute('SELECT id, subject as subject FROM subject WHERE id = ?', (subject_id,)).fetchone()
    else:
        subject = {'id': subject_id, 'subject': 'Unknown'}
    marks = db.execute('''
        SELECT m.id as id, m.marks as marks, m.last_updated as last_updated,
               s.id as student_id, s.firstname as firstname, s.lastname as lastname
        FROM Marks m
        JOIN students s ON m.student_id = s.id
        WHERE m.subject_id = ?
        ORDER BY s.firstname ASC
    ''', (subject_id,)).fetchall()
    edit_mark_id = request.args.get('edit')
    return render_template('subject.html', students=students, subject=subject, subjects=subjects, marks=marks, edit_mark_id=edit_mark_id)

#Copilot's Code
@app.route('/edit_mark/<int:mark_id>', methods=['POST'])
def edit_mark(mark_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    mark_row = db.execute('SELECT * FROM Marks WHERE id = ?', (mark_id,)).fetchone()
    if not mark_row:
        flash('Mark not found', 'error')
        return redirect(url_for('index'))

    try:
        new_mark = int(request.form.get('mark'))
    except (TypeError, ValueError):
        flash('Invalid mark value', 'error')
        return redirect(url_for('student', student_id=mark_row['student_id']))

    db.execute('''
        UPDATE Marks
        SET marks = ?, last_updated = ?
        WHERE id = ?
    ''', (new_mark, datetime.now().strftime('%d/%m/%Y'), mark_id))
    db.commit()
    flash('Mark updated', 'success')
    return redirect(url_for('student', student_id=mark_row['student_id']))

@app.route('/edit_subject/<int:mark_id>', methods=['POST'])
def edit_subject(mark_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    mark_row = db.execute('SELECT * FROM Marks WHERE id = ?', (mark_id,)).fetchone()
    if not mark_row:
        flash('Mark not found', 'error')
        return redirect(url_for('index'))

    try:
        new_mark = int(request.form.get('mark'))
    except (TypeError, ValueError):
        flash('Invalid mark value', 'error')
        sid = mark_row['subject_id'] if 'subject_id' in mark_row.keys() else 0
        return redirect(url_for('subject', subject_id=sid))

    db.execute('''
        UPDATE Marks
        SET marks = ?, last_updated = ?
        WHERE id = ?
    ''', (new_mark, datetime.now().strftime('%d/%m/%Y'), mark_id))
    db.commit()
    flash('Mark updated', 'success')
    sid = mark_row['subject_id'] if 'subject_id' in mark_row.keys() else 0
    return redirect(url_for('subject', subject_id=sid))

#Maha's Code    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        fullname = request. form['fullname' ]
        password = request. form['password' ]
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE fullname = ?', (fullname, )
            ).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id' ] = user['id'] 
            session['fullname'] = user['fullname']
            return redirect(url_for('index'))
        flash('Invalid full name or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET' , 'POST'])
def register():
    if request.method == 'POST':
        fullname = request. form['fullname' ]
        password = request. form['password' ]
        
        db = get_db()
        try: 
            db.execute(
                'INSERT INTO users (fullname, password) VALUES (?, ?) ' ,
                (fullname, generate_password_hash(password))
            )
            db.commit()
            flash('Registration successful! Please log in. ', 'success') 
            return redirect(url_for('login'))
        except sqlite3. IntegrityError: 
            flash('Full name already entered!', 'error') 
    return render_template('register.html')

@app.route('/logout')
def logout():
    session. clear()
    return redirect(url_for('login'))

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

if __name__ == '__main__': 
    app.run(debug=True)