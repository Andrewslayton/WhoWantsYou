from flask import Flask, request, render_template, redirect, url_for,flash 
from werkzeug.utils import secure_filename
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
import os 
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'my_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/images'

from database import get_db, init_db
from modelUser import User

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        bio = request.form['bio']
        file = request.files['picture']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            picture = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            picture = None
        db = get_db()
        c = db.cursor()
        c.execute("INSERT INTO users (name, bio, picture) VALUES (?, ?, ?)", (name, bio, picture))
        db.commit()
        return redirect(url_for('profiles'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if not username or not password or not confirm_password:
            error = 'Please fill out all required fields.'
            return render_template('register.html', error=error)
        if password != confirm_password:
            error = 'Passwords do not match.'
            return render_template('register.html', error=error)
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user is not None:
            error = 'Username already taken.'
            flash('Sorry, username already taken.')
            return render_template('register.html', error=error)
        db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        db.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user is None:
            error = 'Invalid username or password.'
            return render_template('login.html', error=error)
        if not User.check_password(password, user['password']):
            error = 'Invalid username or password.'
            return render_template('login.html', error=error)
        login_user(User(user['id'], user['username'], user['password']), remember=True)
        return redirect(url_for('profiles'))
    return render_template('login.html')
        
@app.route('/profiles')
@login_required
def profiles():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    return render_template('profiles.html', users=users)
        
if __name__ == '__main__':
    init_db()
    app.run(debug=True)


