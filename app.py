from flask import Flask, render_template, url_for, flash, redirect
from form import Registration, Login
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import re  


app = Flask(__name__)
app.config['SECRET_KEY'] = 'efa1dc43ee625d0d91fcb61337ef61c5'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

#TODO - Hide the secret key in a .mv file and ensure that the file is ignored when pushed to repo 
# TODO - create a post class model that links to the user  

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&+=!])[A-Za-z\d@#$%^&+=!]{8,}$'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}','{self.firstname}',  '{self.lastname}', '{self.email}')"

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = Login()
    #If they enter wrong email or password, they cannot log in. 
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', form=form)

@app.route("/Register", methods=['GET', 'POST'])
def register():
    form = Registration()

    if form.validate_on_submit():
        
        existing_email_user = User.query.filter((User.email == form.email.data) | (User.username == form.username.data)).first()
            # if username and/or the email is already registered, they must choose different username or if email is registered must sign in
        if existing_email_user:
            if existing_email_user.email == form.email.data:
                flash('Email address is already registered. Please sign in or choose a different email address.', 'warning')
            if existing_email_user.username == form.username.data:
                flash('Username is already registered. Please choose a different username.', 'warning')
            return redirect(url_for('register'))
        else:
            # This checks if the password meets complexity requirements
            if not re.match(password_pattern, form.password.data):
                flash('Password does not meet complexity requirements. It must contain at least 1 lowercase letter, 1 uppercase letter, 1 digit, 1 special character, and be at least 8 characters long.', 'danger')
                return redirect(url_for('register'))
            # This ensures that the password is in hashed format so no one can access the password. Also add the user who created account to the database
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, firstname=form.Firstname.data, lastname=form.lastname.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.Firstname.data} {form.lastname.data}! You are now able to log in', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)
if __name__ == '__main__':
    
    
    with app.app_context():
        db.create_all()
    app.run(debug=True)