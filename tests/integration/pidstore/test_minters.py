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

from invenio_pidstore.models import PersistentIdentifier
from invenio_workflows import workflow_object_class

from inspirehep.modules.pidstore.minters import inspire_recid_minter, \
    inspire_recid_minter_update
from inspirehep.modules.records.api import InspireRecord


def test_minters_on_create(isolated_app):
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
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
        'arxiv_eprints': [
            {
                'categories': [
                    'astro-ph.HE'
                ],
                'value': '1701.11111'
            },
            {
                'categories': [
                    'astro-ph.HE'
                ],
                'value': '1801.22222'
            }
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
    inspire_recid_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).all()

    assert len(pids) == 6


def test_minters_on_update(isolated_app):
    data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2001-11-01',
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
        'arxiv_eprints': [
            {
                'categories': [
                    'astro-ph.HE'
                ],
                'value': '1701.11111'
            },
            {
                'categories': [
                    'astro-ph.HE'
                ],
                'value': '1801.22222'
            }
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
    inspire_recid_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).all()

    assert len(pids) == 6

    data['authors'] = [
        {'full_name': 'Francis, Castle'},
        {'full_name': 'Jessica, Jones'},
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
    record.update(data)
    record.commit()
    inspire_recid_minter_update(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id)).all()

    assert len(pids) == 7
