import os
import csv
from celery import shared_task
from datetime import datetime
from application.mail import send_email
from application.models import *
from application.utils import format_report


# SEND DEADLINE REMINDER TO STUDENT'S MAIL ABOUT DRIVES
@shared_task(ignore_result=True)
def send_deadline_reminders():
    today = datetime.now().date()
    open_drives = PlacementDrive.query.filter(
        PlacementDrive.status == 'Approved',
        PlacementDrive.application_deadline >= today
    ).all()
    
    if not open_drives:
        return "No open drives found. Zero emails sent."

    users = User.query.filter(User.active == True).all()
    emails_sent = 0

    for user in users:
        if user.has_role('student'):
            student = Student.query.filter_by(user_id=user.id).first()
            if student:
                user_data = {}
                user_data['student_name'] = f"{student.first_name} {student.last_name}"
                user_data['email'] = user.email
                
                user_drives = []
                for drive in open_drives:
                    comp = Company.query.get(drive.company_id)
                    
                    this_drive = {}
                    this_drive["id"] = drive.id
                    this_drive["company_name"] = comp.company_name if comp else "Unknown"
                    this_drive["job_title"] = drive.job_title
                    this_drive["deadline"] = str(drive.application_deadline)
                    
                    user_drives.append(this_drive)
                
                user_data['drives'] = user_drives
                
                message = format_report('templates/deadline_reminder.html', user_data)
                
                send_email(
                    to_address=user.email, 
                    subject="Placement Drive Deadlines Overview", 
                    message=message,
                    content="html"
                )
                emails_sent += 1

    return f"Deadline reminders sent to {emails_sent} students."




# SEND MONTHLY REPORT TO ADMIN 
@shared_task(ignore_result=True)
def send_monthly_admin_report():
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count() 
    # total_selected = Application.query.filter(Application.status.in_(['Selected', 'Shortlisted', 'Accepted'])).count()
    total_selected = Application.query.filter(Application.status=='Selected').count()

    report_data = {
        "month_year": datetime.now().strftime("%B %Y"),
        "total_drives": total_drives,
        "total_applications": total_applications,
        "total_selected": total_selected
    }

    message = format_report('templates/admin_monthly_report.html', report_data)
    admin=User.has_role('admin')
    emails_sent = 0

    send_email(
        to_address=admin.email,
        subject=f"Institute Placement Report: {report_data['month_year']}",
        message=message,
        content="html"
    )
    emails_sent += 1

    return f"Monthly admin reports sent to {emails_sent} admins."


