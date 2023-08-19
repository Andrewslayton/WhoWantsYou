from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from wtforms import StringField
from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime
from sqlalchemy import and_, or_

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SECRET_KEY'] = 'supersecretkey'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def init_db():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False )

    def get_id(self):
        return str(self.id)

    @staticmethod
    def check_password(user_password, hashed_password):
        return check_password_hash(hashed_password, user_password)
    
profile = db.relationship('Profile', backref='user', uselist=False)

class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100))
    bio = db.Column(db.String(500))
    images = db.relationship('ProfileImages', backref='profile', lazy=True)

class ProfileImages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    image_path = db.Column(db.String(255))


class Matches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id_1 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_id_2 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.Boolean, default=False)  # False = not yet matched, True = matched
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists.')
class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

@app.route('/createprofile', methods=['GET', 'POST'])
@login_required
def index():

    profile_exists = Profiles.query.filter_by(user_id=current_user.id).first()
    if profile_exists:
        return redirect(url_for('profiles'))  
    if request.method == 'POST':
        name = request.form['name']
        bio = request.form['bio']
        files = request.files.getlist('picture')  
        try:
            profile = Profiles(user_id=current_user.id, name=name, bio=bio)
            db.session.add(profile)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return render_template('index.html', error="Error creating profile. Please try again.")           
        try:
            for file in files:
                if file:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                        
                    image = ProfileImages(profile_id=profile.id, image_path=file_path)
                    db.session.add(image)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return render_template('index.html', error="Error uploading images. Please try again.")
        return redirect(url_for('profiles'))
    return render_template('index.html')






@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        if form.is_submitted():  # Checks if the form was submitted
            flash("Account not created. Try another username!")
    return render_template('register.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            if form.is_submitted():
                flash("Incorrect username or password", "danger")
    return render_template('login.html', form=form)


    matched_user_ids = [match.user_id_2 for match in Matches.query.filter_by(user_id_1=current_user.id).all()]
@app.route('/profiles')
@login_required
def profiles():
    # comment
    confirmed_matches = Matches.query.filter_by(status=True).all()
    matched_user_ids = [match.user_id_2 for match in Matches.query.filter_by(user_id_1=current_user.id).all()]
    confirmed_partner_ids = matched_user_ids.copy()  # Initialize with matched_user_ids
    # comment
    for match in confirmed_matches:
        if match.user_id_1 == current_user.id:
            confirmed_partner_ids.append(match.user_id_2)
        elif match.user_id_2 == current_user.id:
            confirmed_partner_ids.append(match.user_id_1)
    # comment
    profiles = Profiles.query.filter(
        ~Profiles.user_id.in_(confirmed_partner_ids),
        Profiles.user_id != current_user.id
    ).all()
    images = {profile.id: [img.image_path for img in profile.images] for profile in profiles}
    for image in images:
        print(image)
    return render_template('profiles.html', profiles=profiles, images=images)



@app.route('/match/<profile_id>', methods=['POST'])
@login_required
def match(profile_id):
    profile = Profiles.query.get(profile_id)
    if not profile:
        return {"error": "Profile not found"}, 404
    #comment
    existing_match = Matches.query.filter(
        and_(Matches.user_id_1 == profile.user_id, Matches.user_id_2 == current_user.id)
    ).first()
    if existing_match:
        # comment
        existing_match.status = True
    else:
        # comment
        new_match = Matches(user_id_1=current_user.id, user_id_2=profile.user_id, status=False)
        db.session.add(new_match)
    db.session.commit()
    return redirect(url_for('profiles'))


@app.route('/matches', methods=['GET'])
@login_required
def matches():
    user_id = current_user.id
    # comment
    match_records = Matches.query.filter(
        ((Matches.user_id_1 == user_id) | (Matches.user_id_2 == user_id)), 
        Matches.status == True
    ).all()
    matched_profiles = []
    for record in match_records:
        # comment
        if record.user_id_1 == user_id:
            matched_user_id = record.user_id_2
        else:
            matched_user_id = record.user_id_1
        # Fcomment
        matched_profile = Profiles.query.filter_by(user_id=matched_user_id).first()
        if matched_profile:
            matched_profiles.append(matched_profile)
    return render_template('matches.html', matched_profiles=matched_profiles)


@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    # comment
    Matches.query.filter_by(user_id_1=current_user.id).delete()
    Matches.query.filter_by(user_id_2=current_user.id).delete()
    # comment
    Profiles.query.filter_by(user_id=current_user.id).delete()
    # comment
    User.query.filter_by(id=current_user.id).delete()
    db.session.commit()
    # comment
    logout_user()
    flash('Your account has been deleted.')
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.cli.command("initdb")
def initdb_command():
    """Creates the database tables."""
    db.create_all()
    print('databases initialized')


if __name__ == '__main__':
    with app.app_context():
        db
    app.run(debug=True)
