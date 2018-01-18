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

from mock import patch, Mock
import pytest

from inspirehep.modules.migrator.tasks import add_citation_counts


@patch('inspirehep.modules.migrator.tasks.PersistentIdentifier')
def test_add_citation_counts_numeric_pid_type(mock_pid):
    mock_pid.query.filter.return_value.yield_per.return_value = [
        Mock(pid_value='123')]
    add_citation_counts()


@patch('inspirehep.modules.migrator.tasks.PersistentIdentifier')
def test_add_citation_counts_non_numeric_pid_type(mock_pid):
    mock_pid.query.filter.return_value.yield_per.return_value = [
        Mock(pid_value='abc')]
    with pytest.raises(ValueError):
        add_citation_counts()
