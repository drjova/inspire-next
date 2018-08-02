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

import json

from inspirehep.modules.records.serializers.schemas.json import \
    ReferencesSchemaJSONUIV1, RecordSchemaJSONUIV1

from factories.db.invenio_records import TestRecordMetadata


def test_references_schema_with_record(isolated_app):
    schema = ReferencesSchemaJSONUIV1()
    cited_record = {
        'control_number': 123,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
        'authors': [
            {
                'full_name': 'Frank Castle',
            },
        ],
        'dois': [
            {
                'value': '10.1088/1361-6633/aa5514',
            },
        ],
        'publication_info': [
            {
                'artid': '046201',
                'journal_issue': '4',
                'journal_recid': 1214416,
                'journal_record': {
                    '$ref': 'http://labs.inspirehep.net/api/journals/1214416'
                },
                'journal_title': 'Rept.Prog.Phys.',
                'journal_volume': '80',
                'year': 2017,
            },
        ],
        'arxiv_eprints': [
            {
                'value': '1607.06746',
            },
        ],
        'urls': [
            {
                'value': 'http://sf2a.eu/semaine-sf2a/2013/proceedings/'
            }
        ],
        'collaborations': [{
            'value': 'LHCb',
        }],
    }
    TestRecordMetadata.create_from_kwargs(json=cited_record)

    record = {
        'metadata': {
            'references': [
                {
                    'record': {
                        '$ref': 'http://labs.inspirehep.net/api/literature/123'
                    },
                    'reference': {
                        'authors': [{
                            'full_name': 'Yamanaka, T.'
                        }],
                        'label': '389',
                        'misc': ['The J-PARC KOTO experiment 006'],
                        'publication_info': {
                            'artid': '02B006',
                            'journal_title': 'PTEP',
                            'journal_volume': '2012',
                            'year': 2012,
                        }
                    }
                },
                {
                    'reference': {
                        'titles': {
                            'title': 'Jessica Jones',
                        },
                        'authors': [{
                            'full_name': 'Frank Castle',
                        }],
                        'label': '1',
                        'publication_info': {
                            'artid': '02B006',
                            'journal_title': 'PTEP',
                            'journal_volume': '2012',
                            'year': 2012,
                        }
                    }
                },
                {
                    'reference': {
                        'authors': [{
                            'full_name': 'Jessica, Jones'
                        }],
                        'misc': ['The J-PARC KOTO experiment 006'],
                    }
                },
            ],
        },
    }
    expected = {
        "metadata": {
            "references": [
                {
                    "authors": [
                        {
                            "first_name": "Frank Castle",
                            "full_name": "Frank Castle"
                        }
                    ],
                    "control_number": 123,
                    "label": "389",
                    "publication_info": [
                        {
                            "artid": "046201",
                            "journal_issue": "4",
                            "journal_title": "Rept.Prog.Phys.",
                            "journal_volume": "80"
                        }
                    ]
                },
                {
                    "authors": [
                        {
                            "first_name": "Frank Castle",
                            "full_name": "Frank Castle"
                        }
                    ],
                    "label": "1",
                    "publication_info": [
                        {
                            "artid": "02B006",
                            "journal_title": "PTEP",
                            "journal_volume": "2012"
                        }
                    ]
                },
                {
                    "authors": [
                        {
                            "first_name": "Jones",
                            "full_name": "Jessica, Jones",
                            "last_name": "Jessica"
                        }
                    ]
                }
            ]
        }
    }

    result = json.loads(schema.dumps(record).data)
    assert expected == result


def test_conference_info_schema_with_record(isolated_app):
    schema = RecordSchemaJSONUIV1()
    conf_record = {
        "$schema": "http://localhost:5000/schemas/records/conferences.json",
        "_collections": [
            "Conferences"
        ],
        "control_number": 972464,
        "self": {
            "$ref": "http://localhost:5000/api/conferences/972464"
        },
        "titles": [
            {
                "title": "4th RESCEU International Symposium on Birth and Evolution of the Universe"
            }
        ],
    }
    TestRecordMetadata.create_from_kwargs(json=conf_record)
    record = {
        'metadata': {
            'publication_info': [
                {
                    'artid': '02B006',
                    'journal_title': 'PTEP',
                    'journal_volume': '2012',
                    'year': 2012,
                    'conference_record': {
                        '$ref': 'http://labs.inspirehep.net/api/journals/972464'
                    }

                },
                {
                    'artid': '02B006',
                    'journal_title': 'PTEP',
                    'journal_volume': '2012',
                    'year': 2012

                }
            ]

        }
    }

    expected = {
        'metadata': {
            'publication_info': [
                {
                    'artid': '02B006',
                    'journal_title': 'PTEP',
                    'journal_volume': '2012',
                },
                {
                    'artid': '02B006',
                    'journal_title': 'PTEP',
                    'journal_volume': '2012',
                }
            ],
            'conference_info': [
                {
                    "control_number": 972464,
                    "titles": [
                        {
                            "title": "4th RESCEU International Symposium on Birth and Evolution of the Universe"
                        }
                    ]
                }
            ]

        }
    }

    result = json.loads(schema.dumps(record).data)
    assert expected == result
