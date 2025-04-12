
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'gizli-anahtar'

def get_db_connection():
    conn = sqlite3.connect('arasorhun.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admin WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if admin:
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
    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M')
        conn.execute('INSERT INTO posts (title, content, created_at, category) VALUES (?, ?, ?, ?)',
                     (title, content, created_at, category))
        conn.commit()
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin.html', posts=posts)

@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/yazi/<int:id>')
def yazi(id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('yazi.html', post=post)

@app.route('/kategori/<kategori_adi>')
def kategori(kategori_adi):
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts WHERE category = ? ORDER BY id DESC', (kategori_adi,)).fetchall()
    conn.close()
    return render_template('kategori.html', kategori=kategori_adi, posts=posts)

@app.route('/yazar')
def yazar():
    return render_template('yazar.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
