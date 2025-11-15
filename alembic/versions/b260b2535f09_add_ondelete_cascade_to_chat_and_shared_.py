"""add ondelete cascade to chat and shared post fks of the cols to avoid erros

Revision ID: b260b2535f09
Revises: 41c7b226f3fd
Create Date: 2025-11-15 19:26:52.680684

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b260b2535f09'
down_revision: Union[str, Sequence[str], None] = '41c7b226f3fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('shared_posts_from_user_id_fkey', 'shared_posts', type_='foreignkey')
    op.drop_constraint('shared_posts_to_user_id_fkey', 'shared_posts', type_='foreignkey')
    op.create_foreign_key(
        'shared_posts_from_user_id_fkey', 'shared_posts', 'users',
        ['from_user_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'shared_posts_to_user_id_fkey', 'shared_posts', 'users',
        ['to_user_id'], ['id'], ondelete='CASCADE'
    )

    # Message: sender_id, receiver_id
    op.drop_constraint('messages_sender_id_fkey', 'messages', type_='foreignkey')
    op.drop_constraint('messages_receiver_id_fkey', 'messages', type_='foreignkey')
    op.create_foreign_key(
        'messages_sender_id_fkey', 'messages', 'users',
        ['sender_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'messages_receiver_id_fkey', 'messages', 'users',
        ['receiver_id'], ['id'], ondelete='CASCADE'
    )

    # MessageReaction
    op.drop_constraint('message_reactions_message_id_fkey', 'message_reactions', type_='foreignkey')
    op.drop_constraint('message_reactions_user_id_fkey', 'message_reactions', type_='foreignkey')
    op.create_foreign_key(
        'message_reactions_message_id_fkey', 'message_reactions', 'messages',
        ['message_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'message_reactions_user_id_fkey', 'message_reactions', 'users',
        ['user_id'], ['id'], ondelete='CASCADE'
    )

    # SharedPostReaction
    op.drop_constraint('shared_post_reactions_user_id_fkey', 'shared_post_reactions', type_='foreignkey')
    op.create_foreign_key(
        'shared_post_reactions_user_id_fkey', 'shared_post_reactions', 'users',
        ['user_id'], ['id'], ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('shared_posts_from_user_id_fkey', 'shared_posts', type_='foreignkey')
    op.drop_constraint('shared_posts_to_user_id_fkey', 'shared_posts', type_='foreignkey')
    op.create_foreign_key('shared_posts_from_user_id_fkey', 'shared_posts', 'users', ['from_user_id'], ['id'])
    op.create_foreign_key('shared_posts_to_user_id_fkey', 'shared_posts', 'users', ['to_user_id'], ['id'])

    op.drop_constraint('messages_sender_id_fkey', 'messages', type_='foreignkey')
    op.drop_constraint('messages_receiver_id_fkey', 'messages', type_='foreignkey')
    op.create_foreign_key('messages_sender_id_fkey', 'messages', 'users', ['sender_id'], ['id'])
    op.create_foreign_key('messages_receiver_id_fkey', 'messages', 'users', ['receiver_id'], ['id'])

    op.drop_constraint('message_reactions_message_id_fkey', 'message_reactions', type_='foreignkey')
    op.drop_constraint('message_reactions_user_id_fkey', 'message_reactions', type_='foreignkey')
    op.create_foreign_key('message_reactions_message_id_fkey', 'message_reactions', 'messages', ['message_id'], ['id'])
    op.create_foreign_key('message_reactions_user_id_fkey', 'message_reactions', 'users', ['user_id'], ['id'])

    op.drop_constraint('shared_post_reactions_user_id_fkey', 'shared_post_reactions', type_='foreignkey')
    op.create_foreign_key('shared_post_reactions_user_id_fkey', 'shared_post_reactions', 'users', ['user_id'], ['id'])
