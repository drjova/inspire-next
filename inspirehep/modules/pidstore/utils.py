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

"""PIDStore utils."""

from __future__ import absolute_import, division, print_function

import re
from datetime import date
from itertools import chain
from random import choice

from flask import current_app
from six import iteritems, PY3
from six.moves.urllib.parse import urlsplit
from string import ascii_lowercase
from unidecode import unidecode
import unicodedata

from invenio_pidstore.models import PersistentIdentifier

from inspire_utils.date import earliest_date, PartialDate
from inspire_utils.record import get_value
from inspire_utils.helpers import force_list

def _get_pid_type_endpoint_map():
    pid_type_endpoint_map = {}
    for key, value in iteritems(current_app.config['RECORDS_REST_ENDPOINTS']):
        if value.get('default_endpoint_prefix'):
            pid_type_endpoint_map[value['pid_type']] = key

    return pid_type_endpoint_map


def get_endpoint_from_pid_type(pid_type):
    """Return the endpoint corresponding to a ``pid_type``."""
    PID_TYPE_TO_ENDPOINT = _get_pid_type_endpoint_map()

    return PID_TYPE_TO_ENDPOINT[pid_type]


def get_pid_type_from_endpoint(endpoint):
    """Return the ``pid_type`` corresponding to an endpoint."""
    ENDPOINT_TO_PID_TYPE = {
        v: k for k, v in iteritems(_get_pid_type_endpoint_map())}

    return ENDPOINT_TO_PID_TYPE[endpoint]


def get_pid_type_from_schema(schema):
    """Return the ``pid_type`` corresponding to a schema URL.

    The schema name corresponds to the ``endpoint`` in all cases except for
    Literature records. This implementation exploits this by falling back to
    ``get_pid_type_from_endpoint``.
    """
    def _get_schema_name_from_schema(schema):
        return urlsplit(schema).path.split('/')[-1].split('.')[0]

    schema_name = _get_schema_name_from_schema(schema)
    if schema_name == 'hep':  # FIXME: remove when hep.json -> literature.json
        return 'lit'

    return get_pid_type_from_endpoint(schema_name)


def handle_pid_update_by_type(current, updated, pid_type):
    """Handle pid update.

    Handles pid updates for a given record.

    Args:
        current list(str): a list of the existing ``pids``.
        updated list(str): a list of the new ``pids``.
        pid_type (str): a ``pid_type``.
    """
    # which to delete
    need_deletion = get_deleted_pids(current, updated)
    # which to create
    need_creation = get_new_pids(current, updated)
    # delete
    _delete_pids(need_deletion, pid_type)
    # return need creation
    return need_creation


def get_new_pids(current, updated):
    """Get the new pids from the updated record.

    Compares the current ``pid.values`` with the updated ones.

    Args:
        current list(str): a list of the existing ``pids``.
        updated list(str): a list of the new ``pids``.

    Returns:
        list(str): a list of the new ``pids``.
    """
    return list(set(updated) - set(current))


def get_deleted_pids(current, updated):
    """Get the deleted pids from the updated record.

    Compares the current ``pid.values`` with the updated ones.

    Args:
        current list(str): a list of the existing ``pids``.
        updated list(str): a list of the new ``pids``.

    Returns:
        list(str): a list of the new ``pids``.
    """
    return list(set(current) - set(updated))


def _delete_pids(pids, pid_type):
    """Deletes a list of pids."""
    for pid in pids:
        PersistentIdentifier.get(pid_type, pid).delete()


def get_pid_value(pids, pid_type):
    """Return the pids values for a give ``pid_type``.

    Args:
        pids list(PersistentIdentifier): a list of ``pids``.
        pid_type (str): a persistent identifier type.

    Returns:
        list(str): a list of pids.
    """
    return [pid.pid_value for pid in pids if pid.pid_type == pid_type]


def _texkey_clean_author(value):
    """Sanitize a value.

    Args:
        value (str): a value to sanitize.

    Returns:
        str: the sanitized value.

    Examples:
        >>> value = 'Häöüp'
        >>> _texkey_clean_author(value)
        'Haoup'
    """

    def _asciify(string):
        """Transliterate a string to ASCII."""
        if not PY3 and not isinstance(string, unicode):
            string = unicode(string, 'utf8', errors='ignore')

        string = unidecode(unicodedata.normalize('NFKD', string))
        string = string.encode('ascii', 'ignore')
        string = string.decode('utf8')

        return string

    def _remove_bibtex_invalid_chars(value):
        return re.sub(
            r'[^-A-Za-z0-9.:/^_;&*<>?|!$+]',
            '',
            value
        )

    def _contains_a_letter(value):
        return re.search(
            r'[A-Za-z]',
            value
        )

    value = _remove_bibtex_invalid_chars(_asciify(value))
    if len(value) == 0 or not _contains_a_letter(value):
        value = ''

    return value


def _texkey_create(data, with_random_part=True):
    """Generate ``texkey`` from a record.

    Note:
        The ``texkey`` has the following informat:
        ``NAME``:``YEAR````RANDOM_LETTERS``

        For ``NAME``:
            Gets the first ``full_name`` from authors if the number
            of authors is lower than 10.

            Gets the the first ``collaboartion`` or the ``corporate_author``
            or the ``document_type``.

            If none of the above are met falls back to the first ``full_name``
            from authors or an empty string.

        For ``YEAR``:
            Gets the earliest year of the record, as default the current year.

        For ``RANDOM_LETTERS``:
            Gets three random `ascii` lowercase latters.

    Args:
        data (dict): a record data.
        with_random_part (bool, optional): include the random part.

    Returns:
        str: the generated ``texkey``

    Examples:
        >>> record = {
        ...     'created': '2001-11-01',
        ...     'authors': [
        ...            {'full_name': 'Jessica, Jones'},
        ...            {'full_name': 'Francis, Castle'},
        ...      ]
        ... }
        >>> texkey = _texkey_create(record)
        'Jones:2001'
    """
    # generate the author part
    author_part = ''
    if 1 <= len(data.get('authors', [])) < 10:
        author_part = data['authors'][0]['full_name']
    elif data.get('collaborations'):
        author_part = data['collaborations'][0]['value']
    elif data.get('corporate_author'):
        author_part = data['corporate_author'][0]
    elif 'proceedings' in data.get('document_type', []):
        author_part = 'proceedings'
    elif data.get('authors'):
        author_part = data['authors'][0]['full_name']

    # clean the name
    author_part = _texkey_clean_author(author_part.split(',').pop())

    # generate the date path
    date_paths = [
        'preprint_date',
        'thesis_info.date',
        'thesis_info.defense_date',
        'publication_info.year',
        'legacy_creation_date',
        'imprints.date',
    ]
    date_part = None
    # get the date values
    dates = list(
        chain.from_iterable(
            [force_list(get_value(data, path)) for path in date_paths]
        )
    )

    if dates:
        # generate the erliest date
        date_part = earliest_date(
            map(str, dates)
        )
    # if has ``date_part`` get the year
    if date_part:
        date_part = PartialDate.loads(str(date_part)).year
    else:
        # else try to get the created year or get the current one
        date_part = PartialDate.loads(
            data.get('created', str(date.today().year))).year

    # generate random part (optional)
    random_part = ''
    if with_random_part:
        random_part = ''.join(
            choice(ascii_lowercase) for _ in range(3)
        )
    # return the texkey
    return '{}:{}{}'.format(author_part, date_part, random_part)


def _texkey_is_valid(data, existing):
    """Check the validity of the current ``texkey``.

    Note:
        Checks if the ``texkey`` hasn't changed ignoring the random part.

    Args:
        data (dict): a record data.

    Returns:
        bool: if the ``texkey`` is valid.
    """
    if existing:
        # get previous ``texkeys``
        previous_texkeys = existing[0]
        # generate a ``texkey`` without the random part
        texkey = _texkey_create(data, with_random_part=False)
        # check if they much
        return texkey in previous_texkeys
    return False
