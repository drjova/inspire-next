# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

import json

from inspirehep.modules.records.serializers.schemas.common import ReferenceItemSchemaV1


def test_returns_non_empty_fields():
    schema = ReferenceItemSchemaV1()
    dump = {
        'reference': {
            'label': '123',
            'control_number': 123,
            'authors': [
                {
                    'full_name': 'Jessica, Jones',
                },
            ],
            'publication_info': {
                'journal_title': 'Alias Investigations',
            },
        }
    }
    expected = {
        'label': '123',
        'control_number': 123,
        'authors': [
            {
                'first_name': 'Jones',
                'full_name': 'Jessica, Jones',
                'last_name': 'Jessica'
            }
        ],
        'publication_info': {
            'journal_title': 'Alias Investigations',
        },
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_non_empty_fields_if_all_fields_missing():
    schema = ReferenceItemSchemaV1()
    dump = {
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
    }
    expected = {}
    result = schema.dumps(dump).data

    assert expected == json.loads(result)



def test_returns_non_empty_fields_if_some_fields_missing():
    schema = ReferenceItemSchemaV1()
    dump = {
        'reference': {
            'label': '123',
            'control_number': 123,
        },
    }
    expected = {
        'label': '123',
        'control_number': 123,
    }
    result = schema.dumps(dump).data

    assert expected == json.loads(result)
