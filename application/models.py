from .database import db
from flask_security import UserMixin, RoleMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True, nullable=False)
    username = db.Column(db.String(), unique=True, nullable=True)
    password = db.Column(db.String(), nullable=False)
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(), unique=True, nullable=False)
    
    roles = db.relationship('Role', secondary='users_roles', backref='users')
    company_profile = db.relationship('Company', backref='user', uselist=False, cascade="all, delete")
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade="all, delete")


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), unique=True)
    description = db.Column(db.String())


class UsersRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id'))