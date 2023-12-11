# tests/test_user_routes.py

from flask import url_for
from flask_testing import TestCase
from app import app, db
from app.models.models import Event, Ticket
from app.config import TestConfig

# Suppress SQLAlchemy warning about Query.get() being deprecated


class TestUserRoutes(TestCase):
    def create_app(self):
        app.config.from_object(TestConfig)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()

    def test_register(self):
        # Perform a register request using the 'client'
        response = self.client.post(url_for('user_blueprint.register'), data=dict(
            username='newuser',
            password='newpassword',
            email='newuser@example.com'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_logout_unauthorized(self):
        # Perform a logout request using the 'client'
        response = self.client.get(url_for('user_blueprint.logout'), follow_redirects=True)

        self.assertEqual(response.status_code, 401)
        # Additional assertions for successful logout

    def test_unsuccessful_login(self):
        # Create a test client
        response = self.client.post('/login', data=dict(
            username='nonexistentuser',
            password='wrongpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 400)

    def test_nonexisting_url(self):
        response = self.client.post('/nonexist')

        self.assertEqual(response.status_code, 404)

    def test_create_event(self):
        response = self.client.post(url_for('event_blueprint.create_event'),
                                    json={
                                        'event_name': 'title',
                                        'event_description': 'description',
                                        'total_tickets': 5
                                    })

        event = Event.query.filter_by(event_name='title').first()
        Ticket.query.filter_by(event_id=event.id).delete()
        db.session.delete(event)
        db.session.commit()

        self.assertEqual(response.status_code, 201)

    def test_get_event(self):
        self.client.post(url_for('event_blueprint.create_event'),
                         json={
                             'event_name': 'title',
                             'event_description': 'description',
                             'total_tickets': 5
                         })

        event = Event.query.filter_by(event_name='title').first()
        response = self.client.get(url_for('event_blueprint.get_event', event_id=event.id))
        Ticket.query.filter_by(event_id=event.id).delete()
        db.session.delete(event)
        db.session.commit()

        self.assertEqual(response.status_code, 200)

    # ===========================================

    def test_show_events(self):
        # Perform a request to retrieve all events
        response = self.client.get(url_for('event_blueprint.show_events'))

        self.assertEqual(response.status_code, 200)

    def test_get_nonexist_event_details(self):
        # Assuming there's an existing event with id=1
        event_id = 1
        response = self.client.get(url_for('event_blueprint.get_event', event_id=event_id))

        self.assertEqual(response.status_code, 404)  # Assuming the response contains a JSON with 'event' key

    def test_book_ticket(self):
        # Assuming there's an available ticket with id=1
        response = self.client.post(url_for('event_blueprint.book_ticket', ticket_id=1))

        self.assertEqual(response.status_code, 401)  # Assuming the response contains a JSON with 'message' key

    def test_unbook_ticket_unauthorized(self):
        # Assuming there's a booked ticket with id=1
        response = self.client.post(url_for('event_blueprint.unbook_ticket', ticket_id=1))

        self.assertEqual(response.status_code, 401)

    def test_dashboard_unauthenticated(self):
        # Assuming the user is not logged in
        response = self.client.get(url_for('user_blueprint.dashboard'))

        self.assertEqual(response.status_code, 401)

    def test_payment_unauthorized(self):
        # Assuming there are selected ticket ids for payment
        response = self.client.post(url_for('user_blueprint.payment'), data={'selected_ticket_ids': '1,2,3'})

        self.assertEqual(response.status_code, 401)  # Assuming a redirect status code
