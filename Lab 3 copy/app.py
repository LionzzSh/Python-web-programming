import json
import os
import platform
import datetime
import io
from flask import Flask, request, render_template, redirect, url_for, session, flash, make_response

app = Flask(__name__)
app.secret_key = b'secret'

# Use the correct path to users.json inside the files folder
users_json_path = 'Lab 4/static/files/users.json'

with open(users_json_path, 'r') as users_file:
    users_data = json.load(users_file)

def save_users_data():
    with open(users_json_path, 'w') as users_file:
        json.dump(users_data, users_file, indent=4)

common = {
    'first_name': 'Vitalii',
    'last_name': 'Shmatolokha',
}

def get_static_file(path):
    site_root = os.path.realpath(os.path.dirname(__file__))
    return os.path.join(site_root, path)

def get_static_json(path):
    with open(get_static_file(path), "r", encoding="utf-8") as file:
        return json.load(file)

@app.route('/')
def index():
    return render_template('home.html', common=common)

@app.route('/biography')
def biography():
    biography = get_static_json("static/files/biography.json")
    return render_template('biography.html', common=common, biography=biography)

@app.route('/skills')
def skills():
    data = get_static_json("static/files/skills.json")
    return render_template('skills.html', common=common, data=data)

@app.route('/projects')
def projects():
    data = get_static_json("static/projects/projects.json")['projects']
    data.sort(key=lambda x: x.get('weight', 0), reverse=True)

    tag = request.args.get('tags')
    if tag is not None:
        tag = tag.lower()
        data = [project for project in data if tag in [p.lower() for p in project.get('tags', [])]]

    return render_template('projects.html', common=common, projects=data, tag=tag)

@app.route('/experiences')
def experiences():
    experiences = get_static_json("static/experiences/experiences.json")['experiences']
    experiences.sort(key=lambda x: x.get('weight', 0), reverse=True)
    return render_template('projects.html', common=common, projects=experiences, tag=None)

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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', common=common), 404

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
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users_data:
            if users_data[username]['password'] == password:
                user_info = users_data[username]
                session['user_info'] = user_info
                flash('Успішний вхід', 'success')
                return redirect(url_for('info'))
            else:
                flash('Невірний пароль', 'error')
        else:
            flash( 'Невірне імя користувача', 'error')
    
    if 'user_info' in session:
        flash('Ви вже увійшли', 'info')
        return redirect(url_for('info'))
    
    return render_template('login.html', common=common)

@app.route('/info', methods=['GET', 'POST'])
def info():
    user_info = session.get('user_info')
    projects_data = get_static_json("static/projects/projects.json")['projects']

    if request.method == 'POST':
        action = request.form.get('action')

        if user_info:
            if action == 'logout':
                session.pop('user_info', None)
                flash('Logged out successfully', 'success')
                return redirect(url_for('login'))

            elif action == 'change_password':
                new_password = request.form.get('new_password')

                if not new_password:
                    flash('New password is missing', 'error')
                    return redirect(url_for('info'))

                # Update the user's password in the users_data dictionary
                users_data[user_info['username']]['password'] = new_password

                # Save the updated data to the JSON file (users.json)
                save_users_data()
                flash('Password changed successfully', 'success')

            elif action == 'add_cookie':
                cookie_key = request.form.get('cookie_key')
                cookie_value = request.form.get('cookie_value')
                expire_time = request.form.get('cookie_expire_time')

                if expire_time is not None and expire_time.isnumeric():
                    expire_time = int(expire_time)
                else:
                    expire_time = None

                response = make_response(render_template('info.html', common=common, user_info=user_info, projects=projects_data))

                if expire_time is not None:
                    response.set_cookie(cookie_key, cookie_value, max_age=expire_time)
                    flash('Cookie added successfully', 'success')
                    return response
                else:
                    flash('Invalid expire time', 'error')
                    return response

            elif action == 'delete_cookie':
                cookie_key_delete = request.form.get('cookie_key_delete')
                if cookie_key_delete:
                    response = make_response(render_template('info.html', common=common, user_info=user_info, projects=projects_data))
                    response.delete_cookie(cookie_key_delete)
                    flash('Cookie deleted successfully', 'success')
                    return response
                else:
                    flash('Cookie key is missing', 'error')

    if user_info:
        return render_template('info.html', common=common, user_info=user_info, projects=projects_data)
    else:
        flash('You need to log in to access this page', 'error')
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
