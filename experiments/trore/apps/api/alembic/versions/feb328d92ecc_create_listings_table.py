"""create_listings_table

Revision ID: feb328d92ecc
Revises: 
Create Date: 2026-02-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'feb328d92ecc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create extension for UUID generation
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Create Enum type
    listing_status = sa.Enum('DRAFT', 'AVAILABLE', 'RENTED', 'ARCHIVED', name='listing_status')
    listing_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'listings',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('area_sqm', sa.Float(), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('status', listing_status, nullable=True), # Nullable per schema description? "Default: DRAFT"? AC didn't specify default but it's common. AC says just Enum. I'll make it nullable=True or add default. AC says "status: Enum". I'll assume nullable=False if not specified but good practice is default 'DRAFT'. I'll stick to strict AC: "status: Enum". I will make it Nullable=True unless specified. Actually, "status: Enum" implies it exists. I will set nullable=True for now or False? AC lists columns. I'll guess False usually. Let's make it True to be safe or False? 
        # AC: "status: Enum ('DRAFT', ...)"
        # I'll make it nullable=True for safety unless required.
        # Wait, "price" says "(Not Null)". "status" does NOT say "(Not Null)". So nullable=True is correct interpretation.
        sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('price >= 0', name='check_price_positive'),
        sa.CheckConstraint('area_sqm > 0', name='check_area_positive')
    )


def downgrade() -> None:
    op.drop_table('listings')
    sa.Enum(name='listing_status').drop(op.get_bind(), checkfirst=True)
    # op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"') # Dangerous to drop extension in shared DB