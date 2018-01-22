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

from invenio_pidstore.models import PersistentIdentifier
from invenio_workflows import workflow_object_class

from inspirehep.modules.pidstore.minters import inspire_texkey_minter
from inspirehep.modules.records.api import InspireRecord


def test_texkey_minter_new(app):
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
    # a workflow object
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    # create a record
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    # commit the record
    record.commit()
    # mint the ``texkey``
    inspire_texkey_minter(str(record.id), record)
    # get all pids
    pids = PersistentIdentifier.query.filter_by(object_uuid=str(record.id), pid_type='texkey').all()
    # should be only 1
    assert len(pids) == 1


def test_texkey_minter_with_the_same_pid_value(app):
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
    # a workflow object
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    # create a record
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    # commit the record
    record.commit()
    # mint the ``texkey``
    inspire_texkey_minter(str(record.id), record)
    # get all pids
    pids = PersistentIdentifier.query.filter_by(object_uuid=str(record.id), pid_type='texkey').all()
    # should be only 1
    assert len(pids) == 1
    # create a record
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    # commit the record
    record.commit()
    # mint the ``texkey``
    inspire_texkey_minter(str(record.id), record)
    # get all pids
    pids = PersistentIdentifier.query.filter_by(object_uuid=str(record.id), pid_type='texkey').all()
    # should be only 1
    assert len(pids) == 1


def test_texkey_minter_with_existing_without_change(app):
    """Test texkey with existing texkeys."""
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
    # a workflow object
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    # create a record
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    # commit the record
    record.commit()
    # mint the ``texkey``
    inspire_texkey_minter(str(record.id), record)
    # get all pids
    pids = PersistentIdentifier.query.filter_by(object_uuid=str(record.id), pid_type='texkey').all()
    # should be only 1
    assert len(pids) == 1
    # Should have the same value
    assert record['texkeys'][0] == pids[0].pid_value
    # try to mint again with the  same author
    inspire_texkey_minter(str(record.id), record)
    # get all pids
    pids = PersistentIdentifier.query.filter_by(object_uuid=str(record.id), pid_type='texkey').all()
    # should be only 1
    assert len(pids) == 1
    # Should have the same value
    assert record['texkeys'][0] == pids[0].pid_value


def test_texkey_minter_with_existing_with_change(app):
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
            'Jones:2001azy'
        ]
    }
    # a workflow object
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    # create a record
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    # commit the record
    record.commit()
    # mint the ``texkey``
    inspire_texkey_minter(str(record.id), record)
    # get all pids
    pids = PersistentIdentifier.query.filter_by(object_uuid=str(record.id), pid_type='texkey').all()
    # should be only 1
    assert len(pids) == 2
    keys = str(record['texkeys'])
    # Rand should be part of the texkeys
    assert 'Rand:2001' in keys
    # Jones should be part of the texkeys
    assert 'Jones:2001' in keys


def test_update_texkey_minter_with_existing_with_change(app):
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
    # a workflow object
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    # create a record
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    # commit the record
    record.commit()
    # mint the ``texkey``
    inspire_texkey_minter(str(record.id), record)
    # get all pids
    pids = PersistentIdentifier.query.filter_by(object_uuid=str(record.id), pid_type='texkey').all()
    # should be only 1
    assert len(pids) == 2
    keys = str(record['texkeys'])
    # Rand should be part of the texkeys
    assert 'Rand:2001' in keys
    # Jones should be part of the texkeys
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

    # a workflow object
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    # update record
    record.clear()
    record.update(obj.data)
    record.commit()
    # mint the ``texkey``
    inspire_texkey_minter(str(record.id), record)
    # get all pids
    pids = PersistentIdentifier.query.filter_by(object_uuid=str(record.id), pid_type='texkey').all()
    # should be only 3
    assert len(pids) == 3
    keys = str(record['texkeys'])
    # Castle should be part of the texkeys
    assert 'Castle:2001' in keys
    # Rand should be part of the texkeys
    assert 'Rand:2001' in keys
    # Jones should be part of the texkeys
    assert 'Jones:2001' in keys


def test_update_texkey_minter_with_existing_without_change(app):
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
    # a workflow object
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    # create a record
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    # commit the record
    record.commit()
    # mint the ``texkey``
    inspire_texkey_minter(str(record.id), record)
    # get all pids
    pids = PersistentIdentifier.query.filter_by(object_uuid=str(record.id), pid_type='texkey').all()
    # should be only 1
    assert len(pids) == 2
    keys = str(record['texkeys'])
    # Rand should be part of the texkeys
    assert 'Rand:2001' in keys
    # Jones should be part of the texkeys
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
    # a workflow object
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    # update record
    record.clear()
    record.update(obj.data)
    record.commit()
    # mint the ``texkey``
    inspire_texkey_minter(str(record.id), record)
    # get all pids
    pids = PersistentIdentifier.query.filter_by(object_uuid=str(record.id), pid_type='texkey').all()
    # should be only 2
    assert len(pids) == 2
    keys = str(record['texkeys'])
    # Rand should be part of the texkeys
    assert 'Rand:2001' in keys
    # Jones should be part of the texkeys
    assert 'Jones:2001' in keys
