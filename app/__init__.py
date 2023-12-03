from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# creating an app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/LABAP'

# db initialization
db = SQLAlchemy(app)


# Starting up the project
if __name__ == '__main__':
    app.run(debug=True)

from app.routes.user import user_blueprint
app.register_blueprint(user_blueprint)
