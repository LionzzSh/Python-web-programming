from flask import render_template, flash, redirect, url_for, request
from sqlalchemy import desc
from app import db
from flask_login import login_required, current_user
from ..pic_upd import save_picture
from .forms import PostForm, CategoryForm, TagForm, SearchForm
from .models import Post, EnumTypes, PostCategory, Tag
from . import posts_bp
import os
from PIL import Image
from flask import current_app
import uuid


def save_picture(form_picture, save_path):
    # Генерує унікальне ім'я файлу
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = str(uuid.uuid4()) + f_ext
    picture_path = os.path.join(save_path, picture_fn)

    # Перевіряє, чи існує директорія для збереження, і створює її, якщо ні
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Змінює розмір зображення та зберігає його
    output_size = (125, 125)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)

    return picture_fn

@posts_bp.route('/', methods=["GET"])
def posts_page():
    form = SearchForm()
    form.category.choices.extend([(c.id, c.name) for c in PostCategory.query.all()])

    category_id = request.args.get('category', -1, type=int)
    page = request.args.get('page', 1, type=int)

    pagination = Post.query

    if current_user.is_authenticated:
        pagination = pagination.filter(db.or_(Post.enabled == True, Post.user_id == current_user.id)).order_by(
            desc(Post.created))
    else:
        pagination = pagination.filter(Post.enabled == True).order_by(desc(Post.created))

    if category_id > 0:
        pagination = pagination.filter(Post.category_id == category_id)

    pagination = pagination.paginate(page=page, per_page=2)

    categ_count = PostCategory.query.count()
    teg_count = Tag.query.count()
    return render_template("posts/posts.html", form=form, pagination=pagination, categ_count=categ_count,
                           teg_count=teg_count)


@posts_bp.route("/new", methods=["GET", "POST"])
@login_required
def add_post():
    form = PostForm()

    # Fetch categories and tags
    categories = [(c.id, c.name) for c in PostCategory.query.all()]
    tags = [(t.id, t.name) for t in Tag.query.all()]

    form.categories.choices = categories
    form.tags.choices = tags

    if form.validate_on_submit():
        image = save_picture(form.image.data, f'{posts_bp.root_path}/static/posts/posts_image') if form.image.data else None

        new_post = Post(
            title=form.title.data,
            text=form.text.data,
            image=image,
            type=form.type.data,
            enabled=form.enabled.data,
            user_id=current_user.id,
            category_id=form.categories.data,
            tags=[tag for tag in Tag.query.filter(Tag.id.in_(form.tags.data)).all()]
        )

        try:
            db.session.add(new_post)
            db.session.commit()
            flash('Post added!', category='success')
            return redirect(url_for("posts.posts_page", id=new_post.id))
        except:
            db.session.rollback()
            flash('Error!', category='danger')

    return render_template(
        "posts/create_post.html", form=form, categories=categories, tags=tags
    )


@posts_bp.route('/<int:id>', methods=["GET"])
def post_page(id):
    post = Post.query.get_or_404(id)
    if not post.enabled and post.user.id != current_user.id:
        return redirect(url_for("posts.posts_page"))

    return render_template("posts/post.html", post=post)


@posts_bp.route("/update/<int:id>", methods=["GET", "POST"])
def update_post(id):
    post = Post.query.get_or_404(id)

    if current_user.id != post.user.id:
        return redirect(url_for("posts.posts_page", id=id))

    form = PostForm(obj=post)

    if form.validate_on_submit():

        post.title = form.title.data
        post.text = form.text.data
        post.type = form.type.data
        post.enabled = form.enabled.data
        post.category_id = form.categories.data
        post.tags = [tag for tag in Tag.query.filter(Tag.id.in_(form.tags.data)).all()]

        if form.image.data:
            post.image = save_picture(form.image.data, f'{posts_bp.root_path}/static/posts/posts_image')

        try:
            db.session.commit()
            flash(f'Post ({post.title}) updated!', category='success')
            return redirect(url_for("posts.post_page", id=id))
        except:
            db.session.rollback()
            flash('Error!', category='danger')

        return redirect(url_for("posts.update_post", id=id))

    form.type.data = str(post.type.value)
    form.enabled.data = post.enabled
    return render_template("posts/update_post.html", form=form, post=post)


@posts_bp.route("/delete/<int:id>", methods=["POST"])
def delete_post(id):
    if request.method == 'POST':
        post = Post.query.get_or_404(id)

        if current_user.id == post.user.id:
            try:
                db.session.delete(post)
                db.session.commit()
                flash(f'Post ({post.title}) deleted!', category='success')
            except:
                db.session.rollback()
                flash('Error!', category='danger')

    return redirect(url_for("posts.posts_page"))


@posts_bp.route('/categories', methods=["GET", "POST"])
def categories_page():
    form = CategoryForm()

    if form.validate_on_submit():
        new_category = PostCategory(name=form.name.data)
        try:
            db.session.add(new_category)
            db.session.commit()
            flash(f'Category ({new_category.name}) created!', category='success')
        except Exception as e:
            flash(f'Error: {e}', category='danger')
            db.session.rollback()

    categories = PostCategory.query.all()
    return render_template("posts/categories.html", categories=categories, form=form)

@posts_bp.route("/categories/new", methods=["POST"])
def add_category():
    print("Inside add_category route")
    form = CategoryForm()

    if form.validate_on_submit():
        new_category = PostCategory(name=form.name.data)
        try:
            db.session.add(new_category)
            db.session.commit()
            flash(f'Category ({new_category.name}) created!', category='success')
        except Exception as e:
            print(f"Error: {e}")
            flash('Error!', category='danger')
            db.session.rollback()
    else:
        print("Invalid form!")
        flash('Invalid form!', category='danger')

    print("Redirecting to categories_page")
    return redirect(url_for('posts.categories_page'))




@posts_bp.route("/categories/delete/<int:id>", methods=["POST"])
def delete_category(id):
    category = PostCategory.query.get_or_404(id)
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash(f'Category ({category.name}) deleted!', category='success')
    except Exception as e:
        flash(f'Error: {e}', category='danger')
        db.session.rollback()

    return redirect(url_for("posts.categories_page"))


@posts_bp.route('/tags', methods=["GET", "POST"])
def tags_page():
    form = TagForm()

    if form.validate_on_submit():
        new_tag = Tag(name=form.name.data)
        try:
            db.session.add(new_tag)
            db.session.commit()
            flash(f'Tag (#{new_tag.name}) created!', category='success')
        except Exception as e:
            flash(f'Error: {e}', category='danger')
            db.session.rollback()

    tags = Tag.query.all()
    return render_template("posts/tags.html", tags=tags, form=form)

@posts_bp.route("/tags/new", methods=["POST"])
def add_tag():
    form = TagForm()

    if form.validate_on_submit():
        new_tag = Tag(name=form.name.data)
        try:
            db.session.add(new_tag)
            db.session.commit()
            flash(f'Tag (#{new_tag.name}) created!', category='success')
        except Exception as e:
            flash(f'Error: {e}', category='danger')
            db.session.rollback()
    else:
        flash('Invalid form!', category='danger')

    return redirect(url_for('posts.tags_page'))

@posts_bp.route("/tags/delete/<int:id>", methods=["POST"])
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    
    try:
        db.session.delete(tag)
        db.session.commit()
        flash(f'Tag (#{tag.name}) deleted!', category='success')
    except Exception as e:
        flash(f'Error: {e}', category='danger')
        db.session.rollback()

    return redirect(url_for("posts.tags_page"))