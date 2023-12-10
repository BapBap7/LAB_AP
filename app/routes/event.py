from flask import Blueprint, request, jsonify, render_template, url_for, redirect, flash
from app import db, login_required, current_user
from app.models.models import Event, Ticket


event_blueprint = Blueprint('event_blueprint', __name__)


@event_blueprint.route('/create-event', methods=['POST'])
def create_event():
    data = request.get_json()

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
    if not ticket or ticket.status != 'AVAILABLE':
        return jsonify({'message': 'Ticket not available'}), 404
    return render_template('wait_payment.html', selected_ticket_ids=[ticket.id])


