from flask import render_template


def register_routes(app):
    @app.route('/')
    def home():
        """Home page - uses base template"""
        return render_template('home.html')
