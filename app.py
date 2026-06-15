from flask import Flask
from application.database import db
from application.models import *
from application.config import LocalDevelopmentConfig
from flask_security import Security, SQLAlchemyUserDatastore
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    
    db.init_app(app)
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore)
    
    app.app_context().push()
    return app

app = create_app()


with app.app_context():
    db.create_all()
    app.security.datastore.find_or_create_role(name="admin", description="Administrator")
    app.security.datastore.find_or_create_role(name="company", description="Companies")
    app.security.datastore.find_or_create_role(name="student", description="Students")
    
    db.session.commit()

    #Admin Creation
    if not app.security.datastore.find_user(email="admin@gmail.com"):
        app.security.datastore.create_user(
            email="admin@gmail.com",
            username="admin",
            password=generate_password_hash("1234"),
            roles=['admin'],
            active=True
        )     
    db.session.commit()

from application.routes import *
if __name__ == "__main__":
    app.run()