from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models import User, db


def register_routes(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = (request.form.get('username') or '').strip()
            password = (request.form.get('password') or '')

            if not username or not password:
                flash('Username and password are required', 'error')
                return render_template('login.html')

            user = User.query.filter_by(username=username).first()
            if not user or not check_password_hash(user.password, password):
                flash('Invalid username or password ', 'error')
                return render_template('login.html')

            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username
            session.permanent = True

            if user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            return redirect(url_for('student_dashboard'))

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out', 'success')
        return redirect(url_for('home'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = (request.form.get('username') or '').strip()
            email = (request.form.get('email') or '').strip()
            password = (request.form.get('password') or '')
            role = (request.form.get('role') or '').strip()

            # backend validation

            if not username:
                flash('Username is requierd', 'error')
                return render_template('register.html', error='Username is requierd')
            if not email:
                flash('Email is requierd', 'error')
                return render_template('register.html', error='Email is requierd', username=username)

            if '@' not in email:
                flash('Enter a valid email', 'error')
                return render_template('register.html', error='provide a proper email', username=username)

            if not password:
                flash('Password is requierd', 'error')
                return render_template('register.html', error='password is requierd', username=username, email=email, role=role)

            if len(password) < 4:
                flash('Password must be atleast 4 characters', 'error')
                return render_template('register.html', error='Password must be atleast 4 characters', username=username, email=email, role=role)

            if role not in ('student', 'teacher'):
                flash('Please select a valid role', 'error')
                return render_template('register.html', error='Please select a valid role', username=username, email=email, role=role)

            # unique user name and email
            if User.query.filter_by(username=username).first():
                flash('This username is already taken', 'error')
                return render_template('register.html', error='username already taken', username=username, email=email, role=role)

            if User.query.filter_by(email=email).first():
                flash('This email is already taken', 'error')
                return render_template('register.html', error='email already taken', username=username, email=email, role=role)

            try:
                hashed_password = generate_password_hash(password)
                user = User(username=username, email=email, password=hashed_password, role=role)
                db.session.add(user)
                db.session.commit()
                flash('Registration successful', 'success')
                return redirect(url_for('list_users'))
            except Exception:
                db.session.rollback()
                flash('Something went wrong.please try agian', 'error')
                return render_template('register.html', username=username, email=email, role=role)

        return render_template('register.html')
