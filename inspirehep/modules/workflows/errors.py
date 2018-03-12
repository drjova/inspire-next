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

from invenio_workflows.errors import WorkflowsError


class DownloadError(WorkflowsError):

    """Error representing a failed download in a workflow."""


class MergeError(WorkflowsError):

    """Error representing a failed merge in a workflow."""


class CallbackError(WorkflowsError):
    """Callback exception."""

    code = 400
    description = 'Workflow callback error.'


class CallbackMalformedError(CallbackError):
    """Malformed request exception."""

    error_code = 'MALFORMED'

    def __init__(self, key, **kwargs):
        """Initialize exception."""
        super(CallbackMalformedError, self).__init__(**kwargs)
        self.description = 'Malformed workflow, "{}" key was not found.'.format(
            key)


class CallbackWorkflowNotFoundError(CallbackError):
    """Workflow not found exception."""

    code = 404
    error_code = 'WORKFLOW_NOT_FOUND'

    def __init__(self, workflow_id, **kwargs):
        """Initialize exception."""
        super(CallbackWorkflowNotFoundError, self).__init__(**kwargs)
        self.description = 'The workflow with id "{}" was not found.'.format(
            workflow_id)


class CallbackValidationError(CallbackError):
    """Validation error exception."""

    error_code = 'VALIDATION_ERROR'
    description = 'Validation error.'

    def __init__(self, workflow_data, **kwargs):
        """Initialize exception."""
        super(CallbackValidationError, self).__init__(**kwargs)
        self.workflow = workflow_data
