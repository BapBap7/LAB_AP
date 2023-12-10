from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# creating an app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/LABAP'
app.config['SECRET_KEY'] = 'secret_key_for_lab'
# db initialization
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def home():
    return render_template('index.html')


from app.models.models import User


class CustomAdminModelView(ModelView):
    def is_accessible(self):
        # Check if the current user is authenticated and is an admin
        return current_user and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # Redirect non-admin users to the login page
        return redirect(url_for('user_blueprint.login'))


admin = Admin(app, name="AdminUser", template_mode='bootstrap3')
admin.add_view(CustomAdminModelView(User, db.session, name='UserAdmin'))

from app.routes.user import user_blueprint
from app.routes.event import event_blueprint

app.register_blueprint(user_blueprint)
app.register_blueprint(event_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
