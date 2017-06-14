# SPDX-License-Identifier: GPL-2.0+

import pytest
import kerberos
import mock
import json
from werkzeug.exceptions import Unauthorized
import waiverdb.auth
import flask_oidc


@pytest.mark.usefixtures('enable_kerberos')
class TestKerberosAuthentication(object):

    def test_keytab_file_is_not_set_should_raise_error(self):
        with pytest.raises(Unauthorized):
            request = mock.MagicMock()
            headers = {'Authorization': "babablaba"}
            request.headers.return_value = mock.MagicMock(spec_set=dict)
            request.headers.__getitem__.side_effect = headers.__getitem__
            request.headers.__setitem__.side_effect = headers.__setitem__
            request.headers.__contains__.side_effect = headers.__contains__
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


class TestOIDCAuthentication(object):

    def test_get_user_without_token(self, session):
        with pytest.raises(Unauthorized) as excinfo:
            request = mock.MagicMock()
            waiverdb.auth.get_user(request)
        assert "No 'Authorization' header found" in excinfo.value.get_description()

    @mock.patch.object(flask_oidc.OpenIDConnect, '_get_token_info')
    def test_get_user_with_invalid_token(self, mocked_get_token, session):
        # http://vsbattles.wikia.com/wiki/Son_Goku
        name = 'Son Goku'
        mocked_get_token.return_value = {'active': False, 'username': name,
                                         'scope': 'openid waiverdb_scope'}
        headers = {'Authorization': 'Bearer invalid'}
        request = mock.MagicMock()
        request.headers.return_value = mock.MagicMock(spec_set=dict)
        request.headers.__getitem__.side_effect = headers.__getitem__
        request.headers.__setitem__.side_effect = headers.__setitem__
        request.headers.__contains__.side_effect = headers.__contains__
        with pytest.raises(Unauthorized) as excinfo:
            waiverdb.auth.get_user(request)
        assert 'Token required but invalid' in excinfo.value.get_description()

    @mock.patch.object(flask_oidc.OpenIDConnect, '_get_token_info')
    def test_get_user_good(self, mocked_get_token, session):
        # http://vsbattles.wikia.com/wiki/Son_Goku
        name = 'Son Goku'
        mocked_get_token.return_value = {'active': True, 'username': name,
                                         'scope': 'openid waiverdb_scope'}
        headers = {'Authorization': 'Bearer foobar'}
        request = mock.MagicMock()
        request.headers.return_value = mock.MagicMock(spec_set=dict)
        request.headers.__getitem__.side_effect = headers.__getitem__
        request.headers.__setitem__.side_effect = headers.__setitem__
        request.headers.__contains__.side_effect = headers.__contains__
        user, header = waiverdb.auth.get_user(request)
        assert user == name
