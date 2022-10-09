"""add prediction model

Revision ID: f6ab8a88245a
Revises: 7f85dff1890c
Create Date: 2022-10-09 18:22:29.343131

"""
# pylint: disable=E1101

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f6ab8a88245a"
down_revision = "7f85dff1890c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("station_id", sa.Integer(), nullable=True),
        sa.Column("bike_availability_probability", sa.Float(), nullable=False),
        sa.Column("bike_eta", sa.Float(), nullable=False),
        sa.Column("user_eta", sa.Float(), nullable=False),
        sa.Column("user_lat", sa.Numeric(), nullable=False),
        sa.Column("user_lon", sa.Numeric(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["station_id"], ["stations.station_id"], name="stations_fk"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("stations_status") as batch_op:
        batch_op.create_foreign_key(
            "fk_stations_status_stations", "stations", ["station_id"], ["station_id"]
        )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("stations_status") as batch_op:
        batch_op.drop_constraint("fk_stations_status_stations", type_="foreignkey")
    op.drop_table("predictions")
    # ### end Alembic commands ###
