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

from __future__ import absolute_import, division, print_function

import uuid

from invenio_pidstore.models import PersistentIdentifier

from inspirehep.modules.pidstore.utils import (
    get_endpoint_from_pid_type,
    get_pid_type_from_endpoint,
    get_pid_type_from_schema,
    get_pid_types_from_endpoints,
    get_new_pid_values,
    get_deleted_pid_values,
    get_pid_type_values
)


def test_get_endpoint_from_pid_type():
    expected = 'literature'
    result = get_endpoint_from_pid_type('lit')

    assert expected == result


def test_get_pid_type_from_endpoint():
    expected = 'lit'
    result = get_pid_type_from_endpoint('literature')

    assert expected == result


def test_get_pid_type_from_schema():
    expected = 'lit'
    result = get_pid_type_from_schema('http://localhost:5000/schemas/record/hep.json')

    assert expected == result


def test_get_pid_from_schema_supports_relative_urls():
    expected = 'aut'
    result = get_pid_type_from_schema('schemas/record/authors.json')

    assert expected == result


def test_get_pid_types_from_endpoint(app):
    pid_types = set(('lit', 'con', 'exp', 'jou', 'aut', 'job', 'ins'))
    assert pid_types.issubset(get_pid_types_from_endpoints())


def test_new_pid_values():
    """Test new values from record."""
    expected = ['1901.33333']
    current = ['1701.11111', '1801.22222']
    update = ['1701.11111', '1801.22222', '1901.33333']

    new_values = get_new_pid_values(current, update)

    assert new_values == expected


def test_deleted_pid_values():
    """Test deleted values from record."""
    expected = ['1901.33333']
    update = ['1701.11111', '1801.22222']
    current = ['1701.11111', '1801.22222', '1901.33333']

    deleted_values = get_deleted_pid_values(current, update)

    assert deleted_values == expected


def test_pid_type_values(app):
    """Test values from pid_type."""
    rec_uuid = uuid.uuid4()
    PersistentIdentifier.create(
        'arxiv',
        '1901.33333',
        object_type='rec',
        object_uuid=rec_uuid,
    )
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=rec_uuid, pid_type='arxiv').all()
    pid_values = get_pid_type_values(pids, 'arxiv')
    assert len(pid_values) == 1
    assert '1901.33333' in pid_values


def test_texkey_creation_with_author():
    """Test texkey creattion with one author."""
    expected = 'Jones:2001'
    record = {
        'created': '2001-11-01',
        'authors': [
            {'full_name': 'Jessica, Jones'},
            {'full_name': 'Francis, Castle'},
        ]
    }
    result = _texkey_create(record, with_random_part=False)
    assert expected == result


def test_texkey_creation_with_gt_10_authors():
    """Test texkey with more than 10 authors."""
    expected = 'Jones:2001'
    record = {
        'created': '2001-11-01',
        'authors': [
            {'full_name': 'Jessica, Jones'},
            {'full_name': 'Francis, Castle'},
            {'full_name': 'Luke, Cage'},
            {'full_name': 'Danny, Rand'},
            {'full_name': 'Matt, Murdock'},
            {'full_name': 'Bruce , Banner'},
            {'full_name': 'Stephen , Strange'},
            {'full_name': 'Scott , Lang'},
            {'full_name': 'Wade , Wilson'},
            {'full_name': 'Kyle , Richmond'},
            {'full_name': 'Felicia , Hardy'},
        ]
    }
    result = _texkey_create(record, with_random_part=False)
    assert expected == result


def test_texkey_creation_with_gt_10_authors_with_collaboration():
    """Test texkey with more than 10 authors and collaboration."""
    expected = 'Defenders:2001'
    record = {
        'created': '2001-11-01',
        'authors': [
            {'full_name': 'Jessica, Jones'},
            {'full_name': 'Francis, Castle'},
            {'full_name': 'Luke, Cage'},
            {'full_name': 'Danny, Rand'},
            {'full_name': 'Matt, Murdock'},
            {'full_name': 'Bruce , Banner'},
            {'full_name': 'Stephen , Strange'},
            {'full_name': 'Scott , Lang'},
            {'full_name': 'Wade , Wilson'},
            {'full_name': 'Kyle , Richmond'},
            {'full_name': 'Felicia , Hardy'},
        ],
        'collaborations': [
            {'value': 'Defenders'}
        ]
    }
    result = _texkey_create(record, with_random_part=False)
    assert expected == result


def test_texkey_creation_without_author_with_collaborations():
    """Test texkey without author and collaborations."""
    expected = 'Defenders:2001'
    record = {
        'created': '2001-11-01',
        'collaborations': [
            {'value': 'Defenders'}
        ]
    }
    result = _texkey_create(record, with_random_part=False)
    assert expected == result


def test_texkey_creation_without_author_and_collaborations_with_corporate():
    """Test texkey without author and collaborations only with corporate."""
    expected = 'StarkIndustries:2001'
    record = {
        'created': '2001-11-01',
        'corporate_author': [
            'Stark Industries'
        ]
    }
    result = _texkey_create(record, with_random_part=False)
    assert expected == result


def test_texkey_creation_without_author_and_collaborations_with_corporate_and_proceedings():
    """Test texkey without author and collaborations only with corporate and proceedings."""

    expected = 'proceedings:2001'
    record = {
        'created': '2001-11-01',
        'document_type': [
            'proceedings'
        ],
    }
    result = _texkey_create(record, with_random_part=False)
    assert expected == result


def test_texkey_creation_without_author_and_collaborations_and_corporate_author_and_proceedings():
    """Test texkey without author and collaborations only with corporate and proceedings."""
    expected = ':2001'
    record = {
        'created': '2001-11-01',
    }
    result = _texkey_create(record, with_random_part=False)
    assert expected == result


def test_texkey_clearn_author_names():
    """Test texkey clean name."""
    expected = 'Haoup'
    result = _texkey_clean_author('Häöüp')
    assert expected == result


def test_texkey_validation():
    """Test texkey validation."""
    expected = True
    record = {
        'created': '2001-11-01',
        'authors': [
            {'full_name': 'Jessica, Jones'},
            {'full_name': 'Francis, Castle'},
            {'full_name': 'Luke, Cage'},
            {'full_name': 'Danny, Rand'},
            {'full_name': 'Matt, Murdock'},
            {'full_name': 'Bruce , Banner'},
            {'full_name': 'Stephen , Strange'},
            {'full_name': 'Scott , Lang'},
            {'full_name': 'Wade , Wilson'},
            {'full_name': 'Kyle , Richmond'},
            {'full_name': 'Felicia , Hardy'},
        ]
    }
    existing = ['Jones:2001xyz']
    result = _texkey_is_valid(record, existing)
    assert expected == result
