# SPDX-License-Identifier: GPL-2.0+

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
