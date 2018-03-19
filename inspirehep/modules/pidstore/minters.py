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
from .utils import get_pid_type_from_schema, get_deleted_pid_values, \
    get_new_pid_values, get_pid_type_values, get_pid_value, _texkey_is_valid, \
    _texkey_create


def inspire_recid_minter_update(record_uuid, data):
    """Update record identifiers."""
    # get all ids for this ``object_uuid``
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=record_uuid).all()
    # mint arxiv eprint
    inspire_arxiv_minter(record_uuid, data, pids=pids)
    # mint isbn
    inspire_isbn_minter(record_uuid, data, pids=pids)
    # mint texkeys
    inspire_texkey_minter(record_uuid, data, pids=pids)


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
    # mint isbn
    inspire_isbn_minter(record_uuid, data)
    # mint texkeys
    inspire_texkey_minter(record_uuid, data)
    return provider.pid


def inspire_arxiv_minter(record_uuid, data, pids=None):
    """Mint arXiv preprint identifier.

    Mints arXiv preprint identifier if ``archive_eprint`` field exists.

    Args:
        record_uuid (str): a record.
        data (dict): record metadata.

    Returns:
        PersistentIdentifier: a persistent identifier.
    """
    arxiv_eprints = []
    if pids is not None:
        current = get_pid_type_values(pids, 'arxiv')
        updated = get_value(data, 'arxiv_eprints.value[:]', default=[])
        arxiv_eprints = get_new_pid_values(current, updated)
    else:
        arxiv_eprints = get_value(data, 'arxiv_eprints.value[:]', default=[])

    for arxiv_eprint in arxiv_eprints:
        try:
            PersistentIdentifier.create(
                'arxiv',
                str(arxiv_eprint),
                object_type='rec',
                object_uuid=record_uuid,
                status=PIDStatus.RESERVED
             )
        except PIDAlreadyExists:
            current_app.logger.error(
                'PID key arxiv with value {0} already exists'.format(
                    arxiv_eprint
                )
            )


def inspire_isbn_minter(record_uuid, data, pids=None):
    """Mint International Series Book Number.

    Mints ISBNs if ``isbns`` field exists.

    Note:
        If the records is updated it will check if any of the existing
        ``isbns`` is deleted and will delete them. Also will add any
        new ones.

    Args:
        record_uuid (str): a record.
        data (dict): record metadata.

    Returns:
        PersistentIdentifier: a persistent identifier.
    """

    isbns = []

    if pids is not None:
        current = get_pid_type_values(pids, 'isbn')
        updated = get_value(data, 'isbns.value[:]', default=[])
        isbns = get_new_pid_values(current, updated)
        deleted_isbns = get_deleted_pid_values(current, updated)
        for pid in deleted_isbns:
            PersistentIdentifier.get('isbn', pid).delete()
    else:
        isbns = get_value(data, 'isbns.value[:]', default=[])
    for isbn in isbns:
        try:
            PersistentIdentifier.create(
                'isbn',
                str(isbn),
                object_type='rec',
                object_uuid=record_uuid,
                status=PIDStatus.RESERVED
             )
        except PIDAlreadyExists:
            current_app.logger.error(
                'PID key isbn with value {0} already exists for {1}.'.format(
                    isbn, record_uuid
                )
            )


def inspire_texkey_minter(record_uuid, data, pids=None):
    """Mint texkey.

    Mints texkey.

    Note:
        If the records is updated it will prepend the ``texkey`` to the
        exising list.

    Args:
        record_uuid (str): a record.
        data (dict): record metadata.

    Returns:
        PersistentIdentifier: a persistent identifier.
    """
    add = []
    if pids:
        existing = get_pid_value(pids, 'texkey') or None
        if not _texkey_is_valid(data, existing):
            texkey = _texkey_create(data)
            add.append(texkey)
    else:
        add = get_value(data, 'texkeys[:]', default=[])
        if not _texkey_is_valid(data, add):
            texkey = _texkey_create(data)
            add = [texkey] + add

    for key in add:
        try:
            PersistentIdentifier.create(
                  'texkey',
                  key,
                  object_type='rec',
                  object_uuid=record_uuid,
                  status=PIDStatus.REGISTERED
            )
        except PIDAlreadyExists:
            current_app.logger.error(
                'PID key texkey with value {0} already exists for {1}.'.format(
                    key, record_uuid
                )
            )
    pids = PersistentIdentifier.query.filter_by(object_uuid=record_uuid).all()
    existing = get_pid_value(pids, 'texkey')
    data['texkeys'] = existing
