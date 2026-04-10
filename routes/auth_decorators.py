from functools import wraps

from flask import abort, flash, jsonify, redirect, request, session, url_for


def api_login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'status': 'error', 'message': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def api_role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('user_id'):
                return jsonify({'status': 'error', 'message': 'Login required'}), 401
            if session.get('role') != role:
                return jsonify({'status': 'error', 'message': 'Access denied'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def login_requierd(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not session.get('user_id'):
            flash('please log in to continue', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('user_id'):
                flash('please log in to continue', 'error')
                return redirect(url_for('login'))
            if session.get('role') != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def _get_api_data():

    # 1.json body

    data = request.get_json(force=True, silent=True)

    if data and isinstance(data, dict):
        return data

    # 2. try form data

    if request.form:

        return {
            k: (v[0] if isinstance(v, list) else v)
            for k, v in request.form.items()
        }

    # 3.try as raw body as json

    if request.get_data():

        import json

        try:
            return json.loads(request.get_data(as_text=True))
        except Exception:
            pass

    # 4 .query string
    if request.args:
        return dict(request.args)

    return {}
