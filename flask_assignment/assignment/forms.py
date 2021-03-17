from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from assignment.models import Employees


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name',
                             validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    phone_no = IntegerField('Phone No', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    address = TextAreaField('Address',
                            validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), Length(min=8), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_phone(self, phone_no):
        if phone_no.data != current_user.phone_no:
            user = Employees.query.filter_by(phone_no=phone_no.data)
            if user:
                raise ValidationError('That Mobile No. is already registered. Please use a different one.')

    def validate_email(self, email):
        user = Employees.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AddForm(FlaskForm):
    first_name = StringField('First Name',
                             validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    phone_no = IntegerField('Phone No', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    address = TextAreaField('Address',
                            validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=120)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), Length(min=8), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_phone(self, phone_no):
        if phone_no.data != current_user.phone_no:
            user = Employees.query.filter_by(phone_no=phone_no.data)
            if user:
                raise ValidationError('That Mobile No. is already registered. Please use a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Employees.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class UpdateAccountForm(FlaskForm):
    first_name = StringField('First Name',
                             validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    phone_no = IntegerField('Phone No', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    address = TextAreaField('Address',
                            validators=[DataRequired(), Length(max=120)])
    submit = SubmitField('Update')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired(), Length(min=8)])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    new_confirm_password = PasswordField('New Confirm Password',
                                         validators=[DataRequired(), Length(min=8), EqualTo('new_password')])
    submit = SubmitField('Update')


class SearchAccountForm(FlaskForm):
    search = StringField('Name or Address',
                         validators=[DataRequired()])
    submit = SubmitField('Search')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = Employees.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
