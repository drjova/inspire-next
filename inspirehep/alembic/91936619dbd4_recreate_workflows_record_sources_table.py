#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Recreate workflows_record_sources table"""

import enum
import sqlalchemy as sa

from alembic import op
from datetime import datetime
from sqlalchemy.dialects import mysql, postgresql
from sqlalchemy_utils.types import JSONType, UUIDType


# revision identifiers, used by Alembic.
revision = '91936619dbd4'
down_revision = '402af3fbf68b'
branch_labels = ()
depends_on = None


class SourceEnum(enum.IntEnum):
    arxiv = 1
    submitter = 2
    publisher = 3


def upgrade():
    """Upgrade database."""
    op.drop_table('workflows_record_sources')
    op.create_table(
        'workflows_record_sources',
        sa.Column(
            'record_id',
            UUIDType,
            sa.ForeignKey('records_metadata.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'source',
            sa.Enum(SourceEnum),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('record_id', 'source'),
        sa.Column(
            'created',
            sa.DateTime(),
            default=datetime.utcnow,
            nullable=False
        ),
        sa.Column(
            'updated',
            sa.DateTime(),
            default=datetime.utcnow,
            nullable=False
        ),
        sa.Column(
            'json',
            postgresql.JSONB(),
            default=lambda: dict(),
            nullable=True
        ),
    )


def downgrade():
    """Downgrade database."""
    op.drop_table('workflows_record_sources')
    op.create_table(
        'workflows_record_sources',
        sa.Column(
            'source',
            sa.Text,
            default='',
            nullable=False,
        ),
        sa.Column(
            'record_id',
            UUIDType,
            sa.ForeignKey('records_metadata.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('record_id', 'source'),
        sa.Column(
            'json',
            JSONType().with_variant(
                postgresql.JSON(none_as_null=True),
                'postgresql',
            ),
            default=lambda: dict(),
        ),
    )
