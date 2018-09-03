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

from inspirehep.modules.submissions.serializers.schemas import Author


def test_dump_author():

    # serialize record -> to form recor
    author = {
        "_collections": [
            "Authors"
        ],
        "_private_notes": [
            {
                "source": "nostrud irure",
                "value": "proident do adipisicing pariatur incididunt"
            }
        ],
        "acquisition_source": {
            "datetime": "3793-11-23T11:09:59.661Z",
            "email": "2sFBUsd6@eGwRnIYRpxIbDNi.qh",
            "internal_uid": 65521769,
            "method": "submitter",
            "orcid": "7219-4853-4660-9575",
            "source": "ut fugiat nulla id sed",
            "submission_number": "do aliqua Lorem min"
        },
        "advisors": [
            {
                "curated_relation": True,
                "degree_type": "bachelor",
                "ids": [
                    {
                        "schema": "DESY",
                        "value": "DESY-55924820881"
                    },
                    {
                        "schema": "SCOPUS",
                        "value": "7039712595"
                    },
                    {
                        "schema": "SCOPUS",
                        "value": "8752067273"
                    }
                ],
                "name": "occaecat qui sint in id",
                "record": {
                    "$ref": "http://1js40iZ"
                }
            },
            {
                "curated_relation": False,
                "degree_type": "laurea",
                "ids": [
                    {
                        "schema": "SCOPUS",
                        "value": "6344523811"
                    }
                ],
                "name": "deserunt nisi in",
                "record": {
                    "$ref": "http://12XQ"
                }
            },
            {
                "curated_relation": False,
                "degree_type": "master",
                "ids": [
                    {
                        "schema": "SCOPUS",
                        "value": "83771302666"
                    },
                    {
                        "schema": "DESY",
                        "value": "DESY-88"
                    },
                    {
                        "schema": "DESY",
                        "value": "DESY-6994808"
                    },
                    {
                        "schema": "DESY",
                        "value": "DESY-81200252953"
                    }
                ],
                "name": "deseru",
                "record": {
                    "$ref": "http://1U/_cD"
                }
            }
        ],
        "arxiv_categories": [
            "math.QA",
            "cond-mat.quant-gas",
            "cs.NE"
        ],
        "awards": [
            {
                "name": "aute proident",
                "url": {
                    "description": "occaecat eiusmod",
                    "value": "http://1w"
                },
                "year": 1654
            },
            {
                "name": "amet consectetur aliqua",
                "url": {
                    "description": "consectetur dolore in",
                    "value": "http://16zOEU"
                },
                "year": 2015
            },
            {
                "name": "nisi exe",
                "url": {
                    "description": "ea culpa",
                    "value": "http://1CIKRtW"
                },
                "year": 1877
            },
            {
                "name": "amet magna commodo incididu",
                "url": {
                    "description": "aliquip ad non nulla",
                    "value": "http://1"
                },
                "year": 1657
            }
        ],
        "birth_date": "1485-06-28",
        "control_number": -5145712,
        "death_date": "1886-08-17",
        "deleted": True,
        "deleted_records": [
            {
                "$ref": "http://1Ib"
            },
            {
                "$ref": "http://1v/M"
            }
        ],
        "email_addresses": [
            {
                "current": False,
                "hidden": True,
                "value": "jh1eODzkDL@AKzwKXUQdjCtfLzMDlCfDIl.yf"
            },
            {
                "current": True,
                "hidden": True,
                "value": "VUR3e@wpyAFFXWzuzGKYTMwAABYkz.nsm"
            },
            {
                "current": True,
                "hidden": True,
                "value": "rK1tZBUNQQ@mRQxfP.cfey"
            },
            {
                "current": True,
                "hidden": True,
                "value": "hMZ0VePfwN7lKl@EZUhLeIeFsIWIhSgZvh.onq"
            },
            {
                "current": True,
                "hidden": True,
                "value": "xGxVc1-F@DpkGBmXIVnkkmRbKwJtKmUCznuE.bly"
            }
        ],
        "ids": [
            {
                "schema": "CERN",
                "value": "CERN-4728331004"
            },
            {
                "value": "http://linkedin",
                "schema": "LINKEDIN"
            },
            {
                "value": "http://twitter",
                "schema": "TWITTER"
            },
            {
                "value": "http://blog",
                "schema": "BLOG"
            },
        ],
        "inspire_categories": [
            {
                "source": "arxiv",
                "term": "Phenomenology-HEP"
            },
            {
                "source": "user",
                "term": "Other"
            }
        ],
        "legacy_creation_date": "1535-10-12",
        "name": {
            "name_variants": [
                "mollit dolore veniam",
                "quis Ut laboris",
                "cillum quis veniam ad ea",
                "elit offici",
                "nulla"
            ],
            "native_names": [
                "ut mollit",
                "occaecat aute est sint dolor"
            ],
            "numeration": "Jr.",
            "preferred_name": "ut deserunt",
            "previous_names": [
                "Duis mollit nisi Excepteur nulla",
                "fugiat",
                "sit"
            ],
            "title": "Sir",
            "value": "qui "
        },
        "new_record": {
            "$ref": "http://1n0ybVuN"
        },
        "positions": [
            {
                "curated_relation": False,
                "current": True,
                "end_date": "1724-07-20",
                "institution": "qui ea pariatur ut nisi",
                "record": {
                    "$ref": "http://180"
                }
            },
            {
                "curated_relation": False,
                "current": False,
                "end_date": "1770-04-16",
                "institution": "irure",
                "rank": "UNDERGRADUATE",
                "record": {
                    "$ref": "http://1"
                },
                "start_date": "1820-02-26"
            }
        ],
        "project_membership": [
            {
                "curated_relation": False,
                "current": False,
                "end_date": "2016",
                "name": "pariatur",
                "record": {
                    "$ref": "http://1pmlJbh"
                },
                "start_date": "1984"
            },
            {
                "curated_relation": False,
                "current": False,
                "end_date": "1879",
                "name": "veniam nisi officia dolore est",
                "record": {
                    "$ref": "http://15XGFW/h"
                },
                "start_date": "1788"
            }
        ],
        "public_notes": [
            {
                "source": "Ut ipsum Duis ea aute",
                "value": "non ullamco culpa quis"
            },
            {
                "source": "elit",
                "value": "sunt"
            },
            {
                "source": "ut Ut dolore aute ex",
                "value": "sit fugiat"
            },
            {
                "source": "Ut in",
                "value": "officia dolor ea voluptate"
            },
            {
                "source": "veniam",
                "value": "Lorem dolore nulla in i"
            }
        ],
        "self": {
            "$ref": "http://1MJ_/6g"
        },
        "status": "deceased",
        "stub": False,
        "urls": [
            {
                "description": "consequat Ut",
                "value": "http://1So_.A"
            },
            {
                "description": "ea",
                "value": "http://1CtmBpC"
            },
            {
                "description": "irure eiusmod in consectetur",
                "value": "http://1d"
            },
        ],
    }
    result = Author().dump(author)
    expected = {
        'given_name': 'qui',
        'display_name': 'ut deserunt',
        'websites': [
            'http://1So_.A',
            'http://1CtmBpC',
            'http://1d'
        ],
        'status': 'deceased',
        'public_emails': [
            'jh1eODzkDL@AKzwKXUQdjCtfLzMDlCfDIl.yf',
            'VUR3e@wpyAFFXWzuzGKYTMwAABYkz.nsm',
            'rK1tZBUNQQ@mRQxfP.cfey',
            'hMZ0VePfwN7lKl@EZUhLeIeFsIWIhSgZvh.onq',
            'xGxVc1-F@DpkGBmXIVnkkmRbKwJtKmUCznuE.bly',
        ],
        'blog': 'http://blog',
        'linkedin': 'http://linkedin',
        'twitter': 'http://twitter',
        'arxiv_categories': [
            'math.QA',
            'cond-mat.quant-gas',
            'cs.NE'
        ],
        'positions': [
            {
                'curated_relation': False,
                'current': True,
                'end_date': '1724-07-20',
                'institution': 'qui ea pariatur ut nisi',
                'record': {'$ref': 'http://180'}
            },
            {
                'curated_relation': False,
                'current': False,
                'end_date': '1770-04-16',
                'institution': 'irure',
                'rank': 'UNDERGRADUATE',
                'record': {'$ref': 'http://1'},
                'start_date': '1820-02-26'
            }
        ],
        'project_membership': [
            {
                'curated_relation': False,
                'current': False,
                'end_date': '2016',
                'name': 'pariatur',
                'record': {'$ref': 'http://1pmlJbh'},
                'start_date': '1984'
            },
            {
                'curated_relation': False,
                'current': False,
                'end_date': '1879',
                'name': 'veniam nisi officia dolore est',
                'record': {'$ref': 'http://15XGFW/h'},
                'start_date': '1788'
            },
        ],
        'advisors': [
            {
                'curated_relation': True,
                'degree_type': 'bachelor',
                'ids': [
                    {'schema': 'DESY', 'value': 'DESY-55924820881'},
                    {'schema': 'SCOPUS', 'value': '7039712595'},
                    {'schema': 'SCOPUS', 'value': '8752067273'}
                ],
                'name': 'occaecat qui sint in id',
                'record': {'$ref': 'http://1js40iZ'}
            },
            {
                'curated_relation': False,
                'degree_type': 'laurea',
                'ids': [{'schema': 'SCOPUS', 'value': '6344523811'}],
                'name': 'deserunt nisi in',
                'record': {'$ref': 'http://12XQ'}
            },
            {
                'curated_relation': False,
                'degree_type': 'master',
                'ids': [
                    {'schema': 'SCOPUS', 'value': '83771302666'},
                    {'schema': 'DESY', 'value': 'DESY-88'},
                    {'schema': 'DESY', 'value': 'DESY-6994808'},
                    {'schema': 'DESY', 'value': 'DESY-81200252953'}
                ],
                'name': 'deseru',
                'record': {'$ref': 'http://1U/_cD'}
            },
        ],
        'comments': 'proident do adipisicing pariatur incididunt'
    }
    assert expected == result.data
