from flask import render_template, session, redirect, url_for, flash
from app.models import User
from . import user

@user.route('/dashboard_user')
def dashboard_user():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    user_data = User.query.get(user_id)
    return render_template('user/dashboard_user.html', user=user_data)
