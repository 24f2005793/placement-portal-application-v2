
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



@app.route('/api/drives', methods=['GET'])
@app.route('/api/drives/<int:id>', methods=['GET'])
@auth_required('token')
def get_drives(id=None):
    if id:
        drive = PlacementDrive.query.get(id)
        if not drive: return jsonify({"message": "Drive not found"}), 404
        comp = Company.query.get(drive.company_id)
        return jsonify({
            "id": drive.id,
            "company_name": comp.company_name ,
            "job_title": drive.job_title,
            "job_description": drive.job_description,
            "job_salary": drive.job_salary,
            "job_location": drive.job_location,
            "eligibility_criteria": drive.eligibility_criteria,
            "application_deadline": str(drive.application_deadline),
            "status": drive.status
        }), 200

    search_query = request.args.get('search_word')
    company = None
    if current_user.has_role('company'):
        company = Company.query.filter_by(user_id=current_user.id).first()

    if search_query:
        raw_search = make_raw(search_query)
        #Show only those drives which the company has created
        if company:
            drives = PlacementDrive.query.filter(
                PlacementDrive.company_id == company.id,
                PlacementDrive.search_job_title.like(f'%{raw_search}%')
            ).all()
        else:
            drives = PlacementDrive.query.filter(
                PlacementDrive.search_job_title.like(f'%{raw_search}%')
            ).all()
    else:
        if company:
            drives = PlacementDrive.query.filter_by(company_id=company.id).all()
        else:
            drives = PlacementDrive.query.all()

    result = []
    for d in drives:
        comp = Company.query.get(d.company_id)
        result.append({
            "id": d.id,
            "company_id": d.company_id,
            "job_title": d.job_title,
            "job_location": d.job_location,
            "status": d.status,
            "application_deadline": str(d.application_deadline),
            "company_name": comp.company_name,
            "eligibility_criteria": d.eligibility_criteria
        })
    return jsonify(result), 200



@app.route('/api/drives', methods=['POST'])
@auth_required('token')
def create_drive():
    #Only approved companies can create drive
    if not current_user.has_role('company'): return jsonify({"message": "Only companies can create drives"}), 403

    company = Company.query.filter_by(user_id=current_user.id).first()
    if company.approval_status != 'Approved': return jsonify({"message": "Company not approved"}), 403

    data = request.get_json() or {}
    
    if not data.get('job_title'): return jsonify({"message": "Job title is required"}), 400
    if not data.get('job_description'): return jsonify({"message": "Job description is required"}), 400
    if not data.get('application_deadline'): return jsonify({"message": "Deadline is required (YYYY-MM-DD)"}), 400

    deadline = datetime.strptime(data['application_deadline'], '%Y-%m-%d').date()

    new_drive = PlacementDrive(
        company_id=company.id,
        job_title=data['job_title'],
        job_description=data['job_description'],
        job_salary=data.get('job_salary'),
        job_location=data.get('job_location'),
        eligibility_criteria=data.get('eligibility_criteria'),
        application_deadline=deadline,
        status='Pending',
        search_job_title=make_raw(data['job_title'])
    )

    db.session.add(new_drive)
    db.session.commit()
    return jsonify({"message": "Drive created successfully"}), 201



@app.route('/api/drives/<int:id>', methods=['PUT'])
@auth_required('token')
def update_drive(id):
    drive = PlacementDrive.query.get(id)
    if not drive: return jsonify({"message": "Drive not found"}), 404
    data = request.get_json() or {}

    if current_user.has_role('admin') and 'status' in data:
        drive.status = data['status']
        db.session.commit()
        return jsonify({"message": "Drive status updated by Admin"}), 200
        
    if current_user.has_role('company'):
        comp = Company.query.filter_by(user_id=current_user.id).first()
        if comp and drive.company_id == comp.id:
            if 'job_title' in data: 
                drive.job_title = data['job_title'] 
                drive.search_job_title = make_raw(data['job_title'])
            if 'status' in data: drive.status = data['status']
            if 'job_description' in data: drive.job_description = data['job_description']
            if 'job_salary' in data: drive.job_salary = data['job_salary']
            if 'job_location' in data: drive.job_location = data['job_location']
            if 'application_deadline' in data: 
                drive.application_deadline = datetime.strptime(data['application_deadline'], '%Y-%m-%d').date()
            db.session.commit()
            return jsonify({"message": "Drive details updated"}), 200

    return jsonify({"message": "Unauthorized action"}), 403



@app.route('/api/drives/<int:id>', methods=['DELETE'])
@auth_required('token')
def delete_drive(id):
    drive = PlacementDrive.query.get(id)
    if not drive: return jsonify({"message": "Drive not found"}), 404

    comp = Company.query.filter_by(user_id=current_user.id).first()
    if not comp or drive.company_id != comp.id: return jsonify({"message": "Unauthorized"}), 403
    #Only delete pending drives
    if drive.status not in ['Pending']: return jsonify({"message": "Cannot delete completed drive"}), 400

    db.session.delete(drive)
    db.session.commit()
    return jsonify({"message": "Drive deleted successfully"}), 200



@app.route('/api/applications', methods=['GET'])
@app.route('/api/applications/<int:id>', methods=['GET'])
@auth_required('token')
def get_applications(id=None):
    if id:
        apps=Application.query.filter_by(id=id).all()
    else:
        apps = Application.query.all()
    result = []
    for a in apps:
        student = Student.query.get(a.student_id)
        drive = PlacementDrive.query.get(a.drive_id)
        comp = Company.query.get(drive.company_id) if drive else None

        result.append({
            "id": a.id,
            "student_name": student.first_name + " " + student.last_name,
            "student_id": student.id,
            "drive_id": a.drive_id,
            "job_title": drive.job_title,
            "company_name": comp.company_name,
            "application_date": str(a.application_date),
            "status": a.status,
            "remark": a.remark,
            "interview_type": a.interview_type
        })
    return jsonify(result), 200


@app.route('/api/applications', methods=['POST'])
@auth_required('token')
def create_application():
    if not current_user.has_role('student'): return jsonify({"message": "Only students can apply"}), 403

    student = Student.query.filter_by(user_id=current_user.id).first()
    data = request.get_json() or {}
    
    drive = PlacementDrive.query.get(data['drive_id'])
    if not drive or drive.status != 'Approved': return jsonify({"message": "Invalid drive"}), 400

    new_application = Application(
        student_id=student.id,
        drive_id=drive.id,
        status='Applied'
    )
    db.session.add(new_application)
    db.session.commit()
    return jsonify({"message": "Application submitted successfully"}), 201



@app.route('/api/applications/<int:id>', methods=['PUT'])
@auth_required('token')
def update_application(id):
    app_record = Application.query.get(id)
    if not app_record: return jsonify({"message": "Application not found"}), 404

    data = request.get_json() or {}
    if 'status' in data and data['status'] != app_record.status:
        app_record.status = data['status']
    if 'remark' in data :
        app_record.remark = data['remark']

    db.session.commit()

    return jsonify({"message": "Application updated successfully"}), 200
