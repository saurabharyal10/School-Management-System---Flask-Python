from flask import render_template, session, g, Blueprint, request, flash, redirect, url_for
from app.models import User
from . import main  # import blueprint instance from __init__.py
from app.models import ContactMessage

from app import db

@main.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = User.query.get(user_id) if user_id else None

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/about_us')
def about_us():
    return render_template('about_us.html')

@main.route('/our_moments')
def our_moments():
    return render_template('our_moments.html')

@main.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        message = request.form.get('message')

        if not name or not email or not message:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('main.contact_us'))

        new_message = ContactMessage(
            name=name,
            email=email,
            phone_number=phone_number,
            message=message
        )

        db.session.add(new_message)
        db.session.commit()

        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('main.contact_us'))

    return render_template('contact_us.html')
