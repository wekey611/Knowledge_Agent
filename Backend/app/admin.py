from sqladmin import Admin, ModelView
from app import models
from app.core.database import engine

class UserAdmin(ModelView, model=models.user.User):
    column_list = [models.user.User.id, models.user.User.email, models.user.User.role]