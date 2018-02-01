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

"""Minter ``arxiv`` integration."""

from __future__ import absolute_import, division, print_function

from invenio_pidstore.models import PersistentIdentifier
from invenio_workflows import workflow_object_class

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.pidstore.minters import inspire_arxiv_minter


def test_arxiv_minter(isolated_app):
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
        ]
    }
    obj = workflow_object_class.create(
        data=data,
        id_user=1,
        data_type='hep'
    )
    record = InspireRecord.create(obj.data, id_=None, skip_files=True)
    record.commit()
    inspire_arxiv_minter(str(record.id), record)
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='arxiv').all()

    assert len(pids) == 2

    data['arxiv_eprints'].append({
        'categories': [
            'astro-ph.HE'
        ],
        'value': '1901.33333'
    })
    record.update(data)
    inspire_arxiv_minter(str(record.id), obj.data, pids=pids)
    record.commit()
    pids = PersistentIdentifier.query.filter_by(
        object_uuid=str(record.id), pid_type='arxiv').all()

    assert len(pids) == 3
