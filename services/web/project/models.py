from datetime import datetime, timedelta
import json
from time import time
from hashlib import md5
import os
import redis
import rq
import base64
from flask import current_app, url_for
from flask_login import current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from project import db, login
from project.search import add_to_index, remove_from_index, query_index


class PagenatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            "items": [item.to_dict() for item in resources.items],
            "_meta": {
                "page": page,
                "per_page": per_page,
                "total_pages": resources.pages,
                "total_items": resources.total,
            },
            "_links": {
                "self": url_for(endpoint, page=page, per_page=per_page, **kwargs),
                "next": url_for(endpoint, page=page + 1, per_page=per_page, **kwargs)
                if resources.has_next
                else None,
                "prev": url_for(endpoint, page=page - 1, per_page=per_page, **kwargs)
                if resources.has_prev
                else None,
            },
        }
        return data


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return (
            cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)),
            total,
        )

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            "add": list(session.new),
            "update": list(session.dirty),
            "delete": list(session.deleted),
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes["add"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes["update"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes["delete"]:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, "before_commit", SearchableMixin.before_commit)
db.event.listen(db.session, "after_commit", SearchableMixin.after_commit)

# Followers association table
followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id")),
)

category_index = db.Table(
    "category_index",
    db.Column("clothes_index_id", db.Integer, db.ForeignKey("clothes_index.id")),
    db.Column("category_id", db.Integer, db.ForeignKey("category.id")),
    db.Column("conditional", db.Boolean),
)


class User(PagenatedAPIMixin, SearchableMixin, UserMixin, db.Model):
    __searchable__ = ["username"]

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    # Many-to-many followers relationship
    followed = db.relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic",
    )
    messages_sent = db.relationship(
        "Message", foreign_keys="Message.sender_id", backref="author", lazy="dynamic"
    )
    messages_received = db.relationship(
        "Message",
        foreign_keys="Message.recipient_id",
        backref="recipient",
        lazy="dynamic",
    )
    last_message_read_time = db.Column(db.DateTime)
    notifications = db.relationship("Notification", backref="user", lazy="dynamic")
    tasks = db.relationship("Task", backref="user", lazy="dynamic")
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    own_clothes = db.relationship("Clothes", backref="owner", lazy="dynamic")
    outfits = db.relationship("Outfit", backref="owner", lazy="dynamic")
    location_id = db.Column(db.Integer, index=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")

    def avatar(self, size):
        """
        """
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"http://www.gravatar.com/avatar/{digest}?d=retro&s={size}"

    def follow(self, user):
        """
        Add followers.
        """
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """
        Remove followers.
        """
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        """
        Check if a self user follows an user of the argument.
        """
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        """
        Return posts of a self user and followed users.
        """
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return (
            Message.query.filter_by(recipient=self)
            .filter(Message.timestamp > last_read_time)
            .count()
        )

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue(
            "project.tasks." + name, self.id, *args, **kwargs
        )
        task = Task(id=rq_job.get_id(), name=name, description=description, user=self)
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self, complete=False).first()

    def to_dict(self, include_email=False):
        data = {
            "id": self.id,
            "username": self.username,
            "last_seen": self.last_seen.isoformat() + "Z",
            "about_me": self.about_me,
            "location": Location.query.filter_by(id=self.location_id).first(),
            "post_count": self.posts.count(),
            "clothes_count": self.own_clothes.count(),
            "outfit_count": self.oputfits.count(),
            "follower_count": self.followers.count(),
            "followed_count": self.followed.count(),
            "_links": {
                "self": url_for("api.get_user", id=self.id),
                "followers": url_for("api.get_followers", id=self.id),
                "followed": url_for("api.get_followed", id=self.id),
                "avatar": self.avatar(128),
            },
        }
        if include_email:
            data["email"] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ["username", "email", "about_me"]:
            if field in data:
                setattr(self, field, data[field])
            if new_user and "password" in data:
                self.set_password(data["password"])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode("utf-8")
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except:
            return
        return User.query.get(id)

    @staticmethod
    def revoke_token(token):
        user = User.query.filter_by(token=token).first()
        if uset is None or user.token_expiration < datetime.utcnow():
            return None
        return user


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(SearchableMixin, db.Model):
    __searchable__ = ["body"]

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    language = db.Column(db.String(5))

    def __repr__(self):
        return f"<Post {self.body}>"


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message {self.body}>"


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get("progress", 0) if job is not None else 100


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, index=True)
    child_id = db.Column(db.Integer, index=True)
    parent_name = db.Column(db.String(30))
    child_name = db.Column(db.String(30))

    def __repr__(self):
        return f"<Category {self.id}:{self.parent_name}-{self.child_name}>"


class Clothes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True, nullable=True)
    note = db.Column(db.String(140), nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    category_id = db.Column(db.Integer, index=True)

    def __repr__(self):
        return f"<Clothes {self.id}:{self.name}>"


class Outfit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), index=True, nullable=True)
    note = db.Column(db.String(140), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    outerwear_id = db.Column(db.Integer, db.ForeignKey("clothes.id"))
    top_1_id = db.Column(db.Integer, db.ForeignKey("clothes.id"))
    top_2_id = db.Column(db.Integer, db.ForeignKey("clothes.id"))
    bottom_id = db.Column(db.Integer, db.ForeignKey("clothes.id"))

    outerwear = db.relationship("Clothes", foreign_keys="Outfit.outerwear_id")
    top_1 = db.relationship("Clothes", foreign_keys="Outfit.top_1_id")
    top_2 = db.relationship("Clothes", foreign_keys="Outfit.top_2_id")
    bottom = db.relationship("Clothes", foreign_keys="Outfit.bottom_id")

    def __repr__(self):
        return f"<Outfit {self.name}>"


class Forecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, index=True)
    clothes_index_id = db.Column(db.Integer)
    weather = db.Column(db.String(30), nullable=True)
    highest_temp = db.Column(db.Integer, nullable=True)
    lowest_temp = db.Column(db.Integer, nullable=True)
    rain_chance = db.Column(db.Integer, nullable=True)
    update_time = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return f"<Forecast {self.id}:{self.update_time}>"


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer)
    pref_id = db.Column(db.Integer)
    city_id = db.Column(db.Integer)
    area_name = db.Column(db.String(20))
    pref_name = db.Column(db.String(20))
    city_name = db.Column(db.String(20))

    def __repr__(self):
        return f"<Location {self.id}:{self.pref_name}/{self.city_name}>"


class ClothesIndex(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)
    description = db.Column(db.String(140))
    categories = db.relationship(
        "Category", secondary=category_index, backref="category_indexes", lazy="dynamic"
    )

    def __repr__(self):
        return f"<ClothesIndex {self.id}:{self.value}>"
