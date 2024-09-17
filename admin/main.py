from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from config import DB_CONNECT

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONNECT
  # Замените на свои данные
db = SQLAlchemy(app)

# Импортируйте ваши модели
from models.models import *

admin = Admin(app, name='My Admin', template_mode='bootstrap3')
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Rating,
 db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Store, db.session))
admin.add_view(ModelView(StoreEmail,
 db.session))
admin.add_view(ModelView(StorePhoneNumber, db.session))
admin.add_view(ModelView(Region, db.session))

if __name__ == '__main__':
    app.run(debug=True)