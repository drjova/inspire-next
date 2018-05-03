# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# Free Software Foundation, either version 3 of the License, or
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

"""Tests for merge and resolve merge conflicts."""

from __future__ import absolute_import, division, print_function

from mock import patch
import json
import pytest

from invenio_workflows import (
    ObjectStatus,
    WorkflowEngine,
    start,
)

from inspirehep.modules.workflows.utils import insert_wf_record_source, read_wf_record_source

from factories.db.invenio_records import TestRecordMetadata


RECORD_WITHOUT_CONFLICTS = {
    '$schema': 'https://labs.inspirehep.net/schemas/records/hep.json',
    'titles': [
        {
            'title': 'Update without conflicts title.'
        },
    ],
    'document_type': ['article'],
    '_collections': ['Literature'],
    'acquisition_source': {'source': 'arXiv'},
}

RECORD_WITH_CONFLICTS = {
    '$schema': 'https://labs.inspirehep.net/schemas/records/hep.json',
    'titles': [
        {
            'title': 'Update with conflicts title.'
        },
    ],
    'document_type': ['article'],
    '_collections': ['Literature'],
    'acquisition_source': {'source': 'arXiv'},
    'collaborations': [
        {
            'record':
                {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/684121'
                },
            'value': 'ALICE'
        },
    ],
}

ARXIV_ROOT = {
    '$schema': 'https://labs.inspirehep.net/schemas/records/hep.json',
    'titles': [
        {
            'title': 'Root title.'
        },
    ],
    'document_type': ['article'],
    '_collections': ['Literature'],
    'acquisition_source': {'source': 'arXiv'},
    'collaborations': [
        {
            'record':
                {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/684121'
                },
            'value': 'ALICE'
        },
    ],
}


@pytest.fixture
def enable_merge_on_update(workflow_app):
    with patch.dict(workflow_app.config, {'FEATURE_FLAG_ENABLE_MERGER': True}):
        yield


@pytest.fixture
def disable_file_upload(workflow_app):
    with patch.dict(workflow_app.config, {'RECORDS_SKIP_FILES': True}):
        yield


def test_merge_with_disabled_merge_on_update_feature_flag(workflow_app, disable_file_upload):
    with patch.dict(workflow_app.config, {'FEATURE_FLAG_ENABLE_MERGER': False}):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json')

        record_update = RECORD_WITHOUT_CONFLICTS
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        assert obj.status == ObjectStatus.COMPLETED

        assert obj.extra_data.get('callback_url') is None
        assert obj.extra_data.get('conflicts') is None
        assert obj.extra_data.get('merged') is True
        assert obj.extra_data.get('merger_root') is None

        updated_root = read_wf_record_source(factory.record_metadata.id, 'arxiv')
        assert updated_root is None


def test_merge_with_conflicts_rootful(workflow_app, enable_merge_on_update, disable_file_upload):
    with patch('inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json')

        record_update = RECORD_WITH_CONFLICTS
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        # By default the root is {}.

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')

        assert obj.status == ObjectStatus.HALTED
        assert len(conflicts) == 1

        assert obj.extra_data.get('callback_url') is not None
        assert obj.extra_data.get('is-update') is True
        assert obj.extra_data['merger_root'] == record_update


def test_merge_without_conflicts_rootful(workflow_app, enable_merge_on_update, disable_file_upload):
    with patch('inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json')

        record_update = RECORD_WITH_CONFLICTS
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        ARXIV_ROOT.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        insert_wf_record_source(json=ARXIV_ROOT, record_uuid=factory.record_metadata.id, source='arxiv')

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')

        assert obj.status == ObjectStatus.COMPLETED
        assert not conflicts

        assert obj.extra_data.get('callback_url') is None
        assert obj.extra_data.get('is-update') is True

        updated_root = read_wf_record_source(factory.record_metadata.id, 'arxiv')
        assert updated_root.json == record_update


def test_merge_without_conflicts_callback_url(workflow_app, enable_merge_on_update, disable_file_upload):
    with patch('inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json')

        record_update = RECORD_WITHOUT_CONFLICTS
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')

        url = 'http://localhost:5000/callback/workflows/resolve_merge_conflicts'

        assert obj.status == ObjectStatus.COMPLETED
        assert conflicts is None
        assert obj.extra_data.get('is-update') is True

        updated_root = read_wf_record_source(factory.record_metadata.id, 'arxiv')
        assert updated_root.json == record_update

        payload = {
            'id': obj.id,
            'metadata': obj.data,
            '_extra_data': obj.extra_data
        }

        with workflow_app.test_client() as client:
            response = client.put(
                url,
                data=json.dumps(payload),
                content_type='application/json',
            )

        assert response.status_code == 400


def test_merge_with_conflicts_callback_url(workflow_app, enable_merge_on_update, disable_file_upload):
    with patch('inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json')

        record_update = RECORD_WITH_CONFLICTS
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')

        expected_url = 'http://localhost:5000/callback/workflows/resolve_merge_conflicts'

        assert obj.status == ObjectStatus.HALTED
        assert expected_url == obj.extra_data.get('callback_url')
        assert len(conflicts) == 1

        assert obj.extra_data.get('is-update') is True
        assert obj.extra_data['merger_root'] == record_update

        payload = {
            'id': obj.id,
            'metadata': obj.data,
            '_extra_data': obj.extra_data
        }

        with workflow_app.test_client() as client:
            response = client.put(
                obj.extra_data.get('callback_url'),
                data=json.dumps(payload),
                content_type='application/json',
            )

        data = json.loads(response.get_data())
        expected_message = 'Workflow {} has been saved with conflicts.'.format(obj.id)

        assert response.status_code == 200
        assert expected_message == data['message']

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        assert obj.status == ObjectStatus.HALTED

        updated_root = read_wf_record_source(factory.record_metadata.id, 'arxiv')
        assert updated_root is None


def test_merge_with_conflicts_callback_url_and_resolve(workflow_app, enable_merge_on_update, disable_file_upload):
    with patch('inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json')

        record_update = RECORD_WITH_CONFLICTS
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')

        expected_url = 'http://localhost:5000/callback/workflows/resolve_merge_conflicts'

        assert obj.status == ObjectStatus.HALTED
        assert expected_url == obj.extra_data.get('callback_url')
        assert len(conflicts) == 1

        assert obj.extra_data.get('is-update') is True
        assert obj.extra_data['merger_root'] == record_update

        # resolve conflicts
        obj.data['collaborations'] = factory.record_metadata.json.get('collaborations')
        del obj.extra_data['conflicts']

        payload = {
            'id': obj.id,
            'metadata': obj.data,
            '_extra_data': obj.extra_data
        }

        with workflow_app.test_client() as client:
            response = client.put(
                obj.extra_data.get('callback_url'),
                data=json.dumps(payload),
                content_type='application/json',
            )
        assert response.status_code == 200

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')

        assert obj.status == ObjectStatus.COMPLETED
        assert conflicts is None

        assert obj.extra_data.get('approved') is True
        assert obj.extra_data.get('is-update') is True
        assert obj.extra_data.get('merged') is True

        updated_root = read_wf_record_source(factory.record_metadata.id, 'arxiv')
        assert updated_root.json == record_update


def test_merge_callback_url_with_malformed_workflow(workflow_app, enable_merge_on_update, disable_file_upload):
    with patch('inspire_json_merger.config.ArxivOnArxivOperations.conflict_filters', ['acquisition_source.source']):
        factory = TestRecordMetadata.create_from_file(
            __name__, 'merge_record_arxiv.json')

        record_update = RECORD_WITH_CONFLICTS
        record_update.update({
            'arxiv_eprints': factory.record_metadata.json.get('arxiv_eprints')
        })

        eng_uuid = start('article', [record_update])

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        conflicts = obj.extra_data.get('conflicts')

        expected_url = 'http://localhost:5000/callback/workflows/resolve_merge_conflicts'

        assert obj.status == ObjectStatus.HALTED
        assert expected_url == obj.extra_data.get('callback_url')
        assert len(conflicts) == 1

        assert obj.extra_data.get('is-update') is True
        assert obj.extra_data['merger_root'] == record_update

        payload = {
            'id': obj.id,
            'metadata': 'Jessica Jones',
            '_extra_data': 'Frank Castle'
        }

        with workflow_app.test_client() as client:
            response = client.put(
                obj.extra_data.get('callback_url'),
                data=json.dumps(payload),
                content_type='application/json',
            )

        data = json.loads(response.get_data())
        expected_message = 'The workflow request is malformed.'

        assert response.status_code == 400
        assert expected_message == data['message']

        eng = WorkflowEngine.from_uuid(eng_uuid)
        obj = eng.objects[0]

        assert obj.status == ObjectStatus.HALTED
        assert obj.extra_data.get('callback_url') is not None
        assert obj.extra_data.get('conflicts') is not None
        assert obj.extra_data['merger_root'] is not None

        updated_root = read_wf_record_source(factory.record_metadata.id, 'arxiv')
        assert updated_root is None
