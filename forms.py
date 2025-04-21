from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from wtforms import FileField
from wtforms import SelectField
from wtforms.validators import DataRequired
from wtforms.validators import EqualTo

class TeacherSignupForm(FlaskForm):
    user_id = StringField('User ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class StudentSignupForm(FlaskForm):
    user_id = StringField('User ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    user_id = StringField('User ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TeacherProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    profile_pic = FileField('Profile Picture')
    timetable_file = FileField('Upload Time Table (Excel File)', validators=[DataRequired()])
    submit = SubmitField('Submit')

class StudentProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    reg_number = StringField('Registration Number', validators=[DataRequired()])
    program = StringField('Program', validators=[DataRequired()])
    stream = StringField('Stream', validators=[DataRequired()])
    section = StringField('Section', validators=[DataRequired()])
    submit = SubmitField('Submit')

class MeetingRequestForm(FlaskForm):
    student_name = StringField('Your Name', validators=[DataRequired()])
    student_reg_no = StringField('Registration Number', validators=[DataRequired()])
    teacher_id = SelectField('Select Teacher', coerce=int)
    requested_day = SelectField('Select Day', choices=[
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday')
    ])
    requested_period = StringField('Enter Period (e.g., "Period 2")', validators=[DataRequired()])
    submit = SubmitField('Request Meeting')

class CheckScheduleForm(FlaskForm):
    teacher_id = SelectField('Choose a Teacher', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Check Free Periods')

class SelectTeacherForm(FlaskForm):
    teacher_id = SelectField('Select Teacher', choices=[], coerce=int)
    submit = SubmitField('View Free Periods')
