
from flask import current_app as app, request, jsonify, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from flask_security import auth_required, current_user
from flask_security.utils import logout_user

from application.database import db
from application.models import *



@app.route('/user-login', methods=['POST'])
def user_login():
    data = request.get_json() #request-> http request body, get_json()-> converts incoming json body to python dict
    email = data.get('email') #data-> dict
    password = data.get('password')
    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    #compares(stored hash password during registration ,pwd entered by user during login)
    if not user or not check_password_hash(user.password, password): 
        return jsonify({"message": "Invalid credentials"}), 400

    if not user.active:
        return jsonify({"message": "Your account has been deactivated or blacklisted."}), 403

    role = user.roles[0].name  #if user.roles else 'student'

    if role == 'company':
        company = Company.query.filter_by(user_id=user.id).first()
        if company and company.approval_status != 'Approved':
            return jsonify({
                "message": f"Login denied. Your company account status is currently: {company.approval_status}."
            }), 403

    token = user.get_auth_token()

    return jsonify({
        "token": token,
        "role": role,
        "user_id": user.id,
        "message": "Login successful"
    }), 200



@app.route('/user-logout', methods=['POST']) 
@auth_required('token', 'session')
def user_logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200


# For search functionality
def make_raw(text):
    if not text:
        return ""
    split_list = text.split()
    search_word = ""
    for word in split_list: #split first name and last name 
        search_word += word.lower()
    return search_word


@app.route('/register', methods=['POST']) 
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not email or not password or not role:
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    if role not in ['student', 'company']:
        return jsonify({"message": "Invalid role specified"}), 400

    user_datastore = app.security.datastore
    new_user = user_datastore.create_user( email=email, password=generate_password_hash(password),roles=[role], active=True)
    db.session.flush()

    if role == 'student':
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        raw_name = make_raw(f"{first_name} {last_name}")
        student_profile = Student(
            user_id=new_user.id,
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            branch=data.get('branch'),
            cgpa=data.get('cgpa'),
            search_student_name=raw_name
        )
        db.session.add(student_profile)
        
    elif role == 'company':
        comp_name = data.get('company_name', '')
        raw_comp_name = make_raw(comp_name)
        company_profile = Company(
            user_id=new_user.id,
            company_name=data.get('company_name', ''),
            hr_contact=data.get('hr_contact', ''),
            description=data.get('description', ''),         
            approval_status='Pending',
            search_company_name=raw_comp_name
        )
        db.session.add(company_profile)
    db.session.commit()
    
    return jsonify({"message": "Registration Successfull"}), 201



#To catch all components in single page 
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_vue_app(path):
    return render_template('index.html')



@app.route('/api/admin/dashboard', methods=['GET'])
@auth_required('token')
def get_admin_dashboard():
    if not current_user.has_role('admin'):
        return jsonify({"message": "Unauthorized"}), 403
    return jsonify({
        "total_students": Student.query.count(),
        "total_companies": Company.query.count(),
        "total_drives": PlacementDrive.query.count()
    }), 200


@app.route('/api/companies', methods=['GET'])
@app.route('/api/companies/<int:id>', methods=['GET'])
@auth_required('token')
def get_companies(id=None):
    # Get specific company
    if id: 
        company = Company.query.get(id)
        if not company:
            return jsonify({"message": "Company not found"}), 404
        return jsonify({
            "id": company.id,
            "company_name": company.company_name,
            "hr_contact": company.hr_contact,
            "description": company.description,
            "approval_status": company.approval_status
        }), 200
    
    # Get searched company
    search_query = request.args.get('search_word')
    if search_query:
        raw_search = make_raw(search_query)
        companies = Company.query.filter(Company.search_company_name.like(f'%{raw_search}%')).all()
    
    # Get all companies
    else:
        companies = Company.query.all()

    result = []
    for c in companies:
        user = User.query.get(c.user_id)
        result.append({
            "id": c.id,
            "company_name": c.company_name,
            "approval_status": c.approval_status,
            "active": user.active if user else False,
        })
    return jsonify(result), 200


@app.route('/api/companies/<int:id>', methods=['PUT'])
@auth_required('token')
def update_company(id):
    company = Company.query.get(id)
    if not company: return jsonify({"message": "Company not found"}), 404
    data = request.get_json() or {}

    #Admin update company details (active,approval_status)
    if current_user.has_role('admin'):
        if 'approval_status' in data: company.approval_status = data['approval_status']
        if 'active' in data and data['active'] is not None:
            user = User.query.get(company.user_id)
            if user: user.active = data['active']
        db.session.commit()
        return jsonify({"message": "Company status updated by Admin"}), 200

    #Company update their own profile
    if current_user.has_role('company') and company.user_id == current_user.id:
        if 'description' in data: company.description = data['description']
        if 'hr_contact' in data: company.hr_contact = data['hr_contact']
        db.session.commit()
        return jsonify({"message": "Company profile updated successfully"}), 200

    return jsonify({"message": "Unauthorized action"}), 403


@app.route('/api/students', methods=['GET'])
@app.route('/api/students/<int:id>', methods=['GET'])
@auth_required('token')
def get_students(id=None):
    if id:
        student = Student.query.get(id)
        if not student: return jsonify({"message": "Student not found"}), 404
        user = User.query.get(student.user_id)
        return jsonify({
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "resume_file": student.resume_file,
            "email": user.email if user else "",
            "active": user.active if user else False
        }), 200

    search_query = request.args.get('search_word')
    if search_query:
        raw_search = make_raw(search_query)
        students = Student.query.filter(Student.search_student_name.like(f'%{raw_search}%')).all()
    else:
        students = Student.query.all()

    result = []
    for s in students:
        user = User.query.get(s.user_id)
        result.append({
            "id": s.id,
            "user_id": s.user_id,
            "first_name": s.first_name,
            "last_name": s.last_name,
            "branch": s.branch,
            "active": user.active if user else False
        })
    return jsonify(result), 200


@app.route('/api/students/<int:id>', methods=['PUT'])
@auth_required('token')
def update_student(id):
    student = Student.query.get(id)
    if not student: return jsonify({"message": "Student not found"}), 404
    data = request.get_json() or {}

    if current_user.has_role('admin'):
        if 'active' in data and data['active'] is not None:
            user = User.query.get(student.user_id)
            if user: user.active = data['active']
            db.session.commit()
            return jsonify({"message": "Student status updated by Admin"}), 200

    if current_user.has_role('student') and student.user_id == current_user.id:
        if 'first_name' in data: student.first_name = data['first_name']
        if 'last_name' in data: student.last_name = data['last_name']
        if 'branch' in data: student.branch = data['branch']
        if 'cgpa' in data: student.cgpa = data['cgpa']
        db.session.commit()
        return jsonify({"message": "Student profile updated successfully"}), 200

    return jsonify({"message": "Unauthorized action"}), 403

