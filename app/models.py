from .extensions import db
from datetime import datetime
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import json


@login.user_loader
def load_user(user_id):
    return db.session.get(UserModel, int(user_id))


class UserModel(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    avatar = db.Column(db.String(100))
    join_time = db.Column(db.DateTime, default=datetime.now)
    points = db.Column(db.Integer, default=0)
    # security
    security_question = db.Column(db.String(255), nullable=False)
    security_answer_hash = db.Column(db.String(255), nullable=False)
    #relationship
    posts = db.relationship('PostModel', backref='author', lazy=True)
    comments = db.relationship('CommentModel', backref='author', lazy=True)
    notifications = db.relationship('Notification', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_notification(self, name, data, post_id=None):
        #
        # existing_notifications = Notification.query.filter_by(user_id=self.id, name=name).all()
        # for notification in existing_notifications:
        #     db.session.delete(notification)
        n = Notification(name=name, payload_json=json.dumps(data), user=self, post_id=post_id)
        db.session.add(n)
        db.session.commit()
        return n


    def set_security_answer(self, answer):
        self.security_answer_hash = generate_password_hash(answer)

    def check_security_answer(self, answer):
        return check_password_hash(self.security_answer_hash, answer)


class PostModel(db.Model):
    # post的数据模型
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    # is_done = db.Column(db.Boolean, default=False)
    post_type = db.Column(db.String(10))
    postcode = db.Column(db.Integer, nullable=False)
    # foreign key
    accepted_answer_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # relationship
    accepted_answer = db.relationship('CommentModel', foreign_keys=[accepted_answer_id], post_update=True)


class CommentModel(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    is_accepted = db.Column(db.Boolean, default=False)
    # foreign key
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # relationship
    post = db.relationship(PostModel, foreign_keys=[post_id], backref=db.backref("comments", order_by=create_time.desc()))


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer)  # 与回复相关的帖子 ID
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    payload_json = db.Column(db.Text)

    user = db.relationship('UserModel', back_populates='notifications')

    def get_data(self):
        return json.loads(str(self.payload_json))