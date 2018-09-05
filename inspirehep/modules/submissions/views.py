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

"""Submissions views."""

from __future__ import absolute_import, division, print_function

import copy

from flask import Blueprint, jsonify, request
from flask.views import MethodView
from flask_login import current_user

from invenio_db import db
from invenio_workflows import workflow_object_class, start

from inspirehep.utils.record_getter import get_db_record
from inspirehep.modules.pidstore.utils import get_pid_type_from_endpoint

import json

from .serializers.json import author_serializer

blueprint = Blueprint(
    'inspirehep_submissions',
    __name__,
    template_folder='templates',
    url_prefix='/submissions',
)

ENDPOINT_TO_DATA_TYPE = {
    'literature': 'hep',
    'authors': 'authors',
}

ENDPOINT_TO_WORKFLOW_NAME = {
    'literature': 'article',
    'authors': 'author',
}

ENDPOINT_TO_FORM_SERIALIZER = {
    'authors': author_serializer,
}


class SubmissionsResource(MethodView):

    def get(self, endpoint, pid_value=None):
        pid_type = get_pid_type_from_endpoint(endpoint)
        record = get_db_record(pid_type, pid_value)
        serializer = ENDPOINT_TO_FORM_SERIALIZER[endpoint]
        serialized = serializer().dump(record.dumps())
        return jsonify({'data': serialized.data})

    def post(self, endpoint, pid_value=None):
        submission_data = json.loads(request.data)
        serializer = ENDPOINT_TO_FORM_SERIALIZER[endpoint]
        serialized_data = serializer().load(submission_data).data
        workflow_object_id = self.start_workflow_for_submission(endpoint,
                                                                serialized_data)
        return jsonify({'workflow_object_id': workflow_object_id})

    def put(self, endpoint, pid_value=None):
        submission_data = json.loads(request.data)
        serializer = ENDPOINT_TO_FORM_SERIALIZER[endpoint]
        serialized_data = serializer().load(submission_data).data
        serialized_data['control_number'] = int(pid_value)
        workflow_object_id = self.start_workflow_for_submission(
            endpoint, serialized_data, True)
        return jsonify({'workflow_object_id': workflow_object_id})

    def start_workflow_for_submission(self, endpoint, serialized_data, is_update=False):

        workflow_object = workflow_object_class.create(
            data={},
            id_user=current_user.get_id(),
            data_type=ENDPOINT_TO_DATA_TYPE[endpoint]
        )
        workflow_object.data = serialized_data
        workflow_object.extra_data['is-update'] = is_update

        # why is this required, rather than being a default behaviour
        workflow_object.extra_data['source_data'] = {
            'data': copy.deepcopy(workflow_object.data),
            'extra_data': copy.deepcopy(workflow_object.extra_data)
        }

        workflow_object.save()
        db.session.commit()

        workflow_object_id = workflow_object.id

        start.delay(
            ENDPOINT_TO_WORKFLOW_NAME[endpoint], object_id=workflow_object.id)

        return workflow_object_id


submissions_view = SubmissionsResource.as_view(
    'submissions_view'
)

blueprint.add_url_rule(
    '/<endpoint>',
    view_func=submissions_view,
)
blueprint.add_url_rule(
    '/<endpoint>/<int:pid_value>',
    view_func=submissions_view,
)
