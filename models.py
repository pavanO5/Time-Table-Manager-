from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Teacher(db.Model):
    __tablename__ = 'teachers'  # Add this line to match the foreign key reference
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    profile_pic = db.Column(db.String(100))
    timetable = db.Column(db.Text, nullable=True)
    processed_timetable = db.Column(db.Text, nullable=True)


class Student(db.Model):
    __tablename__ = 'students'  # Ensures table name consistency
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Correct
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    reg_number = db.Column(db.String(100), nullable=True)  # Required field as per your requirement
    program = db.Column(db.String(100), nullable=True)
    stream = db.Column(db.String(100), nullable=True)
    section = db.Column(db.String(100), nullable=True)


class ClassSchedule(db.Model):
    __tablename__ = 'class_schedule'  # Ensure table name consistency
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))  # Correct reference
    day = db.Column(db.String(20), nullable=False)
    period = db.Column(db.String(20), nullable=False)
    class_info = db.Column(db.String(100), nullable=False)
    is_free = db.Column(db.Boolean, default=False)



class MeetingRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_reg_no = db.Column(db.String(100), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)  # Correct FK reference
    requested_day = db.Column(db.String(20), nullable=False)
    requested_period = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    student_name = db.Column(db.String(100), nullable=False)
    student_reg_no = db.Column(db.String(20), nullable=False)

    # Relationship to access teacher details directly
    teacher = db.relationship('Teacher', backref='meeting_requests')


