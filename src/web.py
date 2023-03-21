from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'

from database import get_db, init_db

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
        
@app.route('/profiles')
def profiles():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    return render_template('profiles.html', users=users)
        
if __name__ == '__main__':
    init_db()
    app.run(debug=True)


