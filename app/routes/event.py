from flask import Blueprint, request, jsonify, render_template, url_for, redirect, flash
from app import db, login_required, current_user, api, fields
from app.models.models import Event, Ticket
from flask_restx import Resource


event_blueprint = Blueprint('event_blueprint', __name__)


@event_blueprint.route('/create-event', methods=['POST'])
def create_event():
    data = request.get_json()

    if current_user.is_authenticated and current_user.is_admin:
        event_name = data.get('event_name')
        event_description = data.get('event_description')
        total_tickets = data.get('total_tickets')

        new_event = Event(event_name=event_name, event_description=event_description, total_tickets=total_tickets)
        tickets = [Ticket(user_id=None, event=new_event, status='AVAILABLE') for _ in range(total_tickets)]

        try:
            # Add the event and tickets to the database
            db.session.add(new_event)
            db.session.add_all(tickets)
            db.session.commit()

            return jsonify({'message': f'Event "{str(event_name)}" created successfully'}), 201
        except Exception as e:
            # Rollback the transaction if an error occurs
            db.session.rollback()
            return jsonify({'message': f'Error creating event: {str(e)}'}), 500
    else:
        return jsonify({'message': 'Forbidden'}), 403

@event_blueprint.route('/events', methods=['GET'])
def show_events():
    event_id = request.args.get('event_id')

    if event_id:
        # If event_id is provided, retrieve details for a specific event
        event = Event.query.get(event_id)
        if event:
            return redirect(url_for('event_blueprint.get_event', event_id=event_id))
        else:
            return jsonify({'message': 'Event not found'}), 404
    else:
        # If no event_id provided, retrieve all events
        events = Event.query.all()
        return render_template('events.html', events=events)


@event_blueprint.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get(event_id)

    if not event:
        return jsonify({'message': 'Event not found'}), 404

    tickets = Ticket.query.filter_by(event_id=event_id).all()

    return render_template('event_details.html', event=event, tickets=tickets)


# Book ticket
@event_blueprint.route('/book-ticket/<int:ticket_id>', methods=['POST'])
@login_required  # Ensure the user is logged in to book a ticket
def book_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)

    if not ticket or ticket.status != 'AVAILABLE':
        return jsonify({'message': 'Ticket not available'}), 404

    # Update the ticket status to 'BOOKED' and set the booked_by_user_id to the current user's ID
    ticket.status = 'BOOKED'
    ticket.user_id = current_user.id

    try:
        db.session.commit()
        return jsonify({'message': 'Ticket booked successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error booking ticket: {str(e)}'}), 500


# Unbook ticket
@event_blueprint.route('/unbook-ticket/<int:ticket_id>', methods=['POST'])
@login_required  # Ensure the user is logged in to book a ticket
def unbook_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)

    if ticket.status != 'BOOKED':
        return jsonify({'message': 'Ticket not available to unbook'}), 404

    # Update the ticket status to 'BOOKED' and set the booked_by_user_id to the current user's ID
    ticket.status = 'AVAILABLE'
    ticket.user_id = None

    try:
        db.session.commit()
        return jsonify({'message': 'Ticket unbooked successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error unbooking ticket: {str(e)}'}), 500


# Buy ticket
@event_blueprint.route('/buy-ticket/<int:ticket_id>', methods=['POST'])
@login_required  # Ensure the user is logged in to book a ticket
def buy_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'message': 'Ticket not available'}), 404
    return render_template('wait_payment.html', selected_ticket_ids=[ticket.id])


# ===========================
# Swagger
# ===========================


event_ns = api.namespace('events', description='Event operations')

event_model = api.model('Event', {
    'event_name': fields.String(required=True, description='Name of the event'),
    'event_description': fields.String(required=True, description='Description of the event'),
    'total_tickets': fields.Integer(required=True, description='Total number of tickets'),
})

@event_ns.route('/create-event')
class CreateEvent(Resource):
    @api.expect(event_model, validate=True)
    @api.response(201, 'Event created successfully')
    @api.response(500, 'Error creating event')
    def post(self):
        """
        Create a new event.
        """
        data = api.payload  # Use api.payload to get the JSON data from the request

        event_name = data.get('event_name')
        event_description = data.get('event_description')
        total_tickets = data.get('total_tickets')

        new_event = Event(event_name=event_name, event_description=event_description, total_tickets=total_tickets)
        tickets = [Ticket(user_id=None, event=new_event, status='AVAILABLE') for _ in range(total_tickets)]

        try:
            # Add the event and tickets to the database
            db.session.add(new_event)
            db.session.add_all(tickets)
            db.session.commit()

            return {'message': f'Event "{str(event_name)}" created successfully'}, 201
        except Exception as e:
            # Rollback the transaction if an error occurs
            db.session.rollback()
            return {'message': f'Error creating event: {str(e)}'}, 500

# Define a data model for the ticket
ticket_model = api.model('Ticket', {
    'id': fields.Integer(description='Ticket ID'),
    'status': fields.String(description='Ticket status (e.g., AVAILABLE, BOOKED)'),
    'user_id': fields.Integer(description='User ID who booked the ticket'),
})

# Endpoint to show events
@event_ns.route('/events')
class ShowEvents(Resource):
    @api.doc(params={'event_id': 'Optional. If provided, retrieve details for a specific event.'})
    @api.marshal_list_with(ticket_model)
    def get(self):
        """
        Retrieve all events or details for a specific event.
        """
        event_id = request.args.get('event_id')

        if event_id:
            event = Event.query.get(event_id)
            if event:
                return redirect(url_for('event_blueprint.get_event', event_id=event_id))
            else:
                return {'message': 'Event not found'}, 404
        else:
            events = Event.query.all()
            return {'events': events}

# Endpoint to get details for a specific event
@event_ns.route('/events/<int:event_id>')
class GetEvent(Resource):
    @api.response(404, 'Event not found')
    @api.marshal_with(ticket_model)
    def get(self, event_id):
        """
        Retrieve details for a specific event.
        """
        event = Event.query.get(event_id)

        if not event:
            return {'message': 'Event not found'}, 404

        tickets = Ticket.query.filter_by(event_id=event_id).all()
        return {'event': event, 'tickets': tickets}

# Endpoint to book a ticket
@event_ns.route('/book-ticket/<int:ticket_id>')
class BookTicket(Resource):
    @api.response(404, 'Ticket not available')
    @api.response(500, 'Error booking ticket')
    def post(self, ticket_id):
        """
        Book a ticket.
        """
        ticket = Ticket.query.get(ticket_id)

        if not ticket or ticket.status != 'AVAILABLE':
            return {'message': 'Ticket not available'}, 404

        ticket.status = 'BOOKED'
        ticket.user_id = current_user.id

        try:
            db.session.commit()
            return {'message': 'Ticket booked successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error booking ticket: {str(e)}'}, 500

# Endpoint to unbook a ticket
@event_ns.route('/unbook-ticket/<int:ticket_id>')
class UnbookTicket(Resource):
    @api.response(404, 'Ticket not available to unbook')
    @api.response(500, 'Error unbooking ticket')
    def post(self, ticket_id):
        """
        Unbook a ticket.
        """
        ticket = Ticket.query.get(ticket_id)

        if ticket.status != 'BOOKED':
            return {'message': 'Ticket not available to unbook'}, 404

        ticket.status = 'AVAILABLE'
        ticket.user_id = None

        try:
            db.session.commit()
            return {'message': 'Ticket unbooked successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error unbooking ticket: {str(e)}'}, 500

# Endpoint to buy a ticket
@event_ns.route('/buy-ticket/<int:ticket_id>')
class BuyTicket(Resource):
    @api.response(404, 'Ticket not available')
    @api.response(200, 'Render payment page')
    def post(self, ticket_id):
        """
        Buy a ticket.
        """
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return {'message': 'Ticket not available'}, 404
        return render_template('wait_payment.html', selected_ticket_ids=[ticket.id])