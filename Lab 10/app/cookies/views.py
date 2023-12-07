from flask import render_template, request, make_response, redirect, url_for, flash, session
from flask_login import login_required, current_user
from datetime import datetime
from ..extensions import db
from . import cookies_bp
from .forms import ChangePasswordForm

user_session = {}
@cookies_bp.route('/info', methods=['GET', 'POST'])
@login_required
def info():
    form = ChangePasswordForm()

    if current_user.is_authenticated:
        email = current_user.email

        cookies = []
        for key, value in request.cookies.items():
            expiration = request.cookies[key]
            creation_time = session.get(f'cookie_creation_{key}')
            cookies.append({
                'key': key,
                'value': value,
                'expiration': expiration,
                'creation_time': creation_time,
            })

        if request.method == 'POST':
            if 'cookie_key' in request.form and 'cookie_value' in request.form and 'cookie_expiration' in request.form:
                cookie_key = request.form['cookie_key']
                cookie_value = request.form['cookie_value']
                cookie_expiration = int(request.form['cookie_expiration'])

                response = make_response(redirect(url_for('cookies.info')))
                response.set_cookie(cookie_key, cookie_value, max_age=cookie_expiration)
                session[f'cookie_creation_{cookie_key}'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                flash(f"Cookie '{cookie_key}' added successfully.", 'success')

            if 'delete_cookie_key' in request.form:
                delete_cookie_key = request.form['delete_cookie_key']

                if delete_cookie_key in request.cookies:
                    response = make_response(redirect(url_for('cookies.info')))
                    response.delete_cookie(delete_cookie_key)
                    session.pop(f'cookie_creation_{delete_cookie_key}', None)
                    flash(f"Cookie '{delete_cookie_key}' deleted successfully.", 'success')

            if 'delete_all_cookies' in request.form:
                response = make_response(redirect(url_for('cookies.info')))
                for key in request.cookies:
                    response.delete_cookie(key)
                    session.pop(f'cookie_creation_{key}', None)
                flash("All cookies deleted successfully.", 'success')

            return response

        return render_template('cookies/info.html', email=email, cookies=cookies, form=form)

    else:
        flash("You are not logged in. Please log in to access this page.", "error")
        return redirect(url_for('profile.login'))

@cookies_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        user = current_user

        if user and user.checkPassword(form.old_password.data):
            try:
                # Update the password
                user.set_password(form.new_password.data)
                db.session.commit()
                flash("Password changed", category="success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {e}", category="danger")
        else:
            flash("Invalid password", category="danger")
    else:
        flash("Form validation failed", category="danger")

    return redirect(url_for('profile.account'))

@cookies_bp.route('/add_cookie', methods=['POST'])
def add_cookie():
    if 'username' in user_session:
        if request.method == 'POST':
            cookie_key = request.form.get('cookie_key')
            cookie_value = request.form.get('cookie_value')
            cookie_expiration = int(request.form.get('cookie_expiration'))

            response = make_response(redirect(url_for('info')))
            response.set_cookie(cookie_key, cookie_value, max_age=cookie_expiration)
            session[f'cookie_creation_{cookie_key}'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            flash(f"Cookie '{cookie_key}' added successfully.", 'success')

            return response
        else:
            return redirect(url_for('info'))
    else:
        return redirect(url_for('login'))

@cookies_bp.route('/delete_cookie', methods=['POST'])
def delete_cookie():
    if 'username' in user_session:
        if request.method == 'POST':
            if 'delete_cookie_key' in request.form:
                delete_cookie_key = request.form['delete_cookie_key']

                if delete_cookie_key in request.cookies:
                    response = make_response(redirect(url_for('info')))
                    response.delete_cookie(delete_cookie_key)
                    session.pop(f'cookie_creation_{delete_cookie_key}', None)
                    flash(f"Cookie '{delete_cookie_key}' deleted successfully.", 'success')

                    return response

        return redirect(url_for('info'))
    else:
        return redirect(url_for('login'))

@cookies_bp.route('/delete_all_cookies', methods=['POST'])
def delete_all_cookies():
    if 'username' in user_session:
        if request.method == 'POST':
            response = make_response(redirect(url_for('info')))
            for key in request.cookies:
                response.delete_cookie(key)
                session.pop(f'cookie_creation_{key}', None)
            flash("All cookies deleted successfully.", 'success')

            return response
        return redirect(url_for('info'))
    else:
        return redirect(url_for('login'))

