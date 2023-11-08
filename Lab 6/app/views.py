

import json
import os
import io
import platform
from datetime import datetime
import datetime
from flask import render_template, request, session, redirect, url_for, flash, make_response
from app import app, db
from app.forms import FeedbackForm
from app.models import Feedback
from app import app, db
from app.forms import LoginForm  
from app.models import Todo
from app.forms import TodoForm

app.secret_key = b'secret'

# Path to the JSON file containing user data
users_json_path = 'Lab 6/app/static/files/users.json'

# Load user data from the JSON file
with open(users_json_path, 'r') as users_file:
    users_data = json.load(users_file)

# Function to save user data to the JSON file
def save_users_data():
    with open(users_json_path, 'w') as users_file:
        json.dump(users_data, users_file, indent=4)

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
@app.route('/todo')
def home():
    todo_list = db.session.query(Todo).all()
    form = TodoForm()  
    return render_template("todo.html", todo_list=todo_list, form=form, common=common) 

@app.route("/add", methods=["POST"])
def add():
    form = TodoForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        new_todo = Todo(title=title, description=description, complete=False)
        db.session.add(new_todo)
        db.session.commit()
    return redirect(url_for("home"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))
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

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if username in users_data:
            if users_data[username]['password'] == password:
                user_info = users_data[username]
                session['user_info'] = user_info
                flash('Ваші дані було збережено', 'success')  # Flash message for successful login
                return redirect(url_for('info'))
            else:
                flash('Невірний пароль', 'error')  # Flash message for incorrect password
        else:
            flash('Невірне імя користувача', 'error')  # Flash message for incorrect username

    if 'user_info' in session:
        flash('Ви вже увійшли', 'info')  # Flash message for already logged in
        return redirect(url_for('info'))


    return render_template('login.html', form=form, common=common)

# Route for the user info page
@app.route('/info', methods=['GET', 'POST'])
def info():
    user_info = session.get('user_info')
    projects_data = get_static_json("static/projects/projects.json")['projects']

    if request.method == 'POST':
        action = request.form.get('action')

        if user_info:
            if action == 'logout':
                session.pop('user_info', None)
                flash('Ви успішно вийшли з системи', 'success')
                return redirect(url_for('login'))

            elif action == 'change_password':
                new_password = request.form.get('new_password')

                if not new_password:
                    flash('Відсутній новий пароль', 'error')
                    return redirect(url_for('info'))

                users_data[user_info['username']]['password'] = new_password

                save_users_data()
                flash('Пароль успішно змінено', 'success')

            elif action == 'add_cookie':
                cookie_key = request.form.get('cookie_key')
                cookie_value = request.form.get('cookie_value')
                expire_time = request.form.get('cookie_expire_time')

                if not cookie_key or not cookie_value:
                    flash('Відсутній ключ або значення cookie', 'error')
                elif not expire_time.isnumeric():
                    flash('Недійсний термін дії', 'error')
                else:
                    expire_time = int(expire_time)
                    response = make_response(render_template('info.html', common=common, user_info=user_info, projects=projects_data))
                    response.set_cookie(cookie_key, cookie_value, max_age=expire_time)
                    flash('Файл cookie успішно додано', 'success')
                    return response

            elif action == 'delete_cookie':
                cookie_key_delete = request.form.get('cookie_key_delete')
                if cookie_key_delete:
                    response = make_response(render_template('info.html', common=common, user_info=user_info, projects=projects_data))
                    response.delete_cookie(cookie_key_delete)
                    flash('Файл cookie успішно видалено', 'success')
                    return response
                else:
                    flash('Відсутній ключ cookie', 'error')

    if user_info:
        return render_template('info.html', common=common, user_info=user_info, projects=projects_data)
    else:
        flash('Ви повинні увійти, щоб отримати доступ до цієї сторінки', 'error')
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
