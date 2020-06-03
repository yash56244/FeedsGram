from main import app, db, bcrypt
from flask import redirect, render_template, url_for, request, abort, \
    flash, session
from flask_login import login_user, logout_user, current_user, \
    login_required
from main.forms import LoginForm, RegistrationForm, \
    AccountUpdateForm, EmptyForm
from main.models import User, Article, Notification
from datetime import datetime


@app.context_processor
def context_processor():
    user = User.query.all()
    accounts = db.session.execute('select count(id) as c from user'
                                  ).scalar()
    return dict(key=user, count=accounts)
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm(request.form)
    if form.validate_on_submit() and request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,
                form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Please check your credentials', 'danger')
    return render_template('login.html', form=form, title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = \
            bcrypt.generate_password_hash(form.password.data).decode('utf-8'
                )
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_pwd)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! Please Login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='Register')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    articles = \
        Article.query.filter_by(author=current_user).order_by(Article.date_posted.desc()).paginate(page=page,
            per_page=3)
    return render_template('dashboard.html', title='Dashboard',
                           articles=articles)

@app.route('/like/<int:article_id>/<action>')
@login_required
def like_action(article_id, action):
    article = Article.query.filter_by(id=article_id).first_or_404()
    if action == 'like':
        if current_user.id != article.user_id:
            message = "{} liked your article titled \"{}\"".format(current_user.username, article.title)
            user = User.query.filter_by(id=article.user_id).first_or_404()
            notification = Notification(author=current_user, receiver = user, message=message)
            db.session.add(notification)
        current_user.like_article(article)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_article(article)
        db.session.commit()
    return redirect(request.referrer)

@app.route('/notification')
@login_required
def notification():
    current_user.last_notification_seen_time = datetime.utcnow()
    db.session.commit()
    notification_received = current_user.notifications_received.order_by(Notification.time.desc())
    return render_template('notification.html', notification_received=notification_received)

@app.route('/feed')
@login_required
def feed():
    page = request.args.get('page', 1, type=int)
    articles = \
        Article.query.order_by(Article.date_posted.desc()).paginate(page=page,
            per_page=3)
    return render_template('dashboard.html', articles=articles,
                           title='Feed')


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = AccountUpdateForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.current_password.data is not None \
            and bcrypt.check_password_hash(current_user.password,
                form.current_password.data):
            pwd_hash = \
                bcrypt.generate_password_hash(form.new_password.data).decode('utf-8'
                    )
            current_user.password = pwd_hash
        db.session.commit()
        flash('Your account credentials has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)


@app.route('/article/new', methods=['POST', 'GET'])
@login_required
def new_article():
    if request.method == 'POST':
        article = Article(title=request.form.get('title'),
                          content=request.form.get('editordata'),
                          author=current_user)
        db.session.add(article)
        db.session.commit()
        flash('Your article has been posted!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('new_article.html', title='New Article',
                           legend='New Article')


@app.route('/article/<int:article_id>')
def article(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template('article.html', title=article.title,
                           article=article)


@app.route('/article/<int:article_id>/update', methods=['GET', 'POST'])
@login_required
def update_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.author != current_user:
        abort(403)
    if request.method == 'POST':
        article.title = request.form.get('title')
        article.content = request.form.get('editordata')
        db.session.commit()
        flash('Your article has been updated!', 'success')
        return redirect(url_for('article', article_id=article.id))
    return render_template('new_article.html', title='Update Article',
                           legend='Update Article')


@app.route('/article/<int:article_id>/delete', methods=['POST'])
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.author != current_user:
        abort(403)
    db.session.delete(article)
    db.session.commit()
    flash('Your article has been deleted', 'success')
    return redirect(url_for('dashboard'))


@app.route('/user/<string:username>')
def user_articles(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    articles = \
        Article.query.filter_by(author=user).order_by(Article.date_posted.desc()).paginate(page=page,
            per_page=3)
    form = EmptyForm()
    return render_template('user_articles.html', articles=articles,
                           user=user, title=username, form=form)


@app.route('/follow/<string:username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username), 'danger')
            return redirect(url_for('dashboard'))
        if user == current_user:
            flash('You cannot follow yourself!', 'warning')
            return redirect(url_for('user_articles', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are now following {} '.format(username), 'success')
        return redirect(url_for('user_articles', username=username))


@app.route('/unfollow/<string:username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username), 'danger')
            return redirect(url_for('dashboard'))
        if user == current_user:
            flash('You cannot unfollow yourself!', 'warning')
            return redirect(url_for('user_articles', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You have unfollowed {} '.format(username), 'success')
        return redirect(url_for('user_articles', username=username))
