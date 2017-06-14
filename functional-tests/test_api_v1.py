# SPDX-License-Identifier: GPL-2.0+


def test_get_waivers(waiverdb_url, requests_session):
    response = requests_session.get(waiverdb_url + 'api/v1.0/waivers/')
    response.raise_for_status()
    assert response.json()['data'] == []
