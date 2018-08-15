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

from marshmallow import Schema, fields, pre_dump, missing
from inspire_utils.record import get_value, get_values_for_schema


class Author(Schema):
    # dump
    display_name = fields.Raw(dump_only=True)
    family_name = fields.Raw(dump_only=True)
    given_name = fields.Raw(dump_only=True)
    native_names = fields.Raw(dumps_only=True)
    public_emails = fields.Raw(dumps_only=True)

    status = fields.Raw(dump_only=True)
    arxiv_categories = fields.Raw(dump_only=True)
    websites = fields.Raw(dump_only=True)
    twitter = fields.Raw(dump_only=True)
    blog = fields.Raw(dump_only=True)
    linkedin = fields.Raw(dump_only=True)

    positions = fields.Raw(dump_only=True)
    project_membership = fields.Raw(dump_only=True)
    advisors = fields.Raw(dump_only=True)

    comments = fields.Raw(dumps_only=True)

    @pre_dump
    def before_dump(self, data):
        author_dict = {}

        given_name, family_name = self.get_name_splitted(data)
        author_dict.update({
            'advisors': get_value(data, 'advisors', default=missing),
            'arxiv_categories': get_value(data, 'arxiv_categories', default=missing),
            'blog': self.get_first_or_missing(get_values_for_schema(data.get('ids', []), 'BLOG')),
            'comments': get_value(data, '_private_notes[0].value', default=missing),
            'display_name': get_value(data, 'name.preferred_name', default=missing),
            'family_name': self.get_value_or_missing(family_name),
            'given_name': self.get_value_or_missing(given_name),
            'linkedin': self.get_first_or_missing(get_values_for_schema(data.get('ids', []), 'LINKEDIN')),
            'native_name': get_value(data, 'name.native_names[0]', default=missing),
            'positions': get_value(data, 'positions', default=missing),
            'project_membership': get_value(data, 'project_membership', default=missing),
            'public_emails': get_value(data, 'email_addresses.value', default=missing),
            'status': get_value(data, 'status', default=missing),
            'twitter': self.get_first_or_missing(get_values_for_schema(data.get('ids', []), 'TWITTER')),
            'websites': get_value(data, 'urls.value', default=missing),
        })

        return author_dict

    def get_name_splitted(self, data):
        name = get_value(data, 'name.value')
        if name:
            first, last = name.split(' ')
            return first, last

        return missing, missing

    def get_value_or_missing(self, value):
        if value:
            return value
        return missing

    def get_first_or_missing(self, value):
        if value:
            return value.pop()
        return missing
