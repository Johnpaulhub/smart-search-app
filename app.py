from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'super_secret_production_key_change_this'

DB_NAME = 'database.db'

# Initialize SQLite database and tables
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Search entries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            contributor TEXT NOT NULL
        )
    ''')
    
    # Seed default accounts and entries if tables are empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        admin_pass = generate_password_hash('adminpassword123')
        user_pass = generate_password_hash('password123')
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', admin_pass, 'admin'))
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('user', user_pass, 'public'))
    
    cursor.execute('SELECT COUNT(*) FROM entries')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO entries (title, content, contributor) VALUES (?, ?, ?)', 
                       ('Cow', "Custom record for 'cow'. Feel free to update or add more details!", 'Smart System'))
        cursor.execute('INSERT INTO entries (title, content, contributor) VALUES (?, ?, ?)', 
                       ('Python Programming', "A high-level programming language used for web development and automation.", 'Admin'))
    
    conn.commit()
    conn.close()

# Run database setup on startup
init_db()

@app.route('/')
def home():
    if 'username' not in session:
        return render_template('index.html', logged_in=False)
    
    return render_template(
        'index.html', 
        logged_in=True, 
        username=session['username'], 
        role=session.get('role', 'public')
    )

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT password, role FROM users WHERE username = ?', (username,))
    user_record = cursor.fetchone()
    conn.close()
    
    if user_record and check_password_hash(user_record[0], password):
        session['username'] = username
        session['role'] = user_record[1]
        flash('Successfully logged in!', 'success')
    else:
        flash('Invalid username or password. Please try again.', 'error')
        
    return redirect(url_for('home'))

@app.route('/search', methods=['POST'])
def search():
    if 'username' not in session:
        flash('You must log in to search.', 'error')
        return redirect(url_for('home'))
    
    query = request.form.get('query', '').strip()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, content, contributor FROM entries WHERE title LIKE ?', (f'%{query}%',))
    rows = cursor.fetchall()
    conn.close()
    
    # Format database rows into dictionaries for the template
    results = [{"id": r[0], "title": r[1], "content": r[2], "contributor": r[3]} for r in rows]
    
    return render_template(
        'index.html',
        logged_in=True,
        username=session['username'],
        role=session.get('role', 'public'),
        results=results,
        query=query
    )

@app.route('/contribute', methods=['POST'])
def contribute():
    if 'username' not in session:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('home'))
        
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    contributor = session['username']
    
    if title and content:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO entries (title, content, contributor) VALUES (?, ?, ?)', (title, content, contributor))
        conn.commit()
        conn.close()
        flash('New word/topic added successfully!', 'success')
    else:
        flash('All fields are required to contribute.', 'error')
        
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
