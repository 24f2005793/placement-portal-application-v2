from .database import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime


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


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(), nullable=False)
    search_company_name = db.Column(db.String())
    description = db.Column(db.Text, nullable=True)
    hr_contact = db.Column(db.String(), nullable=False)
    approval_status = db.Column(db.String(), default='Pending') # pending / approved /rejected

    drives = db.relationship('PlacementDrive', backref='company', cascade="all, delete")


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    search_student_name = db.Column(db.String())
    branch = db.Column(db.String(), nullable=True)
    cgpa = db.Column(db.Float, nullable=True)
    resume_file = db.Column(db.String(), nullable=True)

    applications = db.relationship('Application', backref='student', cascade="all, delete")


class PlacementDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    job_title = db.Column(db.String(), nullable=False)
    search_job_title = db.Column(db.String())
    job_description = db.Column(db.Text, nullable=False)
    job_salary = db.Column(db.Integer, nullable=True)       
    job_location = db.Column(db.String(), nullable=True) 
    eligibility_criteria = db.Column(db.String(), nullable=True)
    drive_date = db.Column(db.Date, default=datetime.utcnow)
    application_deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(), default='Pending') # pending / approved /rejected

    applications = db.relationship('Application', backref='drive',cascade="all, delete")


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    application_date = db.Column(db.Date, default=datetime.utcnow)
    interview_type = db.Column(db.String(), nullable=True) 
    remark = db.Column(db.String(), nullable=True)        
    status = db.Column(db.String(), default='Applied') # Applied / Shortlisted / Selected / Rejected