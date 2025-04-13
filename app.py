from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'gizli'

def db():
    conn = sqlite3.connect('arasorhun.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = db()
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/kategori/<kategori>')
def kategori(kategori):
    conn = db()
    posts = conn.execute('SELECT * FROM posts WHERE category = ? ORDER BY id DESC', (kategori,)).fetchall()
    conn.close()
    return render_template('kategori.html', kategori=kategori, posts=posts)

@app.route('/yazi/<int:id>')
def yazi(id):
    conn = db()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('yazi.html', post=post)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = db()
        user = conn.execute('SELECT * FROM admin WHERE username=? AND password=?',
                            (request.form['username'], request.form['password'])).fetchone()
        if user:
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
    conn = db()
    if request.method == 'POST':
        conn.execute('INSERT INTO posts (title, content, created_at, category) VALUES (?, ?, ?, ?)',
                     (request.form['title'], request.form['content'],
                      datetime.now().strftime('%Y-%m-%d %H:%M'), request.form['category']))
        conn.commit()
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin.html', posts=posts)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
