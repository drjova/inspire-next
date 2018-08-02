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

from marshmallow import Schema, pre_dump, fields

from inspirehep.modules.records.serializers.fields.list_with_limit import ListWithLimit

from .author import AuthorSchemaV1
from .publication_info_item import PublicationInfoItemSchemaV1


class ReferenceItemSchemaV1(Schema):
    authors = ListWithLimit(fields.Nested(AuthorSchemaV1, dump_only=True), limit=10)
    control_number = fields.Int()
    label = fields.String()
    publication_info = fields.List(
        fields.Nested(PublicationInfoItemSchemaV1), dump_only=True)

    @pre_dump
    def get_record_or_reference(self, data):
        if 'record' in data:
            data['record'].update({
                'label': data['reference'].get('label')
            })
            return data['record']
        elif 'reference' in data:
            return data['reference']
