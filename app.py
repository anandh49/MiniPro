from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, abort
import bcrypt
import os
from flask_mysqldb import MySQL
from mysql.connector import MySQLConnection

app = Flask(__name__)
app.secret_key = "recipebook"

app.config['MYSQL_HOST'] = 'localhost'  
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'smith49'  
app.config['MYSQL_DB'] = 'userdb' 
mysql = MySQL(app)
 

config1 = {
    "host": "localhost",
    "user": "root",
    "password": "smith49",
    "database": "search"
}

db = MySQLConnection(**config1)
cursor = db.cursor()
db.commit()

TEMPLATE_DIR = "templates"
allowed_pages = {file[:-5] for file in os.listdir(TEMPLATE_DIR) if file.endswith('.html')}

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cur.fetchone()
    cur.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        session['user_id'] = user[0]  
        return redirect(url_for('main'))
    else:
        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(url_for('home'))


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_user():
    username = request.form['username']
    password = request.form['password']
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users WHERE username = %s', (username,))
    existing_user = cur.fetchone()

    if existing_user:
        flash('Username already exists, try a different one.', 'danger')
        cur.close()
        return redirect(url_for('register'))

    cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
    mysql.connection.commit()
    cur.close()

    flash('Registration successful! You can now log in.', 'success')
    return redirect(url_for('home'))

@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/<page>')
def show_page(page):
    if page in allowed_pages:
        return render_template(f'{page}.html')
    else:
        abort(404)  

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    search_query = data.get("search")

    if search_query:
        cursor.execute("SELECT * FROM search_queries WHERE query = %s", (search_query,))
        existing_entry = cursor.fetchone()
        
        if existing_entry and search_query in allowed_pages:
            return jsonify({"redirect": url_for('show_page', page=search_query)})        
        else:
            return jsonify({"message": "Sorry, Recipe Not Found!"}), 404
    else:
        return jsonify({"message": "Invalid input"}), 400

if __name__ == '__main__':
    app.run(debug=True)
