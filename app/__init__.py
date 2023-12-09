from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, login_required, logout_user, current_user


# creating an app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/LABAP'
app.config['SECRET_KEY'] = 'secret_key_for_lab'
# db initialization
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Starting up the project
if __name__ == '__main__':
    app.run(debug=True)


@app.route('/')
def home():
    return render_template('index.html')


from app.routes.user import user_blueprint
from app.routes.event import event_blueprint

app.register_blueprint(user_blueprint)

app.register_blueprint(event_blueprint)
