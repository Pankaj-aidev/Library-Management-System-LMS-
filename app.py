from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Flask secret key (used for sessions)
app.secret_key = os.getenv("SECRET_KEY")

# MySQL Configuration using .env variables
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

#LOGIN
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['username'] = username
            return redirect(url_for('books'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

#VIEW BOOKS
@app.route('/books')
def books():
    if 'username' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM books")
    books = cur.fetchall()
    cur.close()
    return render_template('books.html', books=books)

#ADD BOOK
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO books (title, author, available) VALUES (%s, %s, TRUE)", (title, author))
        mysql.connection.commit()
        cur.close()
        flash("Book added successfully!", "success")
        return redirect(url_for('books'))
    return render_template('add.html')

#ISSUE BOOK
@app.route('/issue', methods=['GET', 'POST'])
def issue_book():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title FROM books WHERE available = TRUE")
    available_books = cur.fetchall()

    if request.method == 'POST':
        book_id = request.form['book_id']
        issued_to = request.form['issued_to']
        cur.execute("UPDATE books SET available = FALSE, issued_to = %s WHERE id = %s", (issued_to, book_id))
        mysql.connection.commit()
        cur.close()
        flash("Book issued successfully!", "info")
        return redirect(url_for('books'))

    cur.close()
    return render_template('issue.html', available_books=available_books)

#RETURN BOOK
@app.route('/return', methods=['GET', 'POST'])
def return_book():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title FROM books WHERE available = FALSE")
    issued_books = cur.fetchall()

    if request.method == 'POST':
        book_id = request.form['book_id']
        cur.execute("UPDATE books SET available = TRUE, issued_to = NULL WHERE id = %s", [book_id])
        mysql.connection.commit()
        cur.close()
        flash("Book returned successfully!", "warning")
        return redirect(url_for('books'))

    cur.close()
    return render_template('return.html', issued_books=issued_books)

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.", "secondary")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
