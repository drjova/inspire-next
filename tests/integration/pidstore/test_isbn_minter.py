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

"""Minter ``isbn`` integration"""

from __future__ import absolute_import, division, print_function

from invenio_pidstore.models import PersistentIdentifier
from invenio_workflows import workflow_object_class

from inspirehep.modules.pidstore.minters import inspire_isbn_minter
from inspirehep.modules.records.api import InspireRecord


def test_isbn_minter_new(app):
    """Test isbn minter in new record."""
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
        '_collections': ['Literature'],
        'titles': [
            {'title': 'merged'},
        ],
        'isbns': [
            {
                'value': '11111111111'
            },
            {
                'value': '22222222222'
            }
        ],
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
    # mint the ``isbn``
    inspire_isbn_minter(str(record.id), record)
    # get all pids
    pids = PersistentIdentifier.query.filter_by(object_uuid=str(record.id), pid_type='isbn').all()
    # should be only 2
    assert len(pids) == 2


def test_isbn_minter_update(app):
    """Test isbn minter in new record."""
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
        '_collections': ['Literature'],
        'titles': [
            {'title': 'merged'},
        ],
        'isbns': [
            {
                'value': '33333333333'
            },
            {
                'value': '44444444444'
            }
        ],
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
    # mint the ``isbn``
    inspire_isbn_minter(str(record.id), record)
    # get all pids
    pids = PersistentIdentifier.query.filter_by(object_uuid=str(record.id), pid_type='isbn').all()
    # should be only 2
    assert len(pids) == 2
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
        '_collections': ['Literature'],
        'titles': [
            {'title': 'merged'},
        ],
        'isbns': [
            {
                'value': '33333333333'
            },
            {
                'value': '44444444444'
            },
            {
                'value': '55555555555'
            }
        ],
    }
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
    # mint the ``isbn``
    inspire_isbn_minter(str(record.id), record)
    # get all pids
    pids = PersistentIdentifier.query.filter_by(object_uuid=str(record.id), pid_type='isbn').all()
    # should be only 3
    assert len(pids) == 3
