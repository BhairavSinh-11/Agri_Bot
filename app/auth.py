from flask import Blueprint, render_template, redirect, url_for, flash, session
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required ,current_user
from .forms import RegistrationForm, LoginForm , ForgotResetForm
from .extension import oauth

auth = Blueprint('auth', __name__)
google= oauth.create_client('google')

#  REGISTER

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username=form.username.data.lower()
        user = User(
            username=username,
            display_name=username,
            email=form.email.data,
            password=form.password.data,
            )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


# ADMIN ROUTE

@auth.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Please login as admin first', 'danger')
        return redirect(url_for('auth.login'))

    users = User.query.all()
    return render_template('data.html', users=users)


# LOGIN

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.lower()
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):

            # CHECK ADMIN FROM DATABASE

            if user.is_admin:
                login_user(user)
                session['admin'] = True
                return redirect(url_for('auth.admin_dashboard'))

            # FOR NORMAL USER

            login_user(user)
            
            session['user'] = {
    "id": user.id,
    "name": user.display_name,   
    "username": user.username,
    "email": user.email
}
            return redirect(url_for('main.home'))

        else:
            flash('Invalid Username or Password', 'danger')

    return render_template('login.html', form=form)

# LOGOUT

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.home'))

#DELETE ROUTE

@auth.route('/delete/<int:id>')
@login_required
def delete_profile(id):
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('auth.admin_dashboard'))


#  FORGOT PASSWORD

@auth.route('/forgotpass', methods=['GET', 'POST'])
def forgotpass():
    form = ForgotResetForm()

    if form.validate_on_submit():
        email = form.email.data.lower()
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Email not found", "danger")
            return redirect(url_for('auth.forgotpass'))

        # 🔐 Update password
       
        user.set_password(form.password.data)
        db.session.commit()

        flash("Password reset successful!", "success")
        return redirect(url_for('auth.login'))

    return render_template('forgotpass.html', form=form)


#google login route
@auth.route('/login/google')
def google_login(): 
    try:
        redirect_uri = url_for('auth.google_callback', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)  
    except Exception as e:
         print("GOOGLE OAUTH ERROR:", e)

         flash(f"Google login failed: {str(e)}", "danger")

         return redirect(url_for('auth.login'))

#google auth callback route
@auth.route('/auth/google/callback')
def google_callback():

    try:

        token = google.authorize_access_token()

        user_info = token['userinfo']

        email = user_info['email']

        user = User.query.filter_by(email=email).first()

        if not user:

            username = email.split("@")[0].lower()

            user = User(
                email=email,
                username=username,
                display_name=user_info.get("name"),
                google_id=user_info.get("sub")
            )

            db.session.add(user)
            db.session.commit()

        login_user(user)

        session['user'] = {
            "id": user.id,
            "name": user.display_name,
            "username": user.username,
            "email": user.email
        }

        return redirect(url_for('main.home'))

    except Exception as e:

        print("Google OAuth Error:", e)

        flash("Google login failed", "danger")

        return redirect(url_for('auth.login'))
