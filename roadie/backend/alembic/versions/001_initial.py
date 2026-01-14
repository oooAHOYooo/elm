"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Create drives table
    op.create_table(
        'drives',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('distance', sa.Float(), default=0.0),
        sa.Column('duration', sa.Integer(), default=0),
        sa.Column('average_speed', sa.Float(), default=0.0),
        sa.Column('max_speed', sa.Float(), default=0.0),
        sa.Column('start_location', Geography('POINT', srid=4326), nullable=True),
        sa.Column('end_location', Geography('POINT', srid=4326), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_drives_user_id', 'drives', ['user_id'])
    op.create_index('ix_drives_start_time', 'drives', ['start_time'])
    
    # Create route_points table
    op.create_table(
        'route_points',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('drive_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('drives.id'), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('altitude', sa.Float(), nullable=True),
        sa.Column('speed', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
    )
    op.create_index('ix_route_points_drive_id', 'route_points', ['drive_id'])
    op.create_index('ix_route_points_sequence', 'route_points', ['drive_id', 'sequence'])


def downgrade() -> None:
    op.drop_table('route_points')
    op.drop_table('drives')
    op.drop_table('users')
    op.execute('DROP EXTENSION IF EXISTS postgis')

