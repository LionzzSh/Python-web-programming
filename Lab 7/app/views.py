import json
import os
import io
import platform
from datetime import datetime
import datetime
from flask import render_template, request, session, redirect, url_for, flash, make_response
from app import app, db
from app.forms import FeedbackForm, TodoForm, LoginForm, ChangePasswordForm, RegistrationForm
from app.models import Feedback, Todo, User
from flask import render_template, request, session, redirect, url_for, flash, make_response

app.secret_key = b'secret'

# Path to the JSON file containing user data
users_json_path = 'Lab 7/app/static/files/users.json'

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
    error_message = None
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.verify_password(form.password.data):
            if form.remember.data:
                session["email"] = form.email.data  # Ensure the 'email' key is being set
                flash("Login successful", category="success")
                return redirect(url_for("info"))

            flash("Login successful", category="success")
            return redirect(url_for("info"))

        flash("ERROR!!!", category="danger")
        return redirect(url_for("login"))

    return render_template('login.html', error_message=error_message, form=form, common=common)



@app.route("/registration", methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash(f"Account created for {form.username.data}!", "success")
        except:
            db.session.rollback()
            flash("ERROR, try use another data", category="danger")
            return redirect(url_for("registration"))

        return redirect(url_for('login'))
    return render_template("register.html", form=form, common=common)

@app.route('/info', methods=['GET', 'POST'])
def info():
    form = ChangePasswordForm()
    if 'email' in session:
        email = session['email']

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

                response = make_response(redirect(url_for('info')))
                response.set_cookie(cookie_key, cookie_value, max_age=cookie_expiration)
                session[f'cookie_creation_{cookie_key}'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                flash(f"Cookie '{cookie_key}' added successfully.", 'success')

            if 'delete_cookie_key' in request.form:
                delete_cookie_key = request.form['delete_cookie_key']

                if delete_cookie_key in request.cookies:
                    response = make_response(redirect(url_for('info')))
                    response.delete_cookie(delete_cookie_key)
                    session.pop(f'cookie_creation_{delete_cookie_key}', None)
                    flash(f"Cookie '{delete_cookie_key}' deleted successfully.", 'success')

            if 'delete_all_cookies' in request.form:
                response = make_response(redirect(url_for('info')))
                for key in request.cookies:
                    response.delete_cookie(key)
                    session.pop(f'cookie_creation_{key}', None)
                flash("All cookies deleted successfully.", 'success')

            return response

        return render_template('info.html', email=email, cookies=cookies, form=form, common=common)
    else:
        flash("You are not logged in. Please log in to access this page.", "error")
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

            flash(f"Cookie '{cookie_key}' added successfully.", 'success')

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
                    flash(f"Cookie '{delete_cookie_key}' deleted successfully.", 'success')

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
            flash("All cookies deleted successfully.", 'success')

            return response
        return redirect(url_for('info'))
    else:
        return redirect(url_for('login'))


@app.route('/logout', methods=['POST'])
def logout():
    if 'username' in user_session:
        del user_session['username']

    return redirect(url_for('login'))

@app.route('/change_password', methods=['POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=session.get("email")).first()

        if user and user.verify_password(form.old_password.data):
            try:
                user.password = form.new_password.data
                db.session.commit()
                flash("Password changed", category="success")
            except:
                db.session.rollback()
                flash("Error", category="danger")
        else:
            flash("Error", category="danger")
    else:
        flash("Error", category="danger")

    return redirect(url_for('info'))

@app.route('/todo', methods=['GET', 'POST'])
def todo():
    form = TodoForm()

    if form.validate_on_submit():
        task = form.task.data
        new_todo = Todo(task=task)
        db.session.add(new_todo)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('todo'))

    todos = Todo.query.all()
    return render_template('todo.html', form=form, todos=todos, common=common)

@app.route('/todo/update/<int:id>')
def update_todo(id):
    todo = Todo.query.get_or_404(id)
    todo.status = not todo.status  # Toggle status
    db.session.commit()
    flash('Task updated successfully!', 'success')
    return redirect(url_for('todo'))

@app.route('/todo/delete/<int:id>')
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('todo'))

@app.route('/users')
def users():
    return render_template('users.html', users=User.query.all())

if __name__ == '__main__':
    app.run(debug=True)
