from flask import flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from models import User, db
from routes.auth_decorators import login_requierd


def register_routes(app):
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
        return render_template('user_detail.html', user=user)

    @app.route('/user/edit/<int:id>', methods=['GET', 'POST'])
    @login_requierd
    def edit_user(id):

        user = User.query.get_or_404(id)
        if request.method == 'POST':
            username = (request.form.get('username') or '').strip()
            email = (request.form.get('email') or '').strip()
            password = (request.form.get('password') or '').strip()
            role = (request.form.get('role') or '').strip()

            # backend validation
            if not username:
                flash('Username is requierd', 'error')
                return render_template('user_edit.html', user=user)

            if not email:
                flash('Email is requierd', 'error')
                return render_template('user_edit.html', user=user)

            if '@' not in email:
                flash('Enter a Valid Email address', 'error')
                return render_template('user_edit.html', user=user)

            if not password:
                flash('Password is requierd', 'error')
                return render_template('user_edit.html', user=user)

            if len(password) < 4:
                flash('Password must be at least 4 Characters.', 'error')
                return render_template('user_edit.html', user=user)

            if role not in ('student', 'teacher'):
                flash('Please select a valid role', 'error')
                return render_template('user_edit.html', user=user)

            # unique username and email
            other = User.query.filter_by(username=username).first()
            if other and other.id != user.id:
                flash('This username is already taken', 'error')
                return render_template('user_edit.html', user=user)

            other = User.query.filter_by(email=email).first()
            if other and other.id != user.id:
                flash('This email is already registered.', 'error')
                return render_template('user_edit.html', user=user)

            try:
                user.username = username
                user.email = email
                user.password = generate_password_hash(password)
                user.role = role
                db.session.commit()
                flash('User updated successfully', 'success')
                return redirect(url_for('list_users'))
            except Exception:
                db.session.rollback()
                flash('Something went wrong please try agian', 'error')
                return render_template('user_edit.html', user=user)

        return render_template('user_edit.html', user=user)

    @app.route('/user/delete/<int:id>')
    @login_requierd
    def delete_user(id):
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('list_users'))
