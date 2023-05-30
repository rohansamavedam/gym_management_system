from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, validators
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Email, ValidationError, NoneOf
from app.models import User


class LoginForm(FlaskForm):
    usertype = SelectField('Usertype',
                           choices=[('Member', 'Member'),
                                    ('Employee', 'Employee')],
                           validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class MemberForm(FlaskForm):

	choices = [('Month-to-Month', 'Month-to-Month'), ('6-Month', '6-Month'), ('Yearly', 'Yearly')]

	name = StringField('Name', 
		validators = [validators.DataRequired(),
		 validators.Length(min=1, max=50)])

	username = StringField('Username', [
		validators.InputRequired(),])

	email = StringField('Email', validators=[
		DataRequired(),
		Email()])

	password = PasswordField('Password', [
        validators.DataRequired(message='Password is required.'),
        validators.EqualTo('confirm', message='Passwords must match.'),
        validators.Length(message='Password must be at least 6 characters long.', min=6)
    ])

	confirm = PasswordField('Confirm Password', validators = [
		validators.DataRequired(), 
		validators.Length(min=6, max=10)])

	plan = SelectField('Select Plan', choices=choices)

	startdate = DateField('Start Date', format = '%Y-%m-%d', validators = [validators.DataRequired()])

	address = StringField('Address', validators = [
		validators.DataRequired(), 
		validators.Length(min=1, max=100)])

	city = StringField('City', validators = [
		validators.DataRequired(), 
		validators.Length(min=1, max=50)])

	phone = StringField('Contact Number', [
		validators.DataRequired(), 
		validators.Length(min=1, max=12)])

	submit = SubmitField('Submit')


class DeactivateForm(FlaskForm):
	email = StringField('Email', validators = [DataRequired()])

	deactivate = SubmitField('Deactivate') 

class RenewMembership(FlaskForm):

	choices = [('Month-to-Month', 'Month-to-Month'), ('6-Month', '6-Month'), ('Yearly', 'Yearly')]

	email = StringField('Email', validators = [DataRequired()])

	plan = SelectField('Select Plan', choices=choices)

	startdate = DateField('Start Date', format = '%Y-%m-%d', validators = [validators.DataRequired()])

	renew = SubmitField('Renew') 

class FreetrialForm(FlaskForm):

	name = StringField('Name', 
		validators = [validators.DataRequired(),
		 validators.Length(min=1, max=50)])

	username = StringField('Username', [
		validators.InputRequired(),])

	email = StringField('Email', validators=[
		DataRequired(),
		Email()])

	password = PasswordField('Password', [
        validators.DataRequired(message='Password is required.'),
        validators.EqualTo('confirm', message='Passwords must match.'),
        validators.Length(message='Password must be at least 6 characters long.', min=6)
    ])

	confirm = PasswordField('Confirm Password', validators = [
		validators.DataRequired(), 
		validators.Length(min=6, max=10)])

	startdate = DateField('Start Date', format = '%Y-%m-%d', validators = [validators.DataRequired()])

	address = StringField('Address', validators = [
		validators.DataRequired(), 
		validators.Length(min=1, max=100)])

	city = StringField('City', validators = [
		validators.DataRequired(), 
		validators.Length(min=1, max=50)])

	phone = StringField('Contact Number', [
		validators.DataRequired(), 
		validators.Length(min=1, max=12)])

	submit = SubmitField('Submit')
