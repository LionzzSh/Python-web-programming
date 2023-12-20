import os
from flask import Flask, render_template, redirect, request, abort
import json
import io
from datetime import datetime
from . import resume_bp 

user_session = {}

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
@resume_bp.route('/')
def index():
    return render_template('home.html', common=common)

# Route for the biography page
@resume_bp.route('/biography')
def biography():
    biography = get_static_json("static/files/biography.json")
    return render_template('biography.html', common=common, biography=biography)

# Route for the skills page
@resume_bp.route('/skills')
def skills():
    data = get_static_json("static/files/skills.json")
    return render_template('skills.html', common=common, data=data)

# Route for the projects page
@resume_bp.route('/projects')
def projects():
    data = get_static_json("static/projects/projects.json")['projects']
    data.sort(key=lambda x: x.get('weight', 0), reverse=True)

    tag = request.args.get('tags')
    if tag is not None:
        tag = tag.lower()
        data = [project for project in data if tag in [p.lower() for p in project.get('tags', [])]]

    return render_template('projects.html', common=common, projects=data, tag=tag)

# Route for the experiences page
@resume_bp.route('/experiences')
def experiences():
    experiences = get_static_json("static/experiences/experiences.json")['experiences']
    experiences.sort(key=lambda x: x.get('weight', 0), reverse=True)
    return render_template('projects.html', common=common, projects=experiences, tag=None)

# Route for individual project or experience
@resume_bp.route('/projects/<title>')
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

