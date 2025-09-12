from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from app import db
from app.models import User

auth = Blueprint('auth', __name__)
UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
PROFILE_PHOTO_BASE = os.path.join('app', 'static', 'images', 'profile_photos')

@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        full_name = request.form['fullname']
        username = request.form['username']
        address = request.form['address']
        role = request.form['role']
        gender = request.form['gender']
        dob_str = request.form['dob']
        qualification = request.form['qualification']
        other_qualification = request.form.get('otherQualification')
        document_type = request.form['documentType']
        other_document = request.form.get('otherDocument')
        notes = request.form.get('notes')

        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        if not password or not confirm_password or password != confirm_password:
            flash('Passwords do not match or are empty.', 'danger')
            return render_template('sign_up.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('sign_up.html')

        # Parse date of birth
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except:
            dob = None

        # Calculate age
        age = None
        try:
            age = int(request.form.get('age', '').strip())
        except:
            if dob:
                today = datetime.today().date()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        # Step 1: Create user (without setting file paths yet)
        user = User(
            username=username,
            full_name=full_name,
            address=address,
            role=role,
            gender=gender,
            dob=dob,
            age=age,
            qualification=qualification,
            other_qualification=other_qualification,
            document_type=document_type,
            other_document=other_document,
            notes=notes
        )
        user.set_password(password)

        db.session.add(user)
        db.session.flush()  # Get assigned user.id

        user_id = user.id

        # Step 2: Handle profile photo
        profile_photo = request.files.get('profile_photo')
        if profile_photo and profile_photo.filename:
            profile_photo_filename = secure_filename(profile_photo.filename)
            profile_photo_folder = os.path.join(PROFILE_PHOTO_BASE, str(user_id))
            os.makedirs(profile_photo_folder, exist_ok=True)
            profile_photo_path = os.path.join(profile_photo_folder, profile_photo_filename)
            profile_photo.save(profile_photo_path)
            # Save relative path to DB
            user.profile_image = f'profile_photos/{user_id}/{profile_photo_filename}'

        # Step 3: Handle document file
        document_file = request.files.get('documentFile')
        if document_file and document_file.filename:
            document_filename = secure_filename(document_file.filename)
            document_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
            os.makedirs(document_folder, exist_ok=True)
            document_path = os.path.join(document_folder, document_filename)
            document_file.save(document_path)
            # Save relative path to DB
            user.document_filename = f'{user_id}/{document_filename}'

        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('sign_up.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.full_name
            session['user_role'] = user.role

            flash('Logged in successfully!', 'success')

            if user.role == 'Admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard_user'))

        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
