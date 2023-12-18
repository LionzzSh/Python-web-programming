from flask import render_template, flash, redirect, url_for
from . import feedback_bp  # Import the feedback blueprint
from .forms import FeedbackForm
from .models import Feedback  # Import the Feedback model from the models module
from app import db  # Assuming your main app instance is named 'app'

common = {
    'first_name': 'Vitalii',
    'last_name': 'Shmatolokha',
}

@feedback_bp.route('/feedback', methods=['GET', 'POST'])
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

        return redirect(url_for('feedback.feedback'))

    feedback_data = Feedback.query.all()
    return render_template('feedback/feedback.html', form=form, feedback_data=feedback_data, common=common)