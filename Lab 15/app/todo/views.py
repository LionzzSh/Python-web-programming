from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from . import todo_bp
from .forms import TodoForm
from .models import Todo
from app import db

@todo_bp.route('/todo', methods=['GET', 'POST'])
@login_required
def todo():
    form = TodoForm()

    if form.validate_on_submit():
        task = form.task.data
        new_todo = Todo(task=task)
        db.session.add(new_todo)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('todo.todo'))

    todos = Todo.query.all()
    return render_template('todo/todo.html', form=form, todos=todos)

@todo_bp.route('/todo/update/<int:id>')
@login_required
def update_todo(id):
    todo = Todo.query.get_or_404(id)
    todo.status = not todo.status  # Toggle status
    db.session.commit()
    flash('Task updated successfully!', 'success')
    return redirect(url_for('todo.todo'))

@todo_bp.route('/todo/delete/<int:id>')
@login_required
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('todo.todo'))
