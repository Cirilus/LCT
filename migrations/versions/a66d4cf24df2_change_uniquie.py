"""change_uniquie

Revision ID: a66d4cf24df2
Revises: ab9dec71acf3
Create Date: 2023-11-10 21:55:17.399935

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a66d4cf24df2'
down_revision: Union[str, None] = 'ab9dec71acf3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('minio_storage_name_key', 'minio_storage', type_='unique')
    op.create_unique_constraint(None, 'minio_storage', ['path'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'minio_storage', type_='unique')
    op.create_unique_constraint('minio_storage_name_key', 'minio_storage', ['name'])
    # ### end Alembic commands ###
