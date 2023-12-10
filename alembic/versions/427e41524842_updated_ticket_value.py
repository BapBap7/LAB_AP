"""updated_ticket_value

Revision ID: 427e41524842
Revises: 96f8b2ef693d
Create Date: 2023-12-10 01:07:03.753615

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '427e41524842'
down_revision: Union[str, None] = '96f8b2ef693d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('event_event_description_key', 'event', type_='unique')
    op.drop_constraint('event_total_tickets_key', 'event', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('event_total_tickets_key', 'event', ['total_tickets'])
    op.create_unique_constraint('event_event_description_key', 'event', ['event_description'])
    # ### end Alembic commands ###
