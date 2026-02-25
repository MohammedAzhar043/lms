

from flask import Flask, redirect, render_template, request, url_for, flash ,session,abort
from functools import wraps
from models import db, User, Course
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)

# Database configuration 
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+mysqlconnector://lms_user:password@localhost:3306/lms_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='learn-by-tech'

app.config['SESSION_COOKIE_HTTPONLY'] =  True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# Bind db to this app
db.init_app(app)


@app.route('/')
def home():
    """Home page - uses base template"""
    return render_template('home.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = (request.form.get('password') or '')

        if not username or not password:
            flash('Username and password are required','error')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password,password):
            flash('Invalid username or password ','error')
            return render_template('login.html')

        session['user_id']=user.id
        session['role']=user.role
        session['username']=user.username
        session.permanent= True

        if user.role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        return redirect(url_for('student_dashboard'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out','success')
    return redirect(url_for('home'))

def login_requierd(f):

    @wraps(f)
    def decorated_function(*args,**kwargs):

        if not session.get('user_id'):
            flash('please log in to continue','error')
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    
    return decorated_function


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('user_id'):
                flash('please log in to continue','error')
                return redirect(url_for('login'))
            if session.get('role') != role:
                abort(403)
            return f(*args,**kwargs)
        return decorated_function
    return decorator

@app.route('/student/dashboard')
@login_requierd
@role_required('student')
def student_dashboard():
    return render_template('student_dashboard.html')


@app.route('/teacher/dashboard')
@login_requierd
@role_required('teacher')
def teacher_dashboard():
    return render_template('teacher_dashboard.html')


@app.route('/users')
@login_requierd
def list_users():
    """Read: list all users """
    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/user/<int:id>')
@login_requierd
def user_detail(id):
    user = User.query.get_or_404(id)
    return render_template('user_detail.html',user=user)

@app.route('/user/edit/<int:id>',methods=['GET','POST'])
@login_requierd
def edit_user(id):

    user =User.query.get_or_404(id)
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        email = (request.form.get('email') or '').strip()
        password = (request.form.get('password') or '').strip()
        role = (request.form.get('role') or '').strip()

        # backend validation
        if not username:
            flash('Username is requierd','error')
            return render_template('user_edit.html',user=user)
        
        if not email:
            flash('Email is requierd','error')
            return render_template('user_edit.html',user=user)

        if '@' not in email:
            flash('Enter a Valid Email address','error')
            return render_template('user_edit.html',user=user)

        
        if not password:
            flash('Password is requierd','error')
            return render_template('user_edit.html',user=user)

        if len(password) < 4:
            flash('Password must be at least 4 Characters.','error')
            return render_template('user_edit.html',user=user)

        if role not in ('student','teacher'):
            flash('Please select a valid role','error')
            return render_template('user_edit.html',user=user)

        # unique username and email 
        other = User.query.filter_by(username=username).first()
        if other and other.id != user.id :
            flash('This username is already taken','error')
            return render_template('user_edit.html',user=user)
        
        other =User.query.filter_by(email=email).first()
        if other and other.id != user.id :
            flash('This email is already registered.','error')
            return render_template('user_edit.html',user=user)
        
        try: 
            user.username = username
            user.email = email
            user.password =generate_password_hash(Password)
            user.role = role
            db.session.commit()
            flash('User updated successfully','success')
            redirect(url_for('list_users'))
        except Exception:
            db.session.rollback()
            flash('Something went wrong please try agian','error')
            return render_template('user_edit.html',user=user)




    return render_template('user_edit.html',user=user)

@app.route('/user/delete/<int:id>')
@login_requierd
def delete_user(id):
    user=User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('list_users'))


@app.route('/course/create',methods=['GET','POST'])
@login_requierd
@role_required('teacher')
def course_create():

    if request.method == 'POST':
        title = (request.form.get('title') or '').strip()
        descripation = (request.form.get('description') or '').strip()
        teacher_id_raw = (request.form.get('teacher_id') or '').strip()

        # backend validation
        if not title:
            flash('Course title is required','error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_form.html',teachers=teachers,title=title,descripation=descripation)

        if not teacher_id_raw:
            flash('Please select a teacher','error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_form.html',teachers=teachers,title=title,descripation=descripation)

        try:
            teacher_id = int(teacher_id_raw)
        except ValueError:
            flash('Invalid teacher selected','error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_form.html',teachers=teachers,title=title,descripation=descripation)

        teacher = User.query.filter_by(id=teacher_id,role='teacher').first()

        if not teacher:
            flash('Invalid teacher selected','error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_form.html',teachers=teachers,title=title,descripation=descripation)
        

        try:
            course = Course(title=title, description=descripation, teacher_id=teacher_id)
            db.session.add(course)
            db.session.commit()
            flash('Course created successfully','success')
            return redirect(url_for('list_courses'))
        except Exception:
            db.session.rollback()
            flash('something went wrong, please try again','error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_form.html',teachers=teachers,title=title,descripation=descripation)

       
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('course_form.html',teachers=teachers)


@app.route('/courses')
@login_requierd
def list_courses():
    """Read: list all courses """
    courses = Course.query.all()
    return render_template('course_list.html', courses=courses)


@app.route('/course/<int:id>')
@login_requierd
def course_detail(id):
    course =Course.query.get_or_404(id)
    return render_template('course_detail.html',course=course)

@app.route('/course/edit/<int:id>', methods=['GET','POST'])
@login_requierd
@role_required('teacher')
def course_edit(id):
    course = Course.query.get_or_404(id)

    if request.method == 'POST':

        title = (request.form.get('title') or '').strip()
        description = (request.form.get('description') or '').strip()
        teacher_id_raw = (request.form.get('teacher_id') or '').strip()

        # backend validation
        if not title:
            flash('Course title is required','error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_edit.html', teachers=teachers, course=course)

        if not teacher_id_raw:
            flash('Please select a teacher','error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_edit.html', teachers=teachers, course=course)

        try:
            teacher_id = int(teacher_id_raw)
        except ValueError:
            flash('Invalid teacher selected','error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_edit.html', teachers=teachers, course=course)

        teacher = User.query.filter_by(id=teacher_id, role='teacher').first()

        if not teacher:
            flash('Invalid teacher selected','error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_edit.html', teachers=teachers, course=course)

        try:
            # Update
            course.title = title
            course.description = description
            course.teacher_id = teacher_id

            db.session.commit()
            flash('Course updated successfully.','success')
            return redirect(url_for('list_courses'))

        except Exception:
            db.session.rollback()
            flash('something went wrong, please try again','error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_edit.html', teachers=teachers, course=course)

    # GET request
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('course_edit.html', course=course, teachers=teachers)


@app.route('/course/delete/<int:id>')
@login_requierd
@role_required('teacher')
def course_delete(id):

    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('list_courses'))



@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        email = (request.form.get('email') or '').strip()
        password = (request.form.get('password') or '')
        role = (request.form.get('role') or '').strip()

        # backend validation 

        if not username:
            flash('Username is requierd','error')
            return render_template('register.html',error='Username is requierd')
        if not email:
            flash('Email is requierd','error')
            return render_template('register.html',error='Email is requierd',username=username)
        
        if '@' not in email:
            flash('Enter a valid email','error')
            return render_template('register.html',error='provide a proper email',username=username)

        if not password:
            flash('Password is requierd','error')
            return render_template('register.html',error='password is requierd',username=username,email=email,role=role)

        if len(password) < 4:
            flash('Password must be atleast 4 characters','error')
            return render_template('register.html',error='Password must be atleast 4 characters',username=username,email=email, role=role)

        if role not in ('student','teacher'):
            flash('Please select a valid role','error')
            return render_template('register.html',error='Please select a valid role',username=username,email=email,role=role)


        #unique user name and email
        if User.query.filter_by(username=username).first():
            flash('This username is already taken','error')
            return render_template('register.html',error='username already taken',username=username,email=email,role=role)


        if User.query.filter_by(email=email).first():
            flash('This email is already taken','error')
            return render_template('register.html',error='email already taken',username=username,email=email,role=role)

        try:
            hashed_password = generate_password_hash(password)
            user = User(username=username,email=email,password=hashed_password,role=role)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful','success')
            return redirect(url_for('list_users'))
        except Exception:
            db.session.rollback()
            flash('Something went wrong.please try agian','error')
            return render_template('register.html',username=username,email=email,role=role)


    return render_template('register.html')


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'),403

# Create all tables when app runs (first time)
with app.app_context():
    db.create_all()
    print('Database tables created (user, course).')



if __name__ == '__main__':
    app.run(debug=True)




























