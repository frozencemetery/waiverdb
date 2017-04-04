
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
import kerberos
import mock
import json
from werkzeug.exceptions import Unauthorized
import waiverdb.auth


class TestKerberosAuthentication(object):

    def test_keytab_file_is_not_set_should_raise_error(self):
        with pytest.raises(Unauthorized):
            request = mock.MagicMock()
            waiverdb.auth.get_user(request)

    def test_unauthorized(self, client, monkeypatch):
        monkeypatch.setenv('KRB5_KTNAME', '/etc/foo.keytab')
        r = client.post('/api/v1.0/waivers/', content_type='application/json')
        assert r.status_code == 401
        assert r.headers.get('www-authenticate') == 'Negotiate'

    @mock.patch('kerberos.authGSSServerInit', return_value=(kerberos.AUTH_GSS_COMPLETE, object()))
    @mock.patch('kerberos.authGSSServerStep', return_value=kerberos.AUTH_GSS_COMPLETE)
    @mock.patch('kerberos.authGSSServerResponse', return_value='STOKEN')
    @mock.patch('kerberos.authGSSServerUserName', return_value='foo@EXAMPLE.ORG')
    @mock.patch('kerberos.authGSSServerClean')
    @mock.patch('kerberos.getServerPrincipalDetails')
    def test_authorized(self, principal, clean, name, response, step, init,
                        client, monkeypatch, session):
        monkeypatch.setenv('KRB5_KTNAME', '/etc/foo.keytab')
        data = {
            'result_id': 123,
            'product_version': 'fool-1',
            'waived': True,
            'comment': 'it broke',
        }
        r = client.post('/api/v1.0/waivers/', data=json.dumps(data),
                        content_type='application/json',
                        headers={'Authorization': 'Negotiate CTOKEN'})
        assert r.status_code == 201
        assert r.headers.get('WWW-Authenticate') == 'negotiate STOKEN'
        res_data = json.loads(r.data.decode('utf-8'))
        assert res_data['username'] == 'foo'
