from fastapi import FastAPI
from sqladmin import Admin
from .views import UserProfileAdmin, PredictAdmin
from phone_app.db.database import engine


def setup_admin(app: FastAPI):
    admin = Admin(app, engine)
    admin.add_view(UserProfileAdmin)
    admin.add_view(PredictAdmin)     
