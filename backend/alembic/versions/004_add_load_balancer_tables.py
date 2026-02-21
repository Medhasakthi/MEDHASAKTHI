"""Add load balancer management tables

Revision ID: 004_load_balancer
Revises: 003_business_intelligence
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_load_balancer'
down_revision = '003_business_intelligence'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create servers table
    op.create_table('servers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hostname', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('server_type', sa.String(length=50), nullable=False),
        sa.Column('weight', sa.Integer(), nullable=True, default=1),
        sa.Column('max_fails', sa.Integer(), nullable=True, default=3),
        sa.Column('fail_timeout', sa.Integer(), nullable=True, default=30),
        sa.Column('status', sa.String(length=20), nullable=True, default='active'),
        sa.Column('region', sa.String(length=50), nullable=True),
        sa.Column('availability_zone', sa.String(length=50), nullable=True),
        sa.Column('instance_type', sa.String(length=50), nullable=True),
        sa.Column('cpu_cores', sa.Integer(), nullable=True),
        sa.Column('memory_gb', sa.Integer(), nullable=True),
        sa.Column('storage_gb', sa.Integer(), nullable=True),
        sa.Column('health_check_path', sa.String(length=255), nullable=True, default='/health'),
        sa.Column('health_check_interval', sa.Integer(), nullable=True, default=30),
        sa.Column('health_check_timeout', sa.Integer(), nullable=True, default=5),
        sa.Column('ssl_enabled', sa.Boolean(), nullable=True, default=False),
        sa.Column('ssl_cert_path', sa.String(length=500), nullable=True),
        sa.Column('ssl_key_path', sa.String(length=500), nullable=True),
        sa.Column('last_health_check', sa.DateTime(), nullable=True),
        sa.Column('health_status', sa.String(length=20), nullable=True, default='unknown'),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True, default=0),
        sa.Column('success_count', sa.Integer(), nullable=True, default=0),
        sa.Column('added_by', sa.Integer(), nullable=True),
        sa.Column('added_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('removed_by', sa.Integer(), nullable=True),
        sa.Column('removed_at', sa.DateTime(), nullable=True),
        sa.Column('configuration', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['added_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['removed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_servers_hostname'), 'servers', ['hostname'], unique=False)
    op.create_index(op.f('ix_servers_id'), 'servers', ['id'], unique=False)
    op.create_index(op.f('ix_servers_server_type'), 'servers', ['server_type'], unique=False)
    op.create_index(op.f('ix_servers_status'), 'servers', ['status'], unique=False)

    # Create server_metrics table
    op.create_table('server_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('server_id', sa.Integer(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=True),
        sa.Column('cpu_usage_percent', sa.Integer(), nullable=True),
        sa.Column('memory_usage_percent', sa.Integer(), nullable=True),
        sa.Column('disk_usage_percent', sa.Integer(), nullable=True),
        sa.Column('network_in_mbps', sa.Integer(), nullable=True),
        sa.Column('network_out_mbps', sa.Integer(), nullable=True),
        sa.Column('active_connections', sa.Integer(), nullable=True),
        sa.Column('requests_per_second', sa.Integer(), nullable=True),
        sa.Column('response_time_avg_ms', sa.Integer(), nullable=True),
        sa.Column('error_rate_percent', sa.Integer(), nullable=True),
        sa.Column('requests_handled', sa.Integer(), nullable=True, default=0),
        sa.Column('bytes_transferred', sa.Integer(), nullable=True, default=0),
        sa.ForeignKeyConstraint(['server_id'], ['servers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_server_metrics_id'), 'server_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_server_metrics_recorded_at'), 'server_metrics', ['recorded_at'], unique=False)

    # Create load_balancer_config table
    op.create_table('load_balancer_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('algorithm', sa.String(length=50), nullable=True, default='least_conn'),
        sa.Column('health_check_enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('health_check_interval', sa.Integer(), nullable=True, default=30),
        sa.Column('health_check_timeout', sa.Integer(), nullable=True, default=5),
        sa.Column('health_check_retries', sa.Integer(), nullable=True, default=3),
        sa.Column('session_persistence', sa.Boolean(), nullable=True, default=False),
        sa.Column('session_timeout', sa.Integer(), nullable=True, default=3600),
        sa.Column('ssl_termination', sa.Boolean(), nullable=True, default=True),
        sa.Column('ssl_redirect', sa.Boolean(), nullable=True, default=True),
        sa.Column('rate_limit_enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('rate_limit_requests', sa.Integer(), nullable=True, default=100),
        sa.Column('rate_limit_window', sa.Integer(), nullable=True, default=60),
        sa.Column('connect_timeout', sa.Integer(), nullable=True, default=5),
        sa.Column('send_timeout', sa.Integer(), nullable=True, default=60),
        sa.Column('read_timeout', sa.Integer(), nullable=True, default=60),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_load_balancer_config_id'), 'load_balancer_config', ['id'], unique=False)

    # Insert default load balancer configuration
    op.execute("""
        INSERT INTO load_balancer_config (
            name, description, algorithm, health_check_enabled, health_check_interval,
            health_check_timeout, rate_limit_enabled, rate_limit_requests, rate_limit_window,
            connect_timeout, send_timeout, read_timeout, is_active, created_at, updated_at
        ) VALUES (
            'default', 'Default load balancer configuration', 'least_conn', true, 30,
            5, true, 100, 60, 5, 60, 60, true, NOW(), NOW()
        )
    """)

    # Insert initial backend servers (if running in single server mode)
    # Only insert if no servers exist to avoid conflicts on re-runs
    op.execute("""
        INSERT INTO servers (
            hostname, ip_address, port, server_type, weight, max_fails, fail_timeout,
            status, health_status, added_at, updated_at
        )
        SELECT * FROM (
            SELECT 'medhasakthi-backend-1' as hostname, '127.0.0.1' as ip_address, 8000 as port,
                   'backend' as server_type, 1 as weight, 3 as max_fails, 30 as fail_timeout,
                   'active' as status, 'unknown' as health_status, NOW() as added_at, NOW() as updated_at
            UNION ALL
            SELECT 'medhasakthi-frontend-1', '127.0.0.1', 3000, 'frontend', 1, 3, 30,
                   'active', 'unknown', NOW(), NOW()
        ) AS tmp
        WHERE NOT EXISTS (SELECT 1 FROM servers LIMIT 1)
    """)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_load_balancer_config_id'), table_name='load_balancer_config')
    op.drop_table('load_balancer_config')
    
    op.drop_index(op.f('ix_server_metrics_recorded_at'), table_name='server_metrics')
    op.drop_index(op.f('ix_server_metrics_id'), table_name='server_metrics')
    op.drop_table('server_metrics')
    
    op.drop_index(op.f('ix_servers_status'), table_name='servers')
    op.drop_index(op.f('ix_servers_server_type'), table_name='servers')
    op.drop_index(op.f('ix_servers_id'), table_name='servers')
    op.drop_index(op.f('ix_servers_hostname'), table_name='servers')
    op.drop_table('servers')
