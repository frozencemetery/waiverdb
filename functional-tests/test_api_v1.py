
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


def test_get_waivers(waiverdb_url, requests_session):
    response = requests_session.get(waiverdb_url + 'api/v1.0/waivers/')
    response.raise_for_status()
    assert response.json()['data'] == []
