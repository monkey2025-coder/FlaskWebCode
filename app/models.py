from app import db
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app 
from datetime import datetime
import hashlib 
from flask import request 
from markdown import markdown 
import bleach 

class Permission:  
    FOLLOW = 0x01 
    COMMENT = 0x02 
    WRITE_ARTICLES = 0x04 
    MODERATE_COMMENTS = 0x08 
    ADMINISTER = 0x80

class Role(db.Model): 
    __tablename__ = 'roles' 
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(64), unique=True) 
    default = db.Column(db.Boolean, default=False, index=True) 
    permissions = db.Column(db.Integer) 
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod 
    def insert_roles(): 
        roles = { 
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True), 
            'Moderator': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS, False), 
            'Administrator': (0xff, False) 
        } 
        for r in roles: 
            role = Role.query.filter_by(name=r).first() 
            if role is None: 
                role = Role(name=r) 
            role.permissions = roles[r][0] 
            role.default = roles[r][1] 
            db.session.add(role) 
        db.session.commit()

    def __repr__(self): 
        return '<Role %r>' % self.name 


class Follow(db.Model): 
    __tablename__ = 'follows' 
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
                            primary_key=True) 
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
                            primary_key=True) 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model): 
    __tablename__ = 'users' 
    id = db.Column(db.Integer, primary_key = True) 
    email = db.Column(db.String(64), unique=True, index=True) 
    username = db.Column(db.String(64), unique=True, index=True) 
    password_hash = db.Column(db.String(128)) 
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    name = db.Column(db.String(64)) 
    location = db.Column(db.String(64)) 
    about_me = db.Column(db.Text()) 
    member_since = db.Column(db.DateTime(), default=datetime.utcnow) 
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32)) 
    
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id], backref=db.backref('follower', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan') 
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], backref=db.backref('followed', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, **kwargs): 
        super(User, self).__init__(**kwargs)
        if self.role is None: 
            if self.email == current_app.config['FLASKY_ADMIN']: 
                self.role = Role.query.filter_by(permissions=0xff).first() 
            if self.role is None: 
                self.role = Role.query.filter_by(default=True).first() 
        if self.email is not None and self.avatar_hash is None: 
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest() 
        self.follow(self)
    
    @staticmethod 
    def add_self_follows(): 
        for user in User.query.all(): 
            if not user.is_following(user): 
                user.follow(user) 
                db.session.add(user) 
                db.session.commit() 
    
    @property 
    def followed_posts(self): 
        # 包含用户自己的文章和关注的人的文章
        return Post.query.filter(
            db.or_(
                Post.author_id == self.id,
                Post.author_id.in_(
                    db.session.query(Follow.followed_id).filter(Follow.follower_id == self.id)
                )
            )
        ).order_by(Post.timestamp.desc())
    
    def follow(self, user): 
       if not self.is_following(user): 
           f = Follow(follower=self, followed=user) 
           db.session.add(f) 
           db.session.commit()
    
    def unfollow(self, user): 
       if self.is_following(user): 
           f = self.followed.filter_by(followed_id=user.id).first() 
           if f: 
               db.session.delete(f) 
               db.session.commit()
    
    def is_following(self, user): 
        return self.followed.filter_by(followed_id=user.id).first() is not None
    
    def is_followed_by(self, user): 
        return self.followers.filter_by(follower_id=user.id).first() is not None
    
    def ping(self): 
        self.last_seen = datetime.utcnow() 
        db.session.add(self)
    
    def can(self, permissions): 
        return self.role is not None and (self.role.permissions & permissions) == permissions 
    
    def is_administrator(self): 
        return self.can(Permission.ADMINISTER) 
    
    def gravatar(self, size=100, default='identicon', rating='g'): 
        if request.is_secure: 
            url = 'https://secure.gravatar.com/avatar' 
        else: 
            url = 'http://www.gravatar.com/avatar' 
        
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest() 
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

    def change_email(self, new_email): 
        self.email = new_email 
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest() 
        db.session.add(self) 
        db.session.commit() 
        return True 

    @property 
    def password(self): 
        raise AttributeError('password is not a readable attribute') 

    @password.setter 
    def password(self, password): 
        self.password_hash = generate_password_hash(password) 

    def verify_password(self, password): 
        return check_password_hash(self.password_hash, password) 

    def __repr__(self): 
        return '<User %r>' % self.username

class Post(db.Model): 
    __tablename__ = 'posts' 
    id = db.Column(db.Integer, primary_key=True) 
    body = db.Column(db.Text) 
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) 
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    body_html = db.Column(db.Text) 

    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod 
    def on_changed_body(target, value, oldvalue, initiator): 
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p'] 
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True)) 

class Comment(db.Model): 
    __tablename__ = 'comments' 
    id = db.Column(db.Integer, primary_key=True) 
    body = db.Column(db.Text) 
    body_html = db.Column(db.Text) 
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) 
    disabled = db.Column(db.Boolean, default=False) 
    author_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id')) 
    
    @staticmethod 
    def on_changed_body(target, value, oldvalue, initiator): 
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong'] 
        target.body_html = bleach.linkify(bleach.clean( markdown(value, output_format='html'), tags=allowed_tags, strip=True)) 

class AnonymousUser(AnonymousUserMixin): 
    def can(self, permissions): 
        return False 
    def is_administrator(self): 
        return False

db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Comment.body, 'set', Comment.on_changed_body)