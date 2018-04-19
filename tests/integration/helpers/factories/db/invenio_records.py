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
import pkg_resources
import os
import uuid
import random

from invenio_pidstore.models import PersistentIdentifier
from invenio_records.models import RecordMetadata
from invenio_search import current_search_client as es

from .base import TestBaseModel, generate_random_string


def generate_record(data):
    """Generate a valid record."""
    required_record = {
        '$schema': 'http://localhost:5000/schemas/record/hep.json',
        'titles': [
            {
                'title': generate_random_string(60)
            }
        ],
        'document_type': ['article'],
        '_collections': ['Literature'],
        'control_number': random.randint(1, 9) * 5
    }
    required_record.update(data)
    return required_record


class TestRecord(TestBaseModel):
    """Create Record instances.

    Example:
        >>> from factories.db.invenio_records import TestRecord
        >>> factory = TestRecord.create_from_kwargs(json={})
        >>> factory.record
        <RecordMetadata (transient 4661300240)>
        >>> factory.record.json
    """
    model_class = RecordMetadata

    @classmethod
    def create_from_kwargs(cls, index=True, create_pid=True, **kwargs):
        instance = cls()

        updated_kwargs = kwargs.copy()
        if not kwargs.pop('id', None):
            updated_kwargs['id'] = uuid.uuid4()

        updated_kwargs['json'] = generate_record(kwargs.pop('json', {}))

        instance.record = super(TestRecord, cls).create_from_kwargs(updated_kwargs)

        if index:
            es.index(
                index='records-hep',
                doc_type='hep',
                body=instance.record.json,
                params={}
            )
            es.indices.refresh('records-hep')

        if create_pid:
            PersistentIdentifier.create(
                object_type='rec',
                object_uuid=instance.record.id,
                pid_type='lit',
                pid_value=instance.record.json.get('control_number'),
            )
        return instance

    @classmethod
    def create_from_file(cls, module_name, filename, index=True, create_pid=True):
        """Create Record instance from file.

        Note:
            It will look inside the ``fixtures`` directory for the given module.

        Example:
            >>> from factories.db.invenio_records import TestRecord
            >>> factory = TestRecord.create_from_file(__name__, filename)
            >>> factory.record
            <RecordMetadata (transient 4661300240)>
            >>> factory.record.json
        """
        path = pkg_resources.resource_filename(
            module_name, os.path.join('fixtures', filename))

        data = json.load(open(path))
        return cls.create_from_kwargs(
            index=index, create_pid=create_pid, json=data)
