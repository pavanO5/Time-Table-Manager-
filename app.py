from flask import Flask, render_template, redirect, url_for, flash, request
from models import db, Teacher, Student, MeetingRequest, ClassSchedule
from forms import TeacherProfileForm, StudentProfileForm, CheckScheduleForm, SelectTeacherForm
from config import Config
import pandas as pd
from flask import request
import json
from forms import MeetingRequestForm  # Correct import statement
from forms import LoginForm
from flask import session
from forms import TeacherSignupForm, StudentSignupForm
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
import os
from werkzeug.utils import secure_filename






app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize database
db.init_app(app)


def process_excel_file(file_path):
    try:
        df = pd.read_excel(file_path)

        processed_data = {}
        for index, row in df.iterrows():
            day = row['Day']
            free_periods = []
            occupied_periods = []

            for col in df.columns:
                if col != 'Day':
                    if str(row[col]).strip().lower() == 'free':
                        free_periods.append(col)
                    else:
                        occupied_periods.append(col)

            processed_data[day] = {
                "Free Periods": free_periods,
                "Occupied Periods": occupied_periods
            }

        print("Processed Data to be Stored:", processed_data)  # Debugging output
        return json.dumps(processed_data)  # Store as JSON string in the database

    except Exception as e:
        print(f"Error processing file: {e}")
        return None






@app.route('/')
def home():
    return render_template('home.html')

@app.route('/teacher_signup', methods=['GET', 'POST'])
def teacher_signup():
    form = TeacherSignupForm()

    if request.method == 'POST':
        print("POST request received")  # ✅ Check if the POST request is happening

    if form.validate_on_submit():
        print("Form submitted successfully")  # ✅ Form validation success check

        # Check if the user ID already exists
        existing_teacher = Teacher.query.filter_by(user_id=form.user_id.data).first()
        if existing_teacher:
            flash('User ID already exists. Please choose a different one.', 'error')
        else:
            new_teacher = Teacher(
                user_id=form.user_id.data,
                password=form.password.data,  # Ideally, hash the password for security
                name=form.name.data
            )

            try:
                db.session.add(new_teacher)
                db.session.commit()
                print(f"New teacher added: {new_teacher.user_id}")  # ✅ Confirm data is stored
            except Exception as e:
                print(f"Database error: {e}")  # ❗️ Catch database errors

            flash('Signup successful! Please log in.', 'success')
            print("Redirecting to teacher_login page...")  # ✅ Confirm redirect
            return redirect(url_for('teacher_login'))
    else:
        print("Form validation failed")  # ❗️ Validation failed
        print(form.errors)  # ❗️ Display errors for diagnosis

    return render_template('teacher_signup.html', form=form)


@app.route('/student_signup', methods=['GET', 'POST'])
def student_signup():
    form = StudentSignupForm()
    if form.validate_on_submit():
        # Check if the user ID already exists
        existing_student = Student.query.filter_by(user_id=form.user_id.data).first()
        if existing_student:
            flash('User ID already exists. Please choose a different one.', 'error')
        else:
            new_student = Student(
                user_id=form.user_id.data,
                password=form.password.data,  # Ideally, hash the password for security
                name=form.name.data
            )
            db.session.add(new_student)
            db.session.commit()
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('student_login'))
    return render_template('student_signup.html', form=form)

@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    form = LoginForm()
    if form.validate_on_submit():
        teacher = Teacher.query.filter_by(user_id=form.user_id.data).first()
        if teacher and teacher.password == form.password.data:
            session['teacher_id'] = teacher.id  # Store teacher ID in session
            session['user_type'] = 'teacher' 
            flash('Login successful!', 'success')
            return redirect(url_for('teacher_dashboard'))  # Redirect to teacher dashboard
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('teacher_login.html', form=form)

@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    form = LoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(user_id=form.user_id.data).first()
        if student and student.password == form.password.data:
            session['student_id'] = student.id  # Store student ID in session
            session['user_type'] = 'student' 
            flash('Login successful!', 'success')
            return redirect(url_for('student_dashboard'))  # Redirect to student dashboard
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('student_login.html', form=form)

@app.route('/teacher_profile', methods=['GET', 'POST'])
def teacher_profile():
    print("Session Data:", session)

    if 'user_type' not in session or session['user_type'] != 'teacher':
        flash('Please log in as a teacher to access this page.', 'warning')
        return redirect(url_for('teacher_login'))

    teacher = Teacher.query.filter_by(id=session.get('teacher_id')).first()

    if not teacher:
        flash('Teacher profile not found.', 'danger')
        return redirect(url_for('teacher_login'))

    form = TeacherProfileForm()

    if form.validate_on_submit():
        # Handle Profile Picture Upload
        profile_pic = request.files.get('profile_pic')
        if profile_pic and profile_pic.filename != '':
            filename = secure_filename(profile_pic.filename)
            file_path = os.path.join('static/uploads/profile_pics', filename)
            
            # Create folder if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            profile_pic.save(file_path)
            teacher.profile_pic = file_path  # Save full path in database

        # Handle Timetable File Upload
        timetable_file = request.files.get('timetable_file')
        if timetable_file:
            print("Uploaded File Detected:", timetable_file.filename)
            processed_data = process_excel_file(timetable_file)

            if processed_data:
                print("Processed Data to be Stored:", processed_data)
                teacher.name = form.name.data
                teacher.processed_data = processed_data
                teacher.timetable = json.dumps(json.loads(processed_data))

                db.session.commit()

                flash('Profile updated successfully with timetable analysis from Excel file!', 'success')
                return redirect(url_for('teacher_dashboard'))
            else:
                flash('Error processing the timetable file. Please check the file format.', 'danger')
                print("Error: Processed data is None.")

    return render_template('teacher_profile.html', form=form, teacher=teacher)




@app.route('/student_profile', methods=['GET', 'POST'])
def student_profile():
    if 'user_type' not in session or session['user_type'] != 'student':
        flash('Please log in as a student to access this page.', 'warning')
        return redirect(url_for('student_login'))
    
    student = Student.query.filter_by(id=session.get('student_id')).first()

    if not student:
        flash('Student profile not found.', 'danger')
        return redirect(url_for('student_login'))

    form = StudentProfileForm()

    if form.validate_on_submit():
        student = Student.query.filter_by(id=session.get('student_id')).first()
        if student:
            student.name = form.name.data
            student.reg_number = form.reg_number.data
            student.program = form.program.data
            student.stream = form.stream.data
            student.section = form.section.data
        else:
            student = Student(
                user_id=session['user_id'],
                name=form.name.data,
                reg_number=form.reg_number.data,
                program=form.program.data,
                stream=form.stream.data,
                section=form.section.data
            )
            db.session.add(student)

        db.session.commit()
        flash('Profile created successfully!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('student_profile.html', form=form)
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'teacher_id' not in session:
        flash('Please log in to access your dashboard.', 'warning')
        return redirect(url_for('teacher_login'))

    teacher = Teacher.query.get(session['teacher_id'])
    if not teacher:
        flash('Teacher profile not found.', 'danger')
        return redirect(url_for('teacher_login'))

    # Ensure profile picture path is correctly formatted
    profile_pic_path = None
    if teacher.profile_pic:
        profile_pic_path = url_for('static', filename=teacher.profile_pic.replace('uploads/', ''))

    # Load teacher's timetable
    timetable = teacher.timetable
    if isinstance(timetable, str):
        try:
            timetable = json.loads(timetable)
        except (json.JSONDecodeError, TypeError):
            flash("Invalid timetable format.", "danger")
            timetable = {}

    # Prepare schedule display
    class_schedule = []
    if isinstance(timetable, dict):
        for day, periods in timetable.items():
            if isinstance(periods, list):
                for period in periods:
                    class_schedule.append({
                        'day': day,
                        'period': period,
                        'class_info': 'Scheduled Class'  # Add more details if available
                    })
            elif isinstance(periods, dict):
                for period, status in periods.items():
                    class_schedule.append({
                        'day': day,
                        'period': period,
                        'class_info': status
                    })

    # Retrieve meeting requests for the teacher
    meetings = MeetingRequest.query.filter_by(teacher_id=teacher.id).all()

    return render_template(
        'teacher_dashboard.html',
        teacher=teacher,
        profile_pic_path=profile_pic_path,
        class_schedule=class_schedule,
        meetings=meetings
    )

@app.route('/student_dashboard', methods=['GET', 'POST'])
def student_dashboard():
    if 'student_id' not in session:
        flash('Please log in to access your dashboard.', 'warning')
        return redirect(url_for('student_login'))

    student = Student.query.get(session['student_id'])
    if not student:
        flash('Student profile not found.', 'danger')
        return redirect(url_for('student_login'))

    teachers = Teacher.query.all()

    # Create one form for both functionalities
    meeting_request_form = MeetingRequestForm()

    # Populate teacher_id field dynamically
    meeting_request_form.teacher_id.choices = [(teacher.id, teacher.name) for teacher in teachers] if teachers else []

    if not teachers:
        flash('No teachers available. Please try again later.', 'info')

    # Fetch student's meeting requests
    meeting_requests = db.session.query(MeetingRequest, Teacher.name).join(Teacher).filter(MeetingRequest.student_reg_no == student.reg_number).all()

    if not meeting_requests:
        flash('You have no meeting requests yet.', 'info')

    # Free Periods Logic - Handle initial load too
    free_periods = {}
    selected_teacher_id = request.form.get('teacher_id') or meeting_request_form.teacher_id.data

    if selected_teacher_id:
        selected_teacher = Teacher.query.get(selected_teacher_id)
        if selected_teacher and selected_teacher.timetable:
            timetable_data = json.loads(selected_teacher.timetable)
            for day, periods in timetable_data.items():
                free_periods[day] = periods.get("Free Periods", [])

    return render_template(
        'student_dashboard.html',
        student=student,
        teachers=teachers,
        meeting_request_form=meeting_request_form,
        meeting_requests=meeting_requests,
        free_periods=free_periods
    )




@app.route('/check_teacher_schedule', methods=['POST'])
def check_teacher_schedule():
    form = MeetingRequestForm()

    # Dynamically populate teacher choices for validation
    teachers = Teacher.query.all()
    form.teacher_id.choices = [(teacher.id, teacher.name) for teacher in teachers]

    # Debugging: Ensure form data reaches this route
    print("Form Data Received:", request.form)

    if form.validate_on_submit():
        teacher_id = form.teacher_id.data
        teacher = Teacher.query.get(teacher_id)

        if not teacher:
            flash("Teacher not found.", "danger")
            return redirect(url_for('student_dashboard'))

        # Ensure timetable is converted to JSON if stored as a string
        timetable = teacher.timetable
        if isinstance(timetable, str):
            try:
                timetable = json.loads(timetable)
            except (json.JSONDecodeError, TypeError):
                flash("Invalid timetable format.", "danger")
                return redirect(url_for('student_dashboard'))

        # Identify free periods
        free_periods = {}
        if isinstance(timetable, dict):  
            for day, periods in timetable.items():
                if isinstance(periods, list):
                    # Handle structure like: {"Monday": ["Period 2", "Period 4"]}
                    free_periods[day] = periods
                elif isinstance(periods, dict):
                    # Handle structure like: {"Monday": {"Period 1": "Free", "Period 2": "Busy"}}
                    free_periods[day] = [
                        period for period, status in periods.items() if status == "Free"
                    ]

        # Debugging: Print identified free periods
        print("Free Periods Identified:", free_periods)

        if not free_periods or all(not periods for periods in free_periods.values()):
            flash("No free periods found for this teacher.", "info")
            return redirect(url_for('student_dashboard'))

        return render_template(
            'free_periods.html',
            free_periods=free_periods,
            teacher=teacher
        )

    # Form submission failure
    flash("Form submission failed. Please try again.", "danger")
    return redirect(url_for('student_dashboard'))


@app.route('/request_meeting', methods=['POST'])
def request_meeting():
    # Check if the student is logged in
    if 'student_id' not in session:
        flash('Please log in to request a meeting.', 'warning')
        return redirect(url_for('student_login'))

    student = Student.query.get(session['student_id'])
    if not student:
        flash('Student profile not found.', 'danger')
        return redirect(url_for('student_login'))

    # Get the form data
    teacher_id = request.form['teacher_id']
    requested_day = request.form['requested_day']
    requested_period = request.form['requested_period']

    # Check if the selected teacher exists
    selected_teacher = Teacher.query.get(teacher_id)
    if not selected_teacher:
        flash('Teacher not found.', 'danger')
        return redirect(url_for('student_dashboard'))

    # Create a new MeetingRequest
    new_request = MeetingRequest(
        student_reg_no=student.reg_number,
        student_name=student.name,
        teacher_id=teacher_id,
        requested_day=requested_day,
        requested_period=requested_period,
        status='Pending'  # Default status
    )

    # Save the request to the database
    db.session.add(new_request)
    db.session.commit()

    flash('Your meeting request has been submitted successfully!', 'success')
    return redirect(url_for('student_dashboard'))


@app.route('/manage_meetings/<int:teacher_id>')
def manage_meetings(teacher_id):
    meeting_requests = (
        db.session.query(
            MeetingRequest.id,
            MeetingRequest.requested_day,
            MeetingRequest.requested_period,
            MeetingRequest.status,
            MeetingRequest.student_name.label('student_name'),  # Directly fetched from MeetingRequest
            MeetingRequest.student_reg_no.label('student_reg_no')  # Directly fetched from MeetingRequest
        )
        .filter(MeetingRequest.teacher_id == teacher_id)
        .all()
    )

    return render_template('manage_meetings.html', requests=meeting_requests)



@app.route('/accept_meeting/<int:meeting_id>')
def accept_meeting(meeting_id):
    meeting = MeetingRequest.query.get_or_404(meeting_id)
    meeting.status = 'Accepted'
    try:
        db.session.commit()
        flash('Meeting request accepted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error accepting meeting request: {str(e)}', 'danger')

    return redirect(url_for('manage_meetings', teacher_id=meeting.teacher_id))

@app.route('/reject_meeting/<int:meeting_id>')
def reject_meeting(meeting_id):
    meeting = MeetingRequest.query.get_or_404(meeting_id)
    meeting.status = 'Rejected'
    try:
        db.session.commit()
        flash('Meeting request rejected.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error rejecting meeting request: {str(e)}', 'danger')

    return redirect(url_for('manage_meetings', teacher_id=meeting.teacher_id))




if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
