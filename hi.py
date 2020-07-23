#! /usr/bin/env python

import os
from flask_wtf import FlaskForm
import secrets
from PIL import Image
from flask import Flask, render_template, flash, request, url_for, redirect, session,g
from wtforms import BooleanField, StringField, SubmitField, PasswordField, validators, IntegerField, RadioField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError, Required
from flask_bcrypt import Bcrypt
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf.file import FileField, FileAllowed
from flask_login import login_user, current_user, logout_user, login_required, LoginManager, UserMixin
from flask_wtf.csrf import CSRFProtect
from werkzeug import secure_filename
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

import pymysql
pymysql.install_as_MySQLdb()

import configparser
from flask import Flask, render_template, request
import mysql.connector

# Read configuration from file.
config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://team_10:127d79ec@eecslab-9:3306/team_10'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# Create a function for fetching data from the database.
def sql_query(sql):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def sql_query_one(sql):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result

def sql_noreturn(sql):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor()
    cursor.execute(sql)
    cursor.close()
    db.commit()
    db.close()

def sql_execute(sql):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

patch_request_class(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

class liketable(db.Model):
   __tablename__ = 'liketable'
   like_id = db.Column(db.Integer,primary_key = True,autoincrement=True)
   user_username = db.Column(db.String(20), )
   liked_username = db.Column(db.String(20), db.ForeignKey('user.username'))

class aggregate(db.Model):
    __tablename__ = 'aggregate'
    content = db.Column(db.String(100), nullable = True)
    usercount = db.Column(db.Integer, primary_key=True)
    average_age = db.Column(db.Integer, nullable = True)
    average_wage = db.Column(db.Integer, nullable = True)

class User(db.Model,UserMixin):
    __tablename__ = 'user'
    username = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(120),  nullable=True)
    occupation = db.Column(db.String(60), nullable=True)
    wage = db.Column(db.Integer, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(60), nullable=True)
    phototype = db.Column(db.String(20), nullable=False)
    required_occupation = db.Column(db.String(60), nullable=True)
    required_wage = db.Column(db.Integer, nullable=True)
    required_age = db.Column(db.Integer, nullable=True)
    required_gender = db.Column(db.String(60), nullable=True)
    password = db.Column(db.String(60), nullable=True)
    

    def is_active(self):
        return True

    def get_id(self):
        return self.username
    
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    



class RegistrationForm(FlaskForm):
    username = StringField('username',
                           validators=[DataRequired(), Length(min=2, max=60)])
    email = StringField('email',
                        validators=[DataRequired(), Email()])
    occupation = StringField('occupation', validators=[DataRequired(), Length(min=2, max=60)])
    age = IntegerField('age', validators=[DataRequired()])
    wage = IntegerField('wage', validators=[DataRequired()])
    gender = RadioField('gender', choices=[('Male','Male'),('Female' ,'Female'),('Other','Other')])
    password = PasswordField('password',validators = [DataRequired()])
    confirm_password = PasswordField('confirm password',
                                     validators=[DataRequired(), EqualTo('password')])
    picture = FileField('picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Sign Up')



    def validate_username(self, username):
        sql = "select username from user where username ='" + username.data + "';"
        user = sql_query_one(sql)
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        sql = "select username from user where username ='" + email.data + "';"
        user = sql_query_one(sql)
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')



class RequirementForm(FlaskForm):
    occupation = StringField('occupation', validators=[DataRequired(), Length(min=2, max=60)])
    age = IntegerField('age', validators=[DataRequired()])
    wage = IntegerField('wage', validators=[DataRequired()])
    gender = RadioField('gender', choices=[('Male','Male'),('Female' ,'Female'),('Other','Other')],validators=[DataRequired()])
    submit = SubmitField('submit')





class LoginForm(FlaskForm):
    username = StringField('username',
                        validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Login')





class UpdateAccountForm(FlaskForm):
    username = StringField('username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])


    occupation = StringField('occupation')
    age = IntegerField('age', [validators.optional()])
    wage = IntegerField('wage', [validators.optional()])
    # occupation = StringField('occupation', [validators.Length(min=1, max=60)])
    # age = IntegerField('age',validators=[DataRequired()])
    # wage = IntegerField('wage', validators=[DataRequired()])
    picture = FileField('picture', validators=[FileAllowed(['jpg', 'png'])])
    password = PasswordField('New password')
    # password = PasswordField('New password', [
    #     validators.DataRequired()
    # ])
    confirm = PasswordField('Repeat password')
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            sql = "select username from user where username ='" + username.data + "';"
            user = sql_query_one(sql)
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')



    def validate_email(self, email):
        if email.data != current_user.email: 
            sql = "select email from user where email ='" + email.data + "';"
            user = sql_query_one(sql)
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/welcome.html')
def welcome():
    return render_template('welcome.html')

# @app.route('/matchlist.html')
# def matchlist():
#     return render_template('matchlist.html')

@app.route('/sign_up.html', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        sql = "insert into user (username, phototype, gender, occupation, wage, password, age, email) values('%s', '%s', '%s', '%s', %d, '%s', %d, '%s')" % (form.username.data, form.picture.data, form.gender.data , form.occupation.data, form.wage.data, form.password.data, form.age.data, form.email.data)
        sql_noreturn(sql)
        # fp = open(os.path.join(app.root_path, 'static/images', 'default.jpg')) 
        # img = fp.read() 
        # fp.close() 
        # sql1 = "update user set phototype = '%s' where username = '%s';" % (mysql.Binary(img), current_user.username)
        # sql_noreturn(sql1)
        user = User(username=form.username.data, email=form.email.data, occupation=form.occupation.data, age=form.age.data, wage=form.wage.data, gender=form.gender.data, password=form.password.data)
        sql1 = "select count(*) from user"
        user_count = sql_query_one(sql1)
        sql2 = "SELECT AVG(age) FROM user"
        avg_wage = sql_query_one(sql2)
        sql3 = "SELECT AVG(wage) FROM user"
        avg_age = sql_query_one(sql3)
        sql12 = "select usercount from aggregate;" 
        result12 = sql_query_one(sql12)
        if result12 is None:
            sql13 = "insert into aggregate (usercount, average_age, average_wage) values(%d, %d, %d)" % (user_count[0], avg_age[0], avg_wage[0])
            sql_noreturn(sql13)
        else:
            sql4 = "Update aggregate set usercount = %d, average_age = %d, average_wage = %d;" % (user_count[0], avg_age[0], avg_wage[0])
            sql_noreturn(sql4)
        login_user(user)
        return redirect(url_for('requirement'))
    return render_template('sign_up.html', title='Sign up', form=form)

@app.route('/requirement.html', methods=['GET', 'POST'])
@login_required
def requirement():
    form = RequirementForm()
    if form.validate_on_submit():
        sql = "update user set required_age = %d, required_gender = '%s', required_occupation = '%s', required_wage = %d where username = '%s';" % (form.age.data, form.gender.data, form.occupation.data, form.wage.data, current_user.username)
        sql_noreturn(sql)
        return redirect(url_for('welcome'))
    return render_template('requirement.html', form = form)

@app.route('/profile.html', methods=['GET', 'POST'])

@login_required

def profile():
    form = UpdateAccountForm()
    #full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'shovon.jpg')
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            sql1 = "update user set phototype = '%s' where username = '%s';" % (picture_file, current_user.username)
            sql_noreturn(sql1)
        if form.username.data:
            sql = "update user set username = '%s' where username = '%s';" % (form.username.data, current_user.username)
            sql_noreturn(sql)
        if form.email.data:
            sql = "update user set email = '%s' where username = '%s';" % (form.email.data, current_user.username)
            sql_noreturn(sql)
        if form.occupation.data:
            sql = "update user set occupation = '%s' where username = '%s';" % (form.occupation.data, current_user.username)
            sql_noreturn(sql)
        if form.age.data:
            sql = "update user set age = %d where username = '%s';" % (form.age.data, current_user.username)
            sql_noreturn(sql)
        if form.wage.data:
            sql = "update user set wage = %d where username = '%s';" % (form.wage.data, current_user.username)
            sql_noreturn(sql)
        if form.password.data:
            sql = "update user set password = '%s' where username = '%s';" % (form.password.data, current_user.username)
            sql_noreturn(sql)
        flash('Your account has been updated!')
        return redirect(url_for('welcome'))
    elif request.method == 'GET': 
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.occupation.data = current_user.occupation
        form.age.data = current_user.age
        form.password.data = current_user.password
    phototype = url_for('static', filename='images/' + current_user.phototype)
    return render_template('profile.html', title='profile', phototype=phototype, form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
    form_picture.save(picture_path)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/sign_in.html', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
       return redirect(url_for('welcome'))
    form = LoginForm()
    if form.validate_on_submit():
        flash('form is valid')
        sql = "select * from user where username = '%s';" % (form.username.data)
        result = sql_query_one(sql)
        #user = User.query.filter_by(username=form.username.data).first()
        user = User(username=result[0], email=result[6], occupation=result[2], age=result[5], wage=result[3], gender=result[1], password=result[4])
        if (result[4] == form.password.data):
            flash('password is correct')
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('welcome'))
    flash(form.errors)
    return render_template('sign_in.html',form = form)

@app.route('/likepeople.html')
@login_required
def display():
    wage=current_user.required_wage
    age=current_user.required_age
    gender=current_user.required_gender
    occupation=current_user.required_occupation
    sql = "select username, gender, age, wage, occupation, email, phototype from user where username <> '%s' and gender = '%s'and (age - %d) < 3 and (age - %d) > -3 and (wage - %d) < 200 and (wage - %d) > -200 and occupation = '%s';" % (current_user.username, current_user.required_gender, current_user.required_age, current_user.required_age, current_user.required_wage, current_user.required_wage, current_user.required_occupation)
    result = sql_query(sql)
    if result is None:
        flash('Sorry, no one match your requirement at this time')
        return redirect(url_for('welcome'))
    else:
        return render_template('likepeople.html', result=result)

#phototype = url_for('static', filename='images/' + current_user.phototype)

@app.route('/likepeople/<username>')
@login_required
def likepeople(username):
    sql1 = "select user_username, liked_username from liketable where user_username = '%s' and liked_username = '%s'" % (current_user.username, username)
    result = sql_query_one(sql1)
    if result is None:
        sql = "insert into liketable (user_username, liked_username) values ('%s', '%s')" % (current_user.username, username)
        sql_noreturn(sql)
        sql2 = "select like_id from liketable where user_username = '%s' and liked_username = '%s'" % (current_user.username, username)
        result1 = sql_query_one(sql2)
        sql3 = "insert into tolike (username, like_id) values ('%s', '%s')" % (current_user.username, result1[0])
        sql_noreturn(sql3)
        return redirect(url_for('welcome'))
    else:
        flash('Have liked!')
        return redirect(url_for('display_liked'))

@app.route('/liketable.html')
@login_required
def display_liked():
    sql = "select username, gender, age, wage, occupation, email, phototype from user where username in (select liked_username from liketable where user_username = '%s')" % (current_user.username)
    result = sql_query(sql)
    if result is None:
        flash('Sorry, no one match your requirement at this time')
        return redirect(url_for('welcome'))
    else:
        return render_template('liketable.html', result=result)

@app.route('/liketable/<username>')
def liketable(username):
    sql1 = "delete from tolike where username = '%s';" % (current_user.username)
    sql_noreturn(sql1)
    sql = "delete from liketable where user_username = '%s' and liked_username = '%s';" % (current_user.username, username)
    sql_noreturn(sql)
    flash('You have stopped following ' + username + '.')
    return redirect(url_for('welcome'))



@app.route("/logout")

def logout():

    logout_user()

    return redirect(url_for('index'))


@app.route("/delete")
def delete():
    sql1 = "delete from user where username = '%s'" % (current_user.username)
    sql_noreturn(sql1)
    sql2 = "delete from tolike where username = '%s'" % (current_user.username)
    sql_noreturn(sql2)
    sql3 = "delete from liketable where user_username = '%s'" % (current_user.username)
    sql_noreturn(sql3)
    sql4 = "delete from liketable where liked_username = '%s'" % (current_user.username)
    sql_noreturn(sql4)
    # sql5 = "delete from tomatch where user_username = '%s'" % (current_user.username)
    # sql_noreturn(sql5)
    # sql6 = "delete from matchtable where user1_username = '%s'" % (current_user.username)
    # sql_noreturn(sql6)
    # sql7 = "delete from matchtable where user2_username = '%s'" % (current_user.username)
    # sql_noreturn(sql7)
    sql8 = "select count(*) from user"
    user_count = sql_query_one(sql8)
    if user_count[0] == 0:
        sql11 = "Update aggregate set usercount = %d, average_age = %d, average_wage = %d;" % (user_count[0], 0, 0)
        sql_noreturn(sql11)
    else:
        sql9 = "SELECT AVG(age) FROM user"
        avg_wage = sql_query_one(sql9)
        sql10 = "SELECT AVG(wage) FROM user"
        avg_age = sql_query_one(sql10)
        sql11 = "Update aggregate set usercount = %d, average_age = %d, average_wage = %d;" % (user_count[0], avg_age[0], avg_wage[0])
        sql_noreturn(sql11)
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":

    app.run(debug=True)

