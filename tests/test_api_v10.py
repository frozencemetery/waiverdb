
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import pytest
import json

def test_create_waiver(client, session):
    data = {
        'result_id': 123,
        'product_version': 'fool-1',
        'waived': True,
        'comment': 'it broke',
    }
    r = client.post('/api/v1.0/waivers/', data=json.dumps(data),
            content_type='application/json')
    res_data = json.loads(r.data)
    assert r.status_code == 201
    assert res_data['username'] == 'mjia'
    assert res_data['result_id'] == 123
    assert res_data['product_version'] == 'fool-1'
    assert res_data['waived'] == True
    assert res_data['comment'] == 'it broke'

def test_create_waiver_with_malformed_data(client):
    data = {
        'result_id': 'wrong id',
    }
    r = client.post('/api/v1.0/waivers/', data=json.dumps(data),
            content_type='application/json')
    res_data = json.loads(r.data)
    assert r.status_code == 400
    assert 'invalid literal for int()' in res_data['message']['result_id']
