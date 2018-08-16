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

"""Submissions views."""

from __future__ import absolute_import, division, print_function

from flask import Blueprint, jsonify
from flask.views import MethodView

from inspirehep.utils.record_getter import get_db_record

from .serializers.json import author_serializer

blueprint = Blueprint(
    'inspirehep_submissions',
    __name__,
    template_folder='templates',
    url_prefix='/submissions',
)


class SubmissionsResource(MethodView):

    def get(self, name, pid_value=None):
        record = get_db_record('aut', pid_value)
        serialized = author_serializer().dump(record.dumps())
        return jsonify({'data': serialized.data})


submissions_view = SubmissionsResource.as_view(
    'submissions_view'
)

blueprint.add_url_rule(
    '/<name>',
    view_func=submissions_view,
)
blueprint.add_url_rule(
    '/<name>/<int:pid_value>',
    view_func=submissions_view,
)
