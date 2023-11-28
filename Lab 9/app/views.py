import json
import os
import io
import platform
from datetime import datetime
import datetime
from flask import render_template, request, session, redirect, url_for, flash, make_response
from app import app, db
from app.forms import LoginForm, ChangePasswordForm, FeedbackForm, TodoForm, RegistrationForm, UpdateAccountForm
from app.models import Feedback, Todo, User
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import shutil

app.secret_key = b'secret'

# Path to the JSON file containing user data
users_json_path = 'Lab 9/app/static/files/users.json'

# Load user data from the JSON file
with open(users_json_path, 'r') as users_file:
    users_data = json.load(users_file)

# Function to save user data to the JSON file
def save_users_data():
    with open(users_json_path, 'w') as users_file:
        json.dump(users_data, users_file, indent=4)

user_session = {}

script_dir = os.path.dirname(os.path.realpath(__file__))
data_json_path = os.path.join(script_dir, 'data.json')

# Common data for templates
common = {
    'first_name': 'Vitalii',
    'last_name': 'Shmatolokha',
}

# Function to get the absolute path of a static file
def get_static_file(path):
    site_root = os.path.realpath(os.path.dirname(__file__))
    return os.path.join(site_root, path)

# Function to get JSON data from a static file
def get_static_json(path):
    with open(get_static_file(path), "r", encoding="utf-8") as file:
        return json.load(file)

# Route for the home page
@app.route('/')
def index():
    return render_template('home.html', common=common)

# Route for the biography page
@app.route('/biography')
def biography():
    biography = get_static_json("static/files/biography.json")
    return render_template('biography.html', common=common, biography=biography)

# Route for the skills page
@app.route('/skills')
def skills():
    data = get_static_json("static/files/skills.json")
    return render_template('skills.html', common=common, data=data)

# Route for the projects page
@app.route('/projects')
def projects():
    data = get_static_json("static/projects/projects.json")['projects']
    data.sort(key=lambda x: x.get('weight', 0), reverse=True)

    tag = request.args.get('tags')
    if tag is not None:
        tag = tag.lower()
        data = [project for project in data if tag in [p.lower() for p in project.get('tags', [])]]

    return render_template('projects.html', common=common, projects=data, tag=tag)

# Route for the experiences page
@app.route('/experiences')
def experiences():
    experiences = get_static_json("static/experiences/experiences.json")['experiences']
    experiences.sort(key=lambda x: x.get('weight', 0), reverse=True)
    return render_template('projects.html', common=common, projects=experiences, tag=None)

# Route for individual project or experience
@app.route('/projects/<title>')
def project(title):
    projects = get_static_json("static/projects/projects.json")['projects']
    experiences = get_static_json("static/experiences/experiences.json")['experiences']

    in_project = next((p for p in projects if p['link'] == title), None)
    in_exp = next((exp for exp in experiences if exp['link'] == title), None)

    if in_project is None and in_exp is None:
        return render_template('404.html'), 404

    elif in_project is not None and in_exp is not None:
        selected = in_exp
    elif in_project is not None:
        selected = in_project
    else:
        selected = in_exp

    if 'description' not in selected:
        path = "experiences" if in_exp is not None else "projects"
        selected['description'] = io.open(get_static_file(
            'static/%s/%s/%s.html' % (path, selected['link'], selected['link'])), "r", encoding="utf-8").read()
    return render_template('project.html', common=common, project=selected)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        name = form.name.data
        comment = form.comment.data

        feedback = Feedback(name=name, comment=comment)

        try:
            db.session.add(feedback)
            db.session.commit()
            flash('Відгук успішно надіслано', 'success')
        except:
            flash('Під час надсилання відгуку сталася помилка', 'error')

        return redirect(url_for('feedback'))

    feedback_data = Feedback.query.all()
    return render_template('feedback.html', form=form, feedback_data=feedback_data, common=common)

# Error handler for 404 Not Found
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', common=common), 404

# Context processor to provide additional data to templates
@app.context_processor
def utility_processor():
    os_info = platform.platform()
    user_agent = request.headers.get('User-Agent')
    current_time = datetime.datetime.now()
    return {
        'os_info': os_info,
        'user_agent': user_agent,
        'current_time': current_time
    }

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('info'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Вхід успішний", category="success")
            return redirect(url_for("info"))

        flash("Невірна адреса електронної пошти або пароль", category="danger")
        return redirect(url_for("login"))

    return render_template('login.html', form=form, common=common)

@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('info'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash(f"Обліковий запис створено для {form.username.data}!", "success")
            return redirect(url_for("login"))
        except:
            db.session.rollback()
            flash("ПОМИЛКА, спробуйте використати інші дані", category="danger")
            return redirect(url_for("registration"))

    return render_template("register.html", form=form, common=common)

@app.route('/info', methods=['GET', 'POST'])
@login_required
def info():
    form = ChangePasswordForm() 

    if current_user.is_authenticated:
        email = current_user.email
        cookies = []

        if request.method == 'POST':
            if 'cookie_key' in request.form and 'cookie_value' in request.form and 'cookie_expiration' in request.form:
                cookie_key = request.form['cookie_key']
                cookie_value = request.form['cookie_value']
                cookie_expiration = int(request.form['cookie_expiration'])

                response = make_response(redirect(url_for('info')))
                response.set_cookie(cookie_key, cookie_value, max_age=cookie_expiration)
                session[f'cookie_creation_{cookie_key}'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                flash(f"Cookie '{cookie_key}' успішно додано.", 'success')

            if 'delete_cookie_key' in request.form:
                delete_cookie_key = request.form['delete_cookie_key']

                if delete_cookie_key in request.cookies:
                    response = make_response(redirect(url_for('info')))
                    response.delete_cookie(delete_cookie_key)
                    session.pop(f'cookie_creation_{delete_cookie_key}', None)
                    flash(f"Cookie '{delete_cookie_key}' успішно видалено.", 'success')

            if 'delete_all_cookies' in request.form:
                response = make_response(redirect(url_for('info')))
                for key in request.cookies:
                    response.delete_cookie(key)
                    session.pop(f'cookie_creation_{key}', None)
                flash("Усі файли cookie успішно видалено.", 'success')

            return response

        return render_template('info.html', email=email, cookies=cookies, common=common, form=form)

    else:
        flash("Ви не ввійшли в систему. Увійдіть, щоб отримати доступ до цієї сторінки.", "error")
        return redirect(url_for('login'))
    
@app.route('/add_cookie', methods=['POST'])
def add_cookie():
    if 'username' in user_session:
        if request.method == 'POST':
            cookie_key = request.form.get('cookie_key')
            cookie_value = request.form.get('cookie_value')
            cookie_expiration = int(request.form.get('cookie_expiration'))

            response = make_response(redirect(url_for('info')))
            response.set_cookie(cookie_key, cookie_value, max_age=cookie_expiration)
            session[f'cookie_creation_{cookie_key}'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            flash(f"Cookie '{cookie_key}' успішно додано.", 'success')

            return response
        else:
            return redirect(url_for('info'))
    else:
        return redirect(url_for('login'))

@app.route('/delete_cookie', methods=['POST'])
def delete_cookie():
    if 'username' in user_session:
        if request.method == 'POST':
            if 'delete_cookie_key' in request.form:
                delete_cookie_key = request.form['delete_cookie_key']

                if delete_cookie_key in request.cookies:
                    response = make_response(redirect(url_for('info')))
                    response.delete_cookie(delete_cookie_key)
                    session.pop(f'cookie_creation_{delete_cookie_key}', None)
                    flash(f"Cookie '{delete_cookie_key}'успішно видалено.", 'success')

                    return response

        return redirect(url_for('info'))
    else:
        return redirect(url_for('login'))

@app.route('/delete_all_cookies', methods=['POST'])
def delete_all_cookies():
    if 'username' in user_session:
        if request.method == 'POST':
            response = make_response(redirect(url_for('info')))
            for key in request.cookies:
                response.delete_cookie(key)
                session.pop(f'cookie_creation_{key}', None)
            flash("Усі файли cookie успішно видалено.", 'success')

            return response
        return redirect(url_for('info'))
    else:
        return redirect(url_for('login'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST' or request.method == 'GET':
        logout_user()
        flash("Ви вийшли з системи", category="success")
        return redirect(url_for("login"))
    return redirect(url_for("login"))

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        user = current_user
                          #checkPassword
        if user and user.verify_password(form.old_password.data):
            try:
                # Update the password
                user.set_password(form.new_password.data)
                db.session.commit()
                flash("Пароль змінено", category="success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {e}", category="danger")
        else:
            flash("Недійсний пароль", category="danger")
    else:
        flash("Помилка перевірки форми", category="danger")

    return redirect(url_for('account'))


@app.route('/todo', methods=['GET', 'POST'])
def todo():
    form = TodoForm()

    if form.validate_on_submit():
        task = form.task.data
        new_todo = Todo(task=task)
        db.session.add(new_todo)
        db.session.commit()
        flash('Завдання успішно додано!', 'success')
        return redirect(url_for('todo'))

    todos = Todo.query.all()
    return render_template('todo.html', form=form, todos=todos, common=common)

@app.route('/todo/update/<int:id>')
def update_todo(id):
    todo = Todo.query.get_or_404(id)
    todo.status = not todo.status  # Toggle status
    db.session.commit()
    flash('Завдання успішно оновлено!', 'success')
    return redirect(url_for('todo'))

@app.route('/todo/delete/<int:id>')
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    flash('Завдання успішно видалено!', 'success')
    return redirect(url_for('todo'))

@app.route('/users')
def users():
    return render_template('users.html', users=User.query.all())

UPLOAD_FOLDER = 'static/imgs/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# end #


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    update_account_form = UpdateAccountForm(obj=current_user)
    change_password_form = ChangePasswordForm()

    if update_account_form.validate_on_submit():
        current_user.username = update_account_form.username.data
        current_user.email = update_account_form.email.data
        current_user.about_me = update_account_form.about_me.data

        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                current_user.image_file = filename

                # Move the file to the UPLOAD_FOLDER
                destination = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
                shutil.move(file_path, destination)

        db.session.commit()
        flash('Обліковий запис успішно оновлено!', 'success')
        return redirect(url_for('account'))

    if change_password_form.validate_on_submit():
        if current_user.check_password(change_password_form.old_password.data):
            try:
                current_user.set_password(change_password_form.new_password.data)
                db.session.commit()
                flash('Пароль успішно змінено!', 'success')
                return redirect(url_for('account'))
            except Exception as e:
                db.session.rollback()
                flash(f"Помилка зміни пароля: {e}", 'danger')
        else:
            flash('Введений пароль невірний', 'danger')


    return render_template('account.html', update_account_form=update_account_form, change_password_form=change_password_form, is_authenticated=True, common=common)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.update_last_seen()

if __name__ == '__main__':
    app.run(debug=True)
