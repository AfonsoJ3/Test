from flask import Blueprint as bl, render_template, request, flash, session, redirect, url_for

auth = bl('auth', __name__)

# Simple in-memory user storage (temporary solution until database is implemented)
users_db = {
    "admin@example.com": {
        "password": "password",
        "firstName": "Admin",
        "lastName": "User"
    }
}

@auth.route('/login', methods=['GET', 'POST'])
def login(): 
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user exists and password matches
        if email in users_db and users_db[email]["password"] == password:
            # Set session to authenticated
            session['authenticated'] = True
            session['user_email'] = email
            session['user_firstName'] = users_db[email]["firstName"]
            flash("Login successful!", category="success")
            # Redirect to home page instead of rendering directly
            return redirect(url_for('views.home'))
        else:
            flash("Invalid email or password.", category="error")
    return render_template("login.html")

@auth.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash("You have been logged out successfully.", category="success")
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Validation
        if len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 12:
            flash('Password must be at least 12 characters.', category='error')
        elif email in users_db:
            flash('Email address already exists. Please use a different email.', category='error')
        else:
            # Create the user account
            users_db[email] = {
                "password": password1,
                "firstName": firstName,
                "lastName": lastName
            }
            flash('Account created! Please log in.', category='success')
            return redirect(url_for('auth.login'))

    return render_template("sign_up.html")