from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SymptomForm(FlaskForm):
    response = SelectField('Response', choices=[('yes', 'Yes'), ('no', 'No')], validators=[DataRequired()])
    submit = SubmitField('Submit')

class UserInfoForm(FlaskForm):
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('m', 'Male'), ('f', 'Female')], validators=[DataRequired()])
    ethnicity = SelectField('Ethnicity', choices=[
        ('White-European', 'White-European'),
        ('Asian', 'Asian'),
        ('Middle Eastern', 'Middle Eastern'),
        ('Black', 'Black'),
        ('Hispanic', 'Hispanic'),
        ('Others', 'Others')
    ], validators=[DataRequired()])
    submit = SubmitField('Proceed')