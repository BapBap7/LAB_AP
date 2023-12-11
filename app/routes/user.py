from flask import Blueprint, request, jsonify, url_for, render_template, redirect
from flask_bcrypt import Bcrypt
from app import db, login_manager, login_required, login_user, logout_user, current_user, app, fields, api, Resource
from app.models.models import User, LoginForm, RegistrationForm, Ticket


user_blueprint = Blueprint('user_blueprint', __name__)
bcrypt = Bcrypt()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@user_blueprint.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # Fetch the user's booked tickets
    user_tickets = Ticket.query.filter_by(user_id=current_user.id).all()

    return render_template('dashboard.html', user_tickets=user_tickets)


@user_blueprint.route('/buy-tickets', methods=['POST'])
@login_required
def buy_tickets():
    selected_ticket_ids = request.form.getlist('selected_tickets')
    return render_template('wait_payment.html', selected_ticket_ids=selected_ticket_ids)


@user_blueprint.route('/payment', methods=['POST'])
@login_required
def payment():
    selected_ticket_ids = request.form.get('selected_ticket_ids').split(',')
    # Perform the purchase logic for the selected tickets (update status, etc.)
    for ticket_id in selected_ticket_ids:
        ticket = Ticket.query.get(ticket_id)
        if ticket:
            ticket.status = 'BOUGHT'
            ticket.user_id = current_user.id
            # Perform other purchase-related logic as needed
            db.session.commit()

    return redirect(url_for('user_blueprint.dashboard'))


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('user_blueprint.dashboard')), 302
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('user_blueprint.dashboard')), 302
    return render_template('login.html', form=form), 400


@user_blueprint.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_blueprint.login'))


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('user_blueprint.dashboard')), 302
    try:
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(email=form.email.data, username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('user_blueprint.login'))
    except Exception as e:
        return str(e), 404

    return render_template('register.html', form=form)


# =====================
# Swagger
# =====================


user_ns = api.namespace('users', description='User operations')

# Define a data model for the user
user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'username': fields.String(description='Username'),
    'email': fields.String(description='Email'),
    # ... (Add more fields as needed)
})


@user_ns.route('/dashboard')
class Dashboard(Resource):
    @api.marshal_list_with(user_model)
    @api.response(401, 'Unauthorized')
    def get(self):
        """
        Fetch the user's booked tickets.
        """
        user_tickets = Ticket.query.filter_by(user_id=current_user.id).all()
        return {'user_tickets': user_tickets}


@user_ns.route('/buy-tickets')
class BuyTickets(Resource):
    @api.expect(api.parser().add_argument('selected_tickets', type=int, action='append', required=True))
    @api.response(401, 'Unauthorized')
    def post(self):
        """
        Buy tickets.
        """
        selected_ticket_ids = api.payload['selected_tickets']
        return {'selected_ticket_ids': selected_ticket_ids}


@user_ns.route('/payment')
class Payment(Resource):
    @api.expect(api.parser().add_argument('selected_ticket_ids', type=str, required=True))
    @api.response(401, 'Unauthorized')
    def post(self):

        selected_ticket_ids = api.payload['selected_ticket_ids'].split(',')
        # Perform the purchase logic for the selected tickets (update status, etc.)
        for ticket_id in selected_ticket_ids:
            ticket = Ticket.query.get(ticket_id)
            if ticket:
                ticket.status = 'BOUGHT'
                ticket.user_id = current_user.id
                # Perform other purchase-related logic as needed
                db.session.commit()

        return {'message': 'Payment successful'}


@user_ns.route('/login')
class Login(Resource):
    @api.expect(api.model('Login', {
        'username': fields.String(required=True, description='Username'),
        'password': fields.String(required=True, description='Password'),
    }))
    def post(self):
        """
        Log in.
        """

        data = api.payload
        username = data.get('username')
        password = data.get('password')

        form = LoginForm(data={'username': username, 'password': password})

        if current_user.is_authenticated:
            return {'message': 'Already authorized'}, 400
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            return {'message': 'Not Found'}, 404
        if bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return {'message': 'Success login'}, 200
        return {'message': 'Bad request'}, 400


@user_ns.route('/logout')
class Logout(Resource):
    @api.response(401, 'Unauthorized')
    def post(self):
        if current_user.is_authenticated:
            logout_user()
            return {'message': 'Logged out successfully'}, 200
        return {'message': 'Unauthorized'}, 401


@user_ns.route('/register')
class Register(Resource):
    @api.expect(api.model('Login', {
        'username': fields.String(required=True, description='Username'),
        'password': fields.String(required=True, description='Password'),
        'email': fields.String(required=True, description='Email')
    }))
    def post(self):

        data = api.payload
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        form = RegistrationForm(data={'username': username, 'password': password, 'email': email})
        if current_user.is_authenticated:
            return {'message': 'Already authorized'}, 400
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(email=form.email.data, username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return {'message': 'Successfully registered'}, 200
        except Exception as e:
            return {'message': 'Email or username is already taken'}, 400