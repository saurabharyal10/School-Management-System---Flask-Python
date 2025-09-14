from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app import db
from app.models import User
from app.models import ContactMessage
import os
from flask import current_app

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.before_request
def restrict_to_admins():
    if session.get('user_role') != 'Admin':
        flash('Access denied. Admins only.', 'warning')
        return redirect(url_for('auth.login'))

@admin.route('/dashboard')
def dashboard():
    user = User.query.get(session['user_id'])  # Optional: to display user's name
    return render_template('admin/dashboard.html', user=user)

@admin.route('/list/<role>')
def list_users(role):
    if role not in ['student', 'teacher']:
        flash('Invalid user type.', 'danger')
        return redirect(url_for('admin.dashboard'))

    users = User.query.filter_by(role=role.capitalize()).all()
    return render_template('admin/list_users.html', users=users, role=role)


@admin.route('/admin_profile')
def admin_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view your profile.', 'warning')
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))

    # Get stored relative image path
    relative_path = user.profile_image or 'profile_photos/default.png'
    full_path = os.path.join(current_app.static_folder, 'images', relative_path)

    # Fallback if file doesn't exist
    if not os.path.isfile(full_path):
        relative_path = 'profile_photos/default.png'

    return render_template('admin/admin_profile.html', user=user, profile_image=relative_path)

# @admin.route('/view_user/<int:user_id>')
# def view_user(user_id):
#     flash(f"View User {user_id} - not implemented yet.", 'info')
#     return redirect(url_for('admin.dashboard'))

# @admin.route('/edit_user/<int:user_id>')
# def edit_user(user_id):
#     flash(f"Edit User {user_id} - not implemented yet.", 'info')
#     return redirect(url_for('admin.dashboard'))

# @admin.route('/delete_user/<int:user_id>')
# def delete_user(user_id):
#     flash(f"Delete User {user_id} - not implemented yet.", 'info')
#     return redirect(url_for('admin.dashboard'))

from flask import request

@admin.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.address = request.form.get('address')
        user.role = request.form.get('role')
        user.gender = request.form.get('gender')
        user.qualification = request.form.get('qualification')
        user.other_qualification = request.form.get('other_qualification')
        user.notes = request.form.get('notes')

        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.list_users', role=user.role.lower()))

    return render_template('admin/edit_user.html', user=user)

@admin.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    role = user.role.lower()
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.list_users', role=role))

@admin.route('/delete_all_users', methods=['POST'])
def delete_all_users():
    if session.get('user_role') != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))

    current_user_id = session.get('user_id')
    
    # Delete all users except the current admin
    User.query.filter(User.id != current_user_id).delete()
    db.session.commit()

    flash('All users deleted successfully (except the current admin).', 'success')
    return redirect(url_for('admin.list_users', role='student'))


@admin.route('/contact_us_details')
def view_messages():    
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/contact_us_details.html', messages=messages)

@admin.route('/delete_message/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Message deleted successfully.', 'success')
    return redirect(url_for('admin.view_messages'))


