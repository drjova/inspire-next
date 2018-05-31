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

"""Marshmallow JSON schema."""

from __future__ import absolute_import, division, print_function

from inspire_dojson.utils import get_recid_from_ref, strip_empty_values
from inspire_utils.helpers import force_list
from marshmallow import Schema, fields, missing, pre_dump

from inspirehep.modules.records.utils import get_resolved_references


class RecordSchemaJSONUIV1(Schema):
    """Schema for record UI."""

    id = fields.Integer(attribute='pid.pid_value')
    metadata = fields.Raw()
    display = fields.Raw()
    links = fields.Raw()
    created = fields.Str()
    updated = fields.Str()


class MetadataReferencesSchemaItemV1(Schema):
    arxiv_eprints = fields.List(fields.Dict())
    authors = fields.Method('get_authors')
    collaborations = fields.List(fields.Dict())
    control_number = fields.Int()
    dois = fields.List(fields.Dict())
    publication_info = fields.List(fields.Dict())
    titles = fields.List(fields.Dict())

    def get_authors(self, data):
        authors = data.get('authors', [])
        return authors[:10] or missing


class MetadataReferencesSchemaUIV1(Schema):
    references = fields.Nested(
        MetadataReferencesSchemaItemV1, many=True, dump_only=True)


class ReferencesSchemaJSONUIV1(RecordSchemaJSONUIV1):
    """Schema for references."""
    metadata = fields.Nested(MetadataReferencesSchemaUIV1, dump_only=True)

    @pre_dump
    def pre_process(self, data):
        resolved = []
        references = data['metadata'].get('references')
        if references:
            reference_records = self.resolve_records(references)

            for reference in references:
                if 'record' in reference:
                    reference_record_id = get_recid_from_ref(
                        reference.get('record'))
                    reference_record = reference_records.get(
                        reference_record_id)
                    if reference_record:
                        resolved.append(reference_record)
                        break

                reference = self.format_references(reference)
                if reference:
                    resolved.append(reference)

        data['metadata']['references'] = resolved
        return data

    def resolve_records(self, references):
        ids = [
            get_recid_from_ref(reference['record'])
            for reference in references if 'record' in reference
        ]
        resolved_records = get_resolved_references(ids)
        return {
            record['control_number']: record
            for record in resolved_records
        }

    def format_references(self, reference):
        reference.update(reference.get('reference', {}))
        reference.pop('reference', None)
        reference.update({
            'publication_info': self.prepare_publication_info(
                reference.get('publication_info', {})),
            'arxiv_eprints': self.prepare_arxiv_eprint(
                reference.get('arxiv_eprint')),
            'collaborations': self.prepare_collaborations(
                reference.get('collaborations', [])),
            'dois': self.prepare_dois(reference.get('dois', [])),
            'titles': self.prepare_titles(reference.get('title', [])),
        })
        reference = strip_empty_values(reference)
        return self.only_meaningful_data(reference)

    def only_meaningful_data(self, reference):
        if any(key in reference for
               key in ['titles', 'authors', 'publication_info']):
            return reference

    def prepare_publication_info(self, publication_info):
        return force_list(
            publication_info
            if {'journal_title', 'pubinfo_freetext'}.issubset(publication_info.keys())
            else None
        )

    def prepare_arxiv_eprint(self, arxiv_eprint):
        if not arxiv_eprint:
            return
        return [{'value': arxiv_eprint}]

    def prepare_titles(self, titles):
        return force_list(titles)

    def prepare_dois(self, dois):
        return [{'value': doi} for doi in dois]

    def prepare_collaborations(self, collaborations):
        return [
            {'value': collaboration} for collaboration in collaborations]
