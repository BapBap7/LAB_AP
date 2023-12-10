from app.models.models import Event, Ticket
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for
from app import db, current_user



class CustomUser(ModelView):
    column_list = ['id', 'username', 'email', 'is_admin']
    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('user_blueprint.dashboard'))


class CustomEvent(ModelView):
    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('user_blueprint.dashboard'))

    def create_model(self, form):
        try:
            event_name = form.event_name.data
            event_description = form.event_description.data
            total_tickets = int(form.total_tickets.data)

            new_event = Event(event_name=event_name, event_description=event_description, total_tickets=total_tickets)
            tickets = [Ticket(user_id=None, event=new_event, status='AVAILABLE') for _ in range(total_tickets)]

            db.session.add(new_event)
            db.session.add_all(tickets)
            db.session.commit()

            return redirect(url_for('events_admin.index_view'))
        except Exception as e:
            db.session.rollback()
            return redirect(url_for('events_admin.index_view'))


class CustomTicket(ModelView):
    column_list = ['id', 'status', 'user_id', 'event_id']

    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('user_blueprint.dashboard'))