
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'gizli-anahtar'

def init_db():
    with sqlite3.connect('arasorhun.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        content TEXT,
                        created_at TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS admin (
                        username TEXT,
                        password TEXT
                    )''')
        conn.commit()
        c.execute("SELECT * FROM admin")
        if not c.fetchall():
            c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("admin", "1234"))
            conn.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('arasorhun.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
            if c.fetchone():
                session['admin'] = True
                return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    with sqlite3.connect('arasorhun.db') as conn:
        c = conn.cursor()
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            c.execute("INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)",
                      (title, content, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
        c.execute("SELECT * FROM posts ORDER BY id DESC")
        posts = c.fetchall()
    return render_template('admin.html', posts=posts)

@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    with sqlite3.connect('arasorhun.db') as conn:
        c = conn.cursor()
        c.execute("DELETE FROM posts WHERE id=?", (id,))
        conn.commit()
    return redirect(url_for('admin'))

@app.route('/')
def index():
    with sqlite3.connect('arasorhun.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM posts ORDER BY id DESC")
        posts = c.fetchall()
    return render_template('index.html', posts=posts)

@app.route('/yazi/<int:id>')
def yazi(id):
    with sqlite3.connect('arasorhun.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM posts WHERE id=?", (id,))
        post = c.fetchone()
    return render_template('yazi.html', post=post)

@app.route('/yazar')
def yazar():
    return render_template('yazar.html')

if __name__ == '__main__':
    init_db()
    import os

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

