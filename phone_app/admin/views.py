from sqladmin import ModelView
from phone_app.db.models import UserProfile, Phone


class UserProfileAdmin(ModelView, model=UserProfile):
    column_list = [UserProfile.id, UserProfile.username]
    name = 'User'
    name_plural = 'Users'


class PredictAdmin(ModelView, model=Phone):
    column_list = [Phone.id, Phone.rating]
    name = 'Phone'
    name_plural = 'Phones'
