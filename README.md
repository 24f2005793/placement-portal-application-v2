# Placement Portal Application (PPA) - V2 🎓

## Overview 

The **Placement Portal Application (PPA)** is a role-based web application developed to streamline campus recruitment activities for educational institutions. It enables seamless interaction between **Admin**, **Companies**, and **Students** through a centralized placement management system.

The application is built using **Flask** for the backend, **Vue.js** for the frontend, **SQLite** for the database, **Redis** for caching, and **Celery** for asynchronous and scheduled background tasks.

---

## Features

### Admin 👩‍💻
- Pre-created Admin login
- Approve or reject company registrations
- Approve or reject placement drives
- View and manage companies, students, and placement drives
- Blacklist companies or students
- Search companies, students, and placement drives

### Company 🏢
- Register and login after Admin approval
- Create and manage placement drives
- View applicants for each placement drive
- Shortlist candidates
- Update application status

### Student 🧑‍🎓
- Register and login
- Update profile and upload resume
- View approved placement drives
- Apply for eligible placement drives
- Track application status
- View placement history
- Export application history as CSV

---

## Additional Features 📌

- Role-Based Access Control (RBAC) using JWT
- RESTful API architecture
- Eligibility validation before applying
- Prevention of duplicate applications
- Redis caching for improved performance
- Celery-based asynchronous and scheduled tasks
- Responsive user interface

---

## Tech Stack ⚙️

| Category | Technology |
|----------|------------|
| Backend | Flask (Python) |
| Frontend | Vue.js |
| UI | HTML, CSS, JavaScript, Bootstrap |
| Database | SQLite |
| ORM | SQLAlchemy |
| Authentication | JWT (Flask-JWT-Extended) |
| Caching | Redis |
| Background Jobs | Celery |



---

