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

import string
import random

from invenio_db import db

from invenio_pidstore.errors import PIDAlreadyExists
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from inspire_utils.record import get_value

from .providers import InspireRecordIdProvider
from .utils import get_pid_type_from_schema, _texkey_is_valid, \
    _texkey_create, get_pid_value, handle_pid_update_by_type


def inspire_recid_minter_update(record_uuid, data):
    """Update specific minters."""
    # get all ids for this ``object_uuid``
    pids = PersistentIdentifier.query.filter_by(object_uuid=record_uuid).all()
    # ``eprint``
    inspire_arxiv_minter(record_uuid, data, pids=pids)
    # ``isbn``
    inspire_isbn_minter(record_uuid, data, pids=pids)
    # ``texkeys``
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

    # eprint
    inspire_arxiv_minter(record_uuid, data)
    # isbn
    inspire_isbn_minter(record_uuid, data)
    # texkey
    inspire_texkey_minter(record_uuid, data)
    # return the pid
    return provider.pid


def inspire_arxiv_minter(record_uuid, data, pids=None):
    """Mint arXiv preprint identifier.

    Mints arXiv preprint identifier if ``archive_eprint`` field exists.

    Note:
        If the records is updated it will check if any of the existing
        ``isbns`` is deleted and will delete them. Also will add any
        new ones.

    Args:
        record_uuid (str): a record.
        data (dict): record metadata

    Returns:
        PersistentIdentifier: a persistent identifier.
    """

    arxiv_eprints = get_value(data, 'arxiv_eprints.value[:]')

    if pids is not None:
        # get the existing pids
        existing = get_pid_value(pids, 'arxiv')
        # get the new ones
        arxiv_eprints = handle_pid_update_by_type(existing, data, 'arxiv')
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
                pass


def inspire_isbn_minter(record_uuid, data, pids=None):
    """Mint International Series Book Number.

    Mints ISBNs if ``isbns`` field exists.

    Note:
        If the records is updated it will check if any of the existing
        ``isbns`` is deleted and will delete them. Also will add any
        new ones.

    Args:
        record_uuid (str): a record.
        data (dict): record metadata

    Returns:
        PersistentIdentifier: a persistent identifier.
    """

    isbns = get_value(data, 'isbns.value[:]')

    if pids is not None:
        # get the existing pids
        existing = get_pid_value(pids, 'isbn')
        # get the new ones
        isbns = handle_pid_update_by_type(existing, data, 'isbn')

    # add all the new ones
    if isbns:
        for isbn in isbns:
            try:
                PersistentIdentifier.create(
                    'isbn',
                    str(isbn),
                    object_type='rec',
                    object_uuid=record_uuid,
                    status=PIDStatus.REGISTERED
                 )
            except PIDAlreadyExists:
                pass


def inspire_texkey_minter(record_uuid, data, pids=None):
    """Mint texkey.

    Mints texkey.

    Note:
        If the records is updated it will prepend the ``texkey`` to the
        exising list.

    Args:
        record_uuid (str): a record.
        data (dict): record metadata

    Returns:
        PersistentIdentifier: a persistent identifier.
    """
    pids = PersistentIdentifier.query.filter_by(object_uuid=record_uuid).all()
    existing = get_pid_value(pids, 'texkey') or ['']
    add = []
    if pids:
        # check if they are still valid
        if not _texkey_is_valid(data, existing):
            # create a new texkey
            texkey = _texkey_create(data)
            add.append(texkey)
    else:
        existing = get_value(data, 'texkeys[:]', default=[])
        add = add + existing
        if not _texkey_is_valid(data, existing):
            # create a new texkey
            texkey = _texkey_create(data)
            add = [texkey] + add

    for key in add:
        PersistentIdentifier.create(
              'texkey',
               key,
              object_type='rec',
              object_uuid=record_uuid,
              status=PIDStatus.REGISTERED
        )
    pids = PersistentIdentifier.query.filter_by(object_uuid=record_uuid).all()
    existing = get_pid_value(pids, 'texkey')
    data['texkeys'] = existing
