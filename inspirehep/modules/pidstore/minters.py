# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Persistent identifier minters."""

from __future__ import absolute_import, division, print_function

from flask import current_app

from invenio_pidstore.errors import PIDAlreadyExists
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from inspire_utils.record import get_value

from .providers import InspireRecordIdProvider
from .utils import get_pid_type_from_schema


def inspire_recid_minter(record_uuid, data):
    """Mint record identifiers."""
    assert '$schema' in data
    args = dict(
        object_type='rec',
        object_uuid=record_uuid,
        pid_type=get_pid_type_from_schema(data['$schema'])
    )
    if 'control_number' in data:
        args['pid_value'] = data['control_number']
    provider = InspireRecordIdProvider.create(**args)
    data['control_number'] = provider.pid.pid_value
    # mint arxiv eprint
    inspire_arxiv_minter(record_uuid, data)
    return provider.pid


def inspire_arxiv_minter(record_uuid, data, pids=None):
    """Mint arXiv preprint identifier.

    Mints arXiv preprint identifier if ``archive_eprint`` field exists.

    Args:
        record_uuid (str): a record.
        data (dict): record metadata
    Returns:
        PersistentIdentifier: a persistent identifier.
    """
    if pids is not None:
        arxiv_eprints = get_value(data, 'arxiv_eprints.value[:]')
    else:
        arxiv_eprints = get_value(data, 'arxiv_eprints.value[:]')

    # add all the new ones
    if arxiv_eprints:
        for arxiv_eprint in arxiv_eprints:
            try:
                PersistentIdentifier.create(
                    'arxiv',
                    str(arxiv_eprint),
                    object_type='rec',
                    object_uuid=record_uuid,
                    status=PIDStatus.REGISTERED
                 )
            except PIDAlreadyExists:
                current_app.logger.error(
                    'PID key arxiv with value {0} already exists'.format(
                        arxiv_eprint
                    )
                )
