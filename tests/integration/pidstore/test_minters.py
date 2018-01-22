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

"""Minter ``arxiv`` integration"""

from __future__ import absolute_import, division, print_function

from inspirehep.modules.workflows.tasks.upload import store_record

from invenio_pidstore.models import PersistentIdentifier
from invenio_workflows import workflow_object_class


def test_store_new_record(app):
    """Test new record."""
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
        'authors': [
            {'full_name': 'Jessica, Jones'},
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
                'value': '1702.11111'
            },
            {
                'categories': [
                    'astro-ph.HE'
                ],
                'value': '1802.22222'
            }
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
    store_record(obj, None)

    arxiv_pids = PersistentIdentifier.query.filter_by(
        object_uuid=obj.extra_data['head_uuid'], pid_type='arxiv').all()

    assert len(arxiv_pids) == 2

    isbn_pids = PersistentIdentifier.query.filter_by(
        object_uuid=obj.extra_data['head_uuid'], pid_type='isbn').all()

    assert len(isbn_pids) == 2

    texkey_pids = PersistentIdentifier.query.filter_by(
        object_uuid=obj.extra_data['head_uuid'], pid_type='texkey').all()

    assert len(texkey_pids) == 1
