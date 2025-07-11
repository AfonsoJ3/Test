from flask import Blueprint as bl, render_template, request, flash, redirect, url_for, session
from .models import User, db
from datetime import datetime
import re

auth = bl('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(input_string):
    """Basic input sanitization"""
    if not input_string:
        return ""
    return input_string.strip()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email'))
        password = request.form.get('password')
        
        if not email or not password:
            flash("Please fill in all fields.", category="error")
            return render_template("login.html")
        
        if not validate_email(email):
            flash("Please enter a valid email address.", category="error")
            return render_template("login.html")
        
        # Check if user exists in database
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user'] = email
            session['user_id'] = user.id
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash("Login successful!", category="success")
            return redirect(url_for('auth.dashboard'))
        else:
            flash("Invalid email or password.", category="error")
    
    return render_template("login.html")

@auth.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    flash("You have been logged out.", category="success")
    return render_template("logout.html")

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email'))
        firstName = sanitize_input(request.form.get('firstName'))
        lastName = sanitize_input(request.form.get('lastName'))
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Validation
        if not email or not firstName or not lastName or not password1 or not password2:
            flash('Please fill in all fields.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif not validate_email(email):
            flash('Please enter a valid email address.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 12:
            flash('Password must be at least 12 characters.', category='error')
        else:
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('An account with this email already exists.', category='error')
            else:
                # Create new user
                try:
                    new_user = User(
                        email=email,
                        first_name=firstName,
                        last_name=lastName
                    )
                    new_user.set_password(password1)
                    
                    db.session.add(new_user)
                    db.session.commit()
                    
                    flash('Account created successfully! Please log in.', category='success')
                    return redirect(url_for('auth.login'))
                except Exception as e:
                    db.session.rollback()
                    flash('An error occurred while creating your account. Please try again.', category='error')

    return render_template("sign_up.html")

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email'))
        
        if not email:
            flash("Please enter your email address.", category="error")
            return render_template("forgot_password.html")
        
        if not validate_email(email):
            flash("Please enter a valid email address.", category="error")
            return render_template("forgot_password.html")
        
        # Check if user exists (but don't reveal if they don't for security)
        user = User.query.filter_by(email=email).first()
        
        # Always show success message for security (prevents email enumeration)
        flash("If that email is registered, a reset link will be sent.", category="success")
        return redirect(url_for('auth.login'))
    
    return render_template("forgot_password.html")

@auth.route('/dashboard')
def dashboard():
    if not session.get('user'):
        flash("Please log in to view the dashboard.", category="error")
        return redirect(url_for('auth.login'))
    
    # Get user information from database
    user = User.query.filter_by(email=session['user']).first()
    if not user:
        flash("User not found. Please log in again.", category="error")
        session.pop('user', None)
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))
    
    return render_template("dashboard.html", user=user)