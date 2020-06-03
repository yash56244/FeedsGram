from main import db, app, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(15), nullable=False)
    articles = db.relationship('Article', backref='author', lazy=True)
    followed = db.relationship('User', secondary=followers, primaryjoin=(followers.c.follower_id==id), 
        secondaryjoin=(followers.c.followed_id==id), backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    liked = db.relationship(
        'PostLike',
        foreign_keys='PostLike.user_id',
        backref='user', lazy='dynamic')
    notifications_sent = db.relationship('Notification', foreign_keys="Notification.senderId", backref='author', lazy='dynamic')
    notifications_received = db.relationship('Notification', foreign_keys="Notification.receiverId", backref='receiver', lazy='dynamic')
    last_notification_seen_time = db.Column(db.DateTime)

    def like_article(self, article):
        if not self.has_liked_article(article):
            like = PostLike(user_id=self.id, article_id=article.id)
            db.session.add(like)

    def unlike_article(self, article):
        if self.has_liked_article(article):
            PostLike.query.filter_by(
                user_id=self.id,
                article_id=article.id).delete()

    def has_liked_article(self, article):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.article_id == article.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def new_notifications(self):
        last_read_time = self.last_notification_seen_time or datetime(1900,1,1)
        return Notification.query.filter_by(receiver=self).filter(Notification.time > last_read_time).count()

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    likes = db.relationship('PostLike', backref='article', lazy='dynamic')
    
    def __repr__(self):
        return f"Article('{self.title}', '{self.date_posted}')"

class PostLike(db.Model):
    __tablename__ = 'article_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    senderId = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiverId = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String())
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow())

    def __repr__(self):
        return 'Notification {}'.format(self.message)
