
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

import os
import pytest
import requests


@pytest.fixture(scope='session')
def waiverdb_url():
    if 'WAIVERDB_TEST_URL' not in os.environ:
        raise AssertionError('WAIVERDB_TEST_URL=http://example.com/ '
                             'must be set in the environment')
    url = os.environ['WAIVERDB_TEST_URL']
    assert url.endswith('/')
    return url


@pytest.fixture(scope='session')
def requests_session(request):
    s = requests.Session()
    request.addfinalizer(s.close)
    return s
