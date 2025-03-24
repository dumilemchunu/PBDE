from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import Enum
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user

app = Flask(__name__)

# Secret Key for Flash Messages
app.secret_key = "your_secret_key"

# Database Configuration for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///peer_tutoring.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'sign_in'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------------
# Database Models
# -------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(Enum('student', 'tutor', 'admin', name="user_role"), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    def get_id(self):
        return str(self.user_id)

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    course = db.Column(db.String(255), nullable=False)
    year_of_study = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

class Tutor(db.Model):
    __tablename__ = 'tutors'
    tutor_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    course = db.Column(db.String(255), nullable=False)
    tutor_transcript = db.Column(db.LargeBinary, nullable=True)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

class Admin(db.Model):
    __tablename__ = 'admins'
    admin_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

class ICTCourses(db.Model):
    __tablename__ = 'All_ict_courses'
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(255), nullable=False)
    course_code = db.Column(db.String(50), unique=True, nullable=False)
    course_year = db.Column(db.Integer, nullable=False)

# Initialize database and add courses
with app.app_context():
    db.create_all()
    
    # Add AppDev Diploma in ICT Courses
All_courses = [
    {"name": "Applications Development Project 1", "code": "APDP101", "year": 1},
    {"name": "ICT Literacy & Skills", "code": "ICTL101", "year": 1},
    {"name": "Business Fundamentals 1", "code": "BFND101", "year": 1},
    {"name": "Fundamentals of Computer Literacy", "code": "FCSC101", "year": 1},
    {"name": "Applications Development 1A", "code": "APDA101", "year": 1},
    {"name": "Operating Systems", "code": "OSYS101", "year": 1},
    {"name": "Information Systems", "code": "IMSS101", "year": 1},
    {"name": "My World My Universe", "code": "MWMU101", "year": 1},
    {"name": "Cornerstone 101", "code": "CSTN101", "year": 1},
    {"name": "Applications Development 1B", "code": "APDB101", "year": 1},
    {"name": "Communications Networks 1", "code": "CNTW101", "year": 1},
    {"name": "Applications Development Project 2", "code": "APDP201", "year": 2},
    {"name": "Mobile Computing 2A", "code": "MCPA201", "year": 2},
    {"name": "Business Fundamentals 2", "code": "BFND201", "year": 2},
    {"name": "IT Project Management", "code": "ITPM101", "year": 2},
    {"name": "Information Management 2A", "code": "INMA201", "year": 2},
    {"name": "Applications Development 2A", "code": "APDA201", "year": 2},
    {"name": "Mobile Computing 2B", "code": "MCPB201", "year": 2},
    {"name": "Information Systems 2A", "code": "ISYA201", "year": 2},
    {"name": "Information Systems 2B", "code": "ISYB201", "year": 2},
    {"name": "Information Management 2AB", "code": "INMB201", "year": 2},
    {"name": "Applications Development 2B", "code": "APDB201", "year": 2},
    {"name": "Applications Development 3A ", "code": "APDA301", "year": 3},
    {"name": "Information Systems 3A", "code": "ISYA301", "year": 3},
    {"name": "Applications Development Project 3A", "code": "ADPA301", "year": 3},
    {"name": "Human Computer Interaction", "code": "HCIN101", "year": 3},
    {"name": "Theory of ICT Professional Practice 3", "code": "TIPP301", "year": 3},
    {"name": "Entrepreneurial Spirit", "code": "ENSP1", "year": 3},
    {"name": "Applications Development 3B", "code": "APDB301", "year": 3},
    {"name": "Information Systems 3B", "code": "ISYB301", "year": 3},
    {"name": "Applications Development Project 3B", "code": "ADPB301", "year": 3},
]


for course in All_courses:
        existing_course = ICTCourses.query.filter_by(course_code=course["code"]).first()
        if not existing_course:
            new_course = ICTCourses(course_name=course["name"], course_code=course["code"], course_year=course["year"])
            db.session.add(new_course)
db.session.commit()

bachelors_courses = [
    {"name": "Introduction to Computing", "code": "INCP101", "year": 1},
    {"name": "Discrete Structures", "code": "DSTR101", "year": 1},
    {"name": "Interpersonal Communication & Self", "code": "ICMS101", "year": 1},
    {"name": "Mathematics for Computing 1A", "code": "MCMA101", "year": 1},
    {"name": "Conerstone 101", "code": "CSTN101", "year": 1},
    {"name": "Business Fundamentals 2", "code": "BFND201", "year": 1},
    {"name": "Software Development Fundamentals", "code": "SWDF101", "year": 1},
    {"name": "Mathematics for Computing 1B", "code": "MCMB101", "year": 1},
    {"name": "Systems Fundamentals", "code": "SYSF101", "year": 1},
    {"name": "Systems Analysis and Design", "code": "SADS201", "year": 2},
    {"name": "Law of Life", "code": "LWLF101", "year": 2},
    {"name": "Organizational Behavior", "code": "OGBH201", "year": 2},
    {"name": "Networks and Operating Systems 2", "code": "NOPS201", "year": 2},
    {"name": "Programming Languages 2", "code": "PRLN201", "year": 2},
    {"name": "Algorithms and Data Structures 2", "code": "ALDS201", "year": 2},
    {"name": "Information Management 2", "code": "INFM201", "year": 2},
    {"name": "Information Assurance and Security", "code": "INAS201", "year": 2},
    {"name": "Computer Organization and Architecture 2", "code": "COAR201", "year": 2},
    {"name": "Entrepreneurial Spirit", "code": "ENSP101", "year": 2},
    {"name": "Industry Exposure", "code": "IEXP101", "year": 3},
    {"name": "Platform Based Development 3", "code": "PBDV301", "year": 3},
    {"name": "Integrative Programming & Technology 3", "code": "IPRT301", "year": 3},
    {"name": "Social and Professional Issues 3 ", "code": "SPRI301", "year": 3},
    {"name": "Research Skills", "code": "RESK301", "year": 3},
    {"name": "Project 3", "code": "PRJT302", "year": 3},
    {"name": "Strategy Acquisition and Management", "code": "SAQM301", "year": 3},
    {"name": "Software Engineering 3", "code": "SFEN301", "year": 3},
    {"name": "Project Management 3", "code": "PJMN301", "year": 3},
    {"name": "Business Intelligence 3", "code": "BSIT301", "year": 3},
    {"name": "Parallel and Distributed Computing 3", "code": "PDCP301", "year": 3},
    {"name": "Machine Intelligence 3", "code": "MCHI301", "year": 3}
]


for course in bachelors_courses:
        existing_course = ICTCourses.query.filter_by(course_code=course["code"]).first()
        if not existing_course:
            new_course = ICTCourses(course_name=course["name"], course_code=course["code"], course_year=course["year"])
            db.session.add(new_course)
db.session.commit()

advanced_diploma_courses = [
    {"name": "Data Structures", "code": "DAST401", "year": 1},
    {"name": "Platform Based Development", "code": "PBDE401", "year": 1},
    {"name": "Research Skills", "code": "RESK401", "year": 1},
    {"name": "Applied Mathematics for Computing A", "code": "APMC401", "year": 1},
    {"name": "Software Development and Management", "code": "SODM401", "year": 1},
    {"name": "Applied Mathematics for Computing B", "code": "APMC402", "year": 1},
    {"name": "Strategy Acquisition and Management 3", "code": "SAMA301", "year": 1},
    {"name": "Business Intelligence 3", "code": "BUIN301", "year": 1},
    {"name": "Parallel and Distributed Computing 3", "code": "PDCO301", "year": 1},
    {"name": "Machine Intelligence 3", "code": "MAIN301", "year": 1},
    {"name": "Graphics 3", "code": "GRAPH301", "year": 1},
    {"name": "Human Computer Interaction 3", "code": "HCIN301", "year": 1},
]
    
for course in App_dev_diploma_courses:
        existing_course = ICTCourses.query.filter_by(course_code=course["code"]).first()
        if not existing_course:
            new_course = ICTCourses(course_name=course["name"], course_code=course["code"], course_year=course["year"])
            db.session.add(new_course)
    

db.session.commit()


#Routes Section

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/sign-in", methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful!", "success")

            if user.role == 'student':
                return redirect(url_for('student_home'))
            elif user.role == 'tutor':
                return redirect(url_for('tutor_home'))
            elif user.role == 'admin':
                return redirect(url_for('admin_home'))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("sign-in.html")



@app.route("/student_home")
@login_required
def student_home():
    student = Student.query.filter_by(email=current_user.email).first()
    
    if not student:
        flash("Student record not found", "danger")
        return redirect(url_for('sign_in'))
    
    semester1_modules = ICTCourses.query.filter_by(
        course_year=student.year_of_study
    ).filter(
        ICTCourses.course_code.like('%A')
    ).all()
    
    semester2_modules = ICTCourses.query.filter_by(
        course_year=student.year_of_study
    ).filter(
        ICTCourses.course_code.like('%B')
    ).all()
    
    return render_template(
        "student_home.html",
        current_user=student,
        role='student',
        semester1_modules=semester1_modules,
        semester2_modules=semester2_modules
    )

@app.route("/tutor_home")
@login_required
def tutor_home():
    tutor = Tutor.query.filter_by(email=current_user.email).first()
    
    if not tutor:
        flash("Tutor record not found", "danger")
        return redirect(url_for('sign_in'))
    
    semester1_modules = ICTCourses.query.filter_by(
        course_year=tutor.year_of_study
    ).filter(
        ICTCourses.course_code.like('%A')
    ).all()
    
    semester2_modules = ICTCourses.query.filter_by(
        course_year=tutor.year_of_study
    ).filter(
        ICTCourses.course_code.like('%B')
    ).all()
    
    return render_template(
        "tutor_home.html",
        current_user=tutor,
        role='tutor',
        semester1_modules=semester1_modules,
        semester2_modules=semester2_modules
    )

@app.route("/admin_home")
@login_required
def admin_home():
    return render_template("admin_home.html")

if __name__ == '__main__':
    app.run(debug=True)