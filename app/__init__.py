from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_admin import Admin


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


from app.models.models import User, Event, Ticket
from app.views.views import CustomUser, CustomTicket, CustomEvent

admin = Admin(app, name="AdminUser", template_mode='bootstrap3')
admin.add_view(CustomUser(User, db.session, name='Users'))
admin.add_view(CustomEvent(Event, db.session, name='Events', endpoint='events_admin'))
admin.add_view(CustomTicket(Ticket, db.session, name='Tickets'))


from app.routes.user import user_blueprint
from app.routes.event import event_blueprint

app.register_blueprint(user_blueprint)
app.register_blueprint(event_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
