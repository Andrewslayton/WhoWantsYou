from flask import Flask, request, render_template
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
    return render_template('index.html')
        
if __name__ == '__main__':
    init_db()
    app.run(debug=True)

