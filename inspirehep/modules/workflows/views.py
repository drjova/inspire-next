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

"""Callback blueprint for interaction with legacy."""

from __future__ import absolute_import, division, print_function

from os.path import join
from functools import wraps

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request
)
from flask.views import MethodView
from invenio_db import db
from inspire_schemas.api import validate
from invenio_workflows import workflow_object_class, ObjectStatus
from invenio_workflows.errors import WorkflowsMissingObject
from jsonschema.exceptions import ValidationError

from inspire_utils.urls import ensure_scheme
from inspirehep.modules.workflows.errors import CallbackMalformedError, \
    CallbackValidationError, CallbackWorkflowNotFoundError
from inspirehep.modules.workflows.models import WorkflowsPendingRecord
from inspirehep.modules.workflows.utils import \
    resolve_validation_callback_url, validation_errors


blueprint = Blueprint(
    'inspire_workflows',
    __name__,
    url_prefix="/callback",
    template_folder='templates',
    static_folder="static",
)


def make_response(data, code=200):
    """Make a response.

    Args:
        data(dict): the data for the response's payload.
        code(int): the http response code.
    """
    response = jsonify(**data)
    return response, code


def _get_base_url():
    """Return base URL for generated URLs for remote reference."""
    base_url = current_app.config.get(
        "LEGACY_ROBOTUPLOAD_URL",
        current_app.config["SERVER_NAME"],
    )
    return ensure_scheme(base_url)


def _continue_workflow(workflow_id, recid, result=None):
    """Small wrapper to continue a workflow.

    Will prepare the needed data from the record id and the result data if
    passed.

    :return: True if succeeded, False if the specified workflow id does not
        exist.
    """
    result = result if result is not None else {}
    base_url = _get_base_url()
    try:
        workflow_object = workflow_object_class.get(workflow_id)
    except WorkflowsMissingObject:
        current_app.logger.error(
            'No workflow object with the id %s could be found.',
            workflow_id,
        )
        return False

    workflow_object.extra_data['url'] = join(
        base_url,
        'record',
        str(recid)
    )
    workflow_object.extra_data['recid'] = recid
    workflow_object.data['control_number'] = recid
    workflow_object.extra_data['callback_result'] = result
    workflow_object.save()
    db.session.commit()
    workflow_object.continue_workflow(delayed=True)

    return True


def _find_and_continue_workflow(workflow_id, recid, result=None):
    workflow_found = _continue_workflow(
        workflow_id=workflow_id,
        recid=recid,
        result=result,
    )
    if not workflow_found:
        current_app.logger.warning(
            'The workflow %s was not found.',
            workflow_id,
        )
        return {
            'success': False,
            'message': 'workflow with id %s not found.' % workflow_id,
        }

    return {
        'success': True,
        'message': 'workflow with id %s continued.' % workflow_id,
    }


def _put_workflow_in_error_state(workflow_id, error_message, result):
    try:
        workflow_object = workflow_object_class.get(workflow_id)
    except WorkflowsMissingObject:
        current_app.logger.error(
            'No workflow object with the id %s could be found.',
            workflow_id,
        )
        return {
            'success': False,
            'message': 'workflow with id %s not found.' % workflow_id,
        }

    workflow_object.status = ObjectStatus.ERROR
    workflow_object.extra_data['callback_result'] = result
    workflow_object.extra_data['_error_msg'] = error_message
    workflow_object.save()
    db.session.commit()

    return {
        'success': True,
        'message': 'workflow %s updated with error.' % workflow_id,
    }


@blueprint.route('/workflows/webcoll', methods=['POST'])
def webcoll_callback():
    """Handle a callback from webcoll with the record ids processed.

    Expects the request data to contain a list of record ids in the
    recids field.

    Example:
        An example of callback::

            $ curl \\
                http://web:5000/callback/workflows/webcoll \\
                -H "Host: localhost:5000" \\
                -F 'recids=1234'


    """
    recids = dict(request.form).get('recids', [])
    pending_records = WorkflowsPendingRecord.query.filter(
        WorkflowsPendingRecord.record_id.in_(recids)
    ).all()
    response = {}
    for pending_record in pending_records:
        recid = int(pending_record.record_id)
        workflow_id = pending_record.workflow_id
        continue_response = _find_and_continue_workflow(
            workflow_id=workflow_id,
            recid=recid,
        )
        if continue_response['success']:
            current_app.logger.debug(
                'Successfully restarted workflow %s',
                workflow_id,
            )
            response[recid] = {
                'success': True,
                'message': 'Successfully restarted workflow %s' % workflow_id,
            }
        else:
            current_app.logger.debug(
                'Error restarting workflow %s: %s',
                workflow_id,
                continue_response['message'],
            )
            response[recid] = {
                'success': False,
                'message': continue_response['message'],
            }

        db.session.delete(pending_record)
        db.session.commit()

    return jsonify(response)


def _robotupload_has_error(result):
    recid = int(result.get('recid'))
    if not result.get('success'):
        message = result.get(
            'error_message',
            'No error message from robotupload.'
        )
    elif recid < 0:
        message = result.get(
            'error_message',
            'Failed to create record on robotupload.',
        )
    else:
        return False, ''

    return True, message


def _is_an_update(workflow_id):
    workflow_object = workflow_object_class.get(workflow_id)
    return bool(workflow_object.extra_data.get('is-update'))


def _parse_robotupload_result(result, workflow_id):
    response = {}
    recid = int(result.get('recid'))

    result_has_error, error_message = _robotupload_has_error(result)
    if result_has_error:
        response = {
            'success': False,
            'message': error_message,
        }
        return response

    already_pending_ones = WorkflowsPendingRecord.query.filter_by(
        record_id=recid,
    ).all()
    if already_pending_ones:
        current_app.logger.warning(
            'The record %s was already found on the pending list.',
            recid
        )
        response = {
            'success': False,
            'message': 'Recid %s already in pending list.' % recid,
        }
        return response

    if not _is_an_update(workflow_id):
        pending_entry = WorkflowsPendingRecord(
            workflow_id=workflow_id,
            record_id=recid,
        )
        db.session.add(pending_entry)
        db.session.commit()

        current_app.logger.debug(
            'Successfully added recid:workflow %s:%s to pending list.',
            recid,
            workflow_id,
        )

    continue_response = _find_and_continue_workflow(
        workflow_id=workflow_id,
        recid=recid,
        result=result,
    )
    if continue_response['success']:
        current_app.logger.debug(
            'Successfully restarted workflow %s',
            workflow_id,
        )
        response = {
            'success': True,
            'message': 'Successfully restarted workflow %s' % workflow_id,
        }
    else:
        current_app.logger.debug(
            'Error restarting workflow %s: %s',
            workflow_id,
            continue_response['message'],
        )
        response = {
            'success': False,
            'message': continue_response['message'],
        }

    return response


@blueprint.route('/workflows/robotupload', methods=['POST'])
def robotupload_callback():
    """Handle callback from robotupload.

    If robotupload was successful caches the workflow
    object id that corresponds to the uploaded record,
    so the workflow can be resumed when webcoll finish
    processing that record.
    If robotupload encountered an error sends an email
    to site administrator informing him about the error.

    Examples:
        An example of failed callback that did not get to create a recid (the
        "nonce" is the workflow id)::

            $ curl \\
                http://web:5000/callback/workflows/robotupload \\
                -H "Host: localhost:5000" \\
                -H "Content-Type: application/json" \\
                -d '{
                    "nonce": 1,
                    "results": [
                        {
                            "recid":-1,
                            "error_message": "Record already exists",
                            "success": false
                        }
                    ]
                }'

        One that created the recid, but failed later::

            $ curl \\
                http://web:5000/callback/workflows/robotupload \\
                -H "Host: localhost:5000" \\
                -H "Content-Type: application/json" \\
                -d '{
                    "nonce": 1,
                    "results": [
                        {
                            "recid":1234,
                            "error_message": "Unable to parse pdf.",
                            "success": false
                        }
                    ]
                }'

        A successful one::

            $ curl \\
                http://web:5000/callback/workflows/robotupload \\
                -H "Host: localhost:5000" \\
                -H "Content-Type: application/json" \\
                -d '{
                    "nonce": 1,
                    "results": [
                        {
                            "recid":1234,
                            "error_message": "",
                            "success": true
                        }
                    ]
                }'
    """

    request_data = request.get_json()
    workflow_id = request_data.get('nonce', '')
    results = request_data.get('results', [])
    responses = {}
    for result in results:
        recid = int(result.get('recid'))

        if recid in responses:
            # this should never happen
            current_app.logger.warning('Received duplicated recid: %s', recid)
            continue

        response = _parse_robotupload_result(
            result=result,
            workflow_id=workflow_id,
        )
        if not response['success']:
            error_set_result = _put_workflow_in_error_state(
                workflow_id=workflow_id,
                error_message='Error in robotupload: %s' % response['message'],
                result=result,
            )
            if not error_set_result['success']:
                response['message'] += (
                    '\nFailed to put the workflow in error state:%s' %
                    error_set_result['message']
                )

        responses[recid] = response

    return jsonify(responses)


def _validate_workflow_payload(keys):
    """Validate and get the workflow data from the request.

    It will first check if all the given keys are part of
    the request's payload, after will validate the ``metadata`` against
    the ``hep`` JSONSchema and finally it will pass the ``workflow_data``
    kwarg.

    Args:
        keys (list(str)): the keys to check if they exist.

    Raises:
        CallbackMalformedError: if any of the ``keys`` is missing from
            the request payload.
        CallbackValidationError: if the workflow ``metadata`` is not valid
            against ``hep`` JSONSchema.
    """
    workflow_data = request.get_json()

    # Check for missing keys
    for key in keys:
        if workflow_data.get(key) is None:
            raise CallbackMalformedError(key)

    # Check for validation errors
    try:
        validate(schema='hep', data=workflow_data['metadata'])
    except ValidationError:
        workflow_data['_extra_data']['validation_errors'] = \
            validation_errors(workflow_data['metadata'], 'hep')
        workflow_data['_extra_data']['callback_url'] = \
            resolve_validation_callback_url()
        raise CallbackValidationError(workflow_data)
    return workflow_data


def error_handler(f):
    """Decorator to handle callback exceptions."""

    @wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except CallbackMalformedError as error:
            return make_response(
                dict(error_code=error.error_code,
                     message=error.description),
                code=error.code
            )
        except CallbackWorkflowNotFoundError as error:
            return make_response(
                dict(error_code=error.error_code,
                     message=error.description),
                code=error.code
            )
        except CallbackValidationError as error:
            return make_response(
                dict(error_code=error.error_code,
                     message=error.description,
                     workflow=error.workflow),
                code=error.code
            )
    return inner


class ResolveValidationResource(MethodView):
    """Resolve validation error callback."""

    @error_handler
    def put(self):
        """Handle callback from validation errors.

        When validation errors occur, the workflow stops in ``ERROR`` state, to
        continue this endpoint is called.

        Args:
            workflow_data (dict): the workflow object send in the
                request's payload.

        Examples:
            An example of successful call:

                $ curl \\
                    http://web:5000/callback/workflows/resolve_validation_errors \\
                    -H "Host: localhost:5000" \\
                    -H "Content-Type: application/json" \\
                    -d '{
                        "_extra_data": {
                            ... extra data content
                        },
                        "id": 910648,
                        "metadata": {
                            "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
                            ... record content
                        }
                    }'

            The response:

                HTTP 200 OK

                {"mesage": "Workflow 910648 validated, continuing it."}


            A failed example:

                $ curl \\
                    http://web:5000/callback/workflows/resolve_validation_errors \\
                    -H "Host: localhost:5000" \\
                    -H "Content-Type: application/json" \\
                    -d '{
                        "_extra_data": {
                            ... extra data content
                        },
                        "id": 910648,
                        "metadata": {
                            "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
                            ... record content
                        }
                    }'

            The error response will contain the workflow that was passed, with the
            new validation errors:

                HTTP 400 Bad request

                {
                    "_extra_data": {
                        "validatior_errors": [
                            {
                                "path": ["path", "to", "error"],
                                "message": "required: ['missing_key1', 'missing_key2']"
                            }
                        ],
                        ... rest of extra data content
                    },
                    "id": 910648,
                    "metadata": {
                        "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
                        ... record content
                    }
                }
        """
        workflow_data = _validate_workflow_payload(
            ['metadata', '_extra_data', 'id'])
        workflow_id = workflow_data['id']

        try:
            workflow = workflow_object_class.get(workflow_id)
        except WorkflowsMissingObject:
            raise CallbackWorkflowNotFoundError(workflow_id)

        workflow.extra_data.pop('callback_url', None)
        workflow.extra_data.pop('validation_errors', None)

        workflow.data = workflow_data['metadata']
        workflow.save()
        db.session.commit()

        if workflow.status != ObjectStatus.COMPLETED:
            workflow.continue_workflow(delayed=True)

        data = {
            'message': 'Workflow {} validated.'.format(workflow.id),
        }
        return make_response(data)


callback_resolve_validation = ResolveValidationResource.as_view(
    'callback_resolve_validation')

blueprint.add_url_rule(
    '/workflows/resolve_validation_errors',
    view_func=callback_resolve_validation,
)
