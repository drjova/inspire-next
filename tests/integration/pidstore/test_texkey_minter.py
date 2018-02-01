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

"""Minter ``texkey`` integration"""

from __future__ import absolute_import, division, print_function

import datetime

from invenio_pidstore.models import PersistentIdentifier
from invenio_workflows import workflow_object_class

from inspirehep.modules.pidstore.minters import inspire_texkey_minter
from inspirehep.modules.records.api import InspireRecord


def test_texkey_minter_new(isolated_app):
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
        'titles': [
            {'title': 'merged'},
        ],
        '_collections': ['Literature'],
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
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    inspire_texkey_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='texkey').all()

    assert len(pids) == 1
    assert 'Jones:2001' in pids[0].pid_value


def test_texkey_minter_with_the_same_pid_value(isolated_app):
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
        'titles': [
            {'title': 'merged'},
        ],
        '_collections': ['Literature'],
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
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    inspire_texkey_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='texkey').all()


    assert len(pids) == 1
    assert 'Jones:2001' in pids[0].pid_value

    inspire_texkey_minter(str(record.id), record, pids=pids)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='texkey').all()

    assert len(pids) == 1
    assert 'Jones:2001' in pids[0].pid_value


def test_texkey_minter_with_existing(isolated_app):
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
        'titles': [
            {'title': 'merged'},
        ],
        '_collections': ['Literature'],
        'authors': [
            {'full_name': 'Jessica, Jones'},
            {'full_name': 'Francis, Castle'},
            {'full_name': 'Luke, Cage'},
            {'full_name': 'Danny, Rand'},
            {'full_name': 'Matt, Murdock'},
            {'full_name': 'Bruce, Banner'},
            {'full_name': 'Stephen, Strange'},
            {'full_name': 'Scott, Lang'},
            {'full_name': 'Wade, Wilson'},
            {'full_name': 'Kyle, Richmond'},
            {'full_name': 'Felicia, Hardy'},
        ],
        'texkeys': [
            'Jones:2001xyz'
        ]
    }
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    inspire_texkey_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='texkey').all()

    assert len(pids) == 1
    assert record['texkeys'][0] == pids[0].pid_value

    inspire_texkey_minter(str(record.id), record, pids=pids)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='texkey').all()

    assert len(pids) == 1
    assert record['texkeys'][0] == pids[0].pid_value


def test_texkey_minter_with_change(isolated_app):
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
        'titles': [
            {'title': 'merged'},
        ],
        '_collections': ['Literature'],
        'authors': [
            {'full_name': 'Danny, Rand'},
            {'full_name': 'Jessica, Jones'},
            {'full_name': 'Francis, Castle'},
            {'full_name': 'Luke, Cage'},
            {'full_name': 'Matt, Murdock'},
            {'full_name': 'Bruce, Banner'},
            {'full_name': 'Stephen, Strange'},
            {'full_name': 'Scott, Lang'},
            {'full_name': 'Wade, Wilson'},
            {'full_name': 'Kyle, Richmond'},
            {'full_name': 'Felicia, Hardy'},
        ],
        'texkeys': [
            'Jones:2001azy'
        ]
    }
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    inspire_texkey_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='texkey').all()
    keys = str(record['texkeys'])

    assert len(pids) == 2
    assert 'Rand:2001' in keys
    assert 'Jones:2001' in keys


def test_update_texkey_minter_with_existing_with_change(isolated_app):
    """Test texkey with existing texkeys with different authors."""
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
        'titles': [
            {'title': 'merged'},
        ],
        '_collections': ['Literature'],
        'authors': [
            {'full_name': 'Danny, Rand'},
            {'full_name': 'Jessica, Jones'},
            {'full_name': 'Francis, Castle'},
            {'full_name': 'Luke, Cage'},
            {'full_name': 'Matt, Murdock'},
            {'full_name': 'Bruce, Banner'},
            {'full_name': 'Stephen, Strange'},
            {'full_name': 'Scott, Lang'},
            {'full_name': 'Wade, Wilson'},
            {'full_name': 'Kyle, Richmond'},
            {'full_name': 'Felicia, Hardy'},
        ],
        'texkeys': [
            'Jones:2001byz'
        ]
    }
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    inspire_texkey_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='texkey').all()
    keys = str(record['texkeys'])

    assert len(pids) == 2
    assert 'Rand:2001' in keys
    assert 'Jones:2001' in keys

    data['authors'] = [
        {'full_name': 'Francis, Castle'},
        {'full_name': 'Danny, Rand'},
        {'full_name': 'Jessica, Jones'},
        {'full_name': 'Francis, Castle'},
        {'full_name': 'Luke, Cage'},
        {'full_name': 'Matt, Murdock'},
        {'full_name': 'Bruce, Banner'},
        {'full_name': 'Stephen, Strange'},
        {'full_name': 'Scott, Lang'},
        {'full_name': 'Wade, Wilson'},
        {'full_name': 'Kyle, Richmond'},
        {'full_name': 'Felicia, Hardy'},
    ]

    record.clear()
    record.update(data)
    record.commit()
    inspire_texkey_minter(str(record.id), record, pids=pids)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='texkey').all()
    keys = str(record['texkeys'])

    assert len(pids) == 3
    assert 'Castle:2001' in keys
    assert 'Rand:2001' in keys
    assert 'Jones:2001' in keys


def test_update_texkey_minter_with_existing_without_change(isolated_app):
    """Test texkey with existing texkeys with different authors."""
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
        'titles': [
            {'title': 'merged'},
        ],
        '_collections': ['Literature'],
        'authors': [
            {'full_name': 'Danny, Rand'},
            {'full_name': 'Jessica, Jones'},
            {'full_name': 'Francis, Castle'},
            {'full_name': 'Luke, Cage'},
            {'full_name': 'Matt, Murdock'},
            {'full_name': 'Bruce, Banner'},
            {'full_name': 'Stephen, Strange'},
            {'full_name': 'Scott, Lang'},
            {'full_name': 'Wade, Wilson'},
            {'full_name': 'Kyle, Richmond'},
            {'full_name': 'Felicia, Hardy'},
        ],
        'texkeys': [
            'Jones:2001eyz'
        ]
    }
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    inspire_texkey_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='texkey').all()
    keys = str(record['texkeys'])

    assert len(pids) == 2
    assert 'Rand:2001' in keys
    assert 'Jones:2001' in keys

    data['authors'] = [
        {'full_name': 'Danny, Rand'},
        {'full_name': 'Jessica, Jones'},
        {'full_name': 'Francis, Castle'},
        {'full_name': 'Luke, Cage'},
        {'full_name': 'Matt, Murdock'},
        {'full_name': 'Bruce, Banner'},
        {'full_name': 'Stephen, Strange'},
        {'full_name': 'Scott, Lang'},
        {'full_name': 'Wade, Wilson'},
        {'full_name': 'Kyle, Richmond'},
        {'full_name': 'Felicia, Hardy'},
    ]
    record.clear()
    record.update(data)
    record.commit()
    inspire_texkey_minter(str(record.id), record, pids=pids)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='texkey').all()
    keys = str(record['texkeys'])

    assert len(pids) == 2
    assert 'Rand:2001' in keys
    assert 'Jones:2001' in keys


def test_texkey_minter_with_collaboaration(isolated_app):
    """Test texkey minter in new record."""
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
        'titles': [
            {'title': 'merged'},
        ],
        '_collections': ['Literature'],
        'collaborations': [
            {'value': 'Defenders'}
        ]
    }
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    inspire_texkey_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='texkey').all()

    assert len(pids) == 1
    assert 'Defenders:2001' in pids[0].pid_value


def test_texkey_with_corporate_author(isolated_app):
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
        'titles': [
            {'title': 'merged'},
        ],
        '_collections': ['Literature'],
        'corporate_author': [
            'Defenders',
        ]
    }
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    inspire_texkey_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='texkey').all()

    assert len(pids) == 1
    assert 'Defenders:2001' in pids[0].pid_value


def test_texkey_minter_with_proceedings(isolated_app):
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
        'titles': [
            {'title': 'merged'},
        ],
        '_collections': ['Literature'],
        'document_type': ['proceedings']
    }

    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    inspire_texkey_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='texkey').all()

    assert len(pids) == 1
    assert 'proceedings:2001' in pids[0].pid_value


def test_texkey_minter_empty(isolated_app):
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
        'titles': [
            {'title': 'merged'},
        ],
        '_collections': ['Literature'],
    }
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    """
    with pytest.raises(TexkeyMinterError):
        inspire_texkey_minter(str(record.id), record)
    """


def test_texkey_minter_current_date_fallback(isolated_app):
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'merged'},
        ],
        '_collections': ['Literature'],
        'document_type': ['proceedings']
    }

    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    inspire_texkey_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='texkey').all()
    now = datetime.datetime.now()

    assert len(pids) == 1
    assert 'proceedings:{}'.format(now.year) in pids[0].pid_value
