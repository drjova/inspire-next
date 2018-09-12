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

from marshmallow import Schema, fields, pre_dump, missing, post_load
from inspire_schemas.builders.authors import AuthorBuilder
from inspire_utils.record import get_value, get_values_for_schema


class Author(Schema):
    display_name = fields.Raw()
    family_name = fields.Raw()
    given_name = fields.Raw()
    native_names = fields.Raw()
    public_emails = fields.Raw()

    status = fields.Raw()
    arxiv_categories = fields.Raw()
    websites = fields.Raw()
    twitter = fields.Raw()
    blog = fields.Raw()
    linkedin = fields.Raw()

    positions = fields.Raw()
    project_membership = fields.Raw()
    advisors = fields.Raw()

    comments = fields.Raw()

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

    @post_load
    def build_author(self, data):
        author = AuthorBuilder()

        for advisor in data.get('advisors', []):
            name = advisor.get('name')
            degree_type = advisor.get('degree_type')
            author.add_advisor(name, None, degree_type)

        for arxiv_category in data.get('arxiv_categories', []):
            author.add_arxiv_category(arxiv_category)

        blog = data.get('blog')
        if blog:
            author.add_blog(blog)

        comments = data.get('comments')
        if comments:
            author.add_private_note(comments)

        display_name = data.get('display_name')
        if display_name:
            author.set_display_name(display_name)

        family_name = data.get('family_name')
        given_name = data.get('given_name')
        full_name = self.get_full_name(family_name, given_name)
        if full_name:
            author.set_name(full_name)

        linkedin = data.get('linkedin')
        if linkedin:
            author.add_linkedin(linkedin)

        native_name = data.get('native_name')
        if native_name:
            author.add_native_name(native_name)

        for position in data.get('positions', []):
            institution_name = position.get('institution')
            start_date = position.get('start_date')
            end_date = position.get('end_date')
            rank = position.get('rank')
            current = position.get('current')
            author.add_institution(
                institution_name, start_date, end_date, rank, None, False, current)

        for project in data.get('project_membership', []):
            name = project.get('name')
            start_date = project.get('start_date')
            end_date = project.get('end_date')
            current = project.get('current')
            author.add_project(name, None, start_date, end_date, False, current)

        for email in data.get('public_emails', []):
            author.add_email_address(email)

        status = data.get('status')
        if status:
            author.set_status(status)

        twitter = data.get('twitter')
        if twitter:
            author.add_twitter(twitter)

        for website in data.get('websites', []):
            author.add_url(website)

        return author.obj

    def get_full_name(self, given_name, family_name):
        if given_name and family_name:
            return '{} {}'.format(given_name, family_name)
        return given_name or family_name
