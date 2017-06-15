# SPDX-License-Identifier: GPL-2.0+

import json
from .utils import create_waiver
import datetime
from mock import patch


@patch('waiverdb.auth.get_user', return_value=('foo', {}))
def test_create_waiver(mocked_get_user, client, session, monkeypatch):
    data = {
        'result_id': 123,
        'product_version': 'fool-1',
        'waived': True,
        'comment': 'it broke',
    }
    r = client.post('/api/v1.0/waivers/', data=json.dumps(data),
                    content_type='application/json')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 201
    assert res_data['username'] == 'foo'
    assert res_data['result_id'] == 123
    assert res_data['product_version'] == 'fool-1'
    assert res_data['waived'] is True
    assert res_data['comment'] == 'it broke'


@patch('waiverdb.auth.get_user', return_value=('foo', {}))
def test_create_waiver_with_malformed_data(mocked_get_user, client):
    data = {
        'result_id': 'wrong id',
    }
    r = client.post('/api/v1.0/waivers/', data=json.dumps(data),
                    content_type='application/json')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 400
    assert 'invalid literal for int()' in res_data['message']['result_id']


def test_get_waiver(client, session):
    # create a new waiver
    waiver = create_waiver(session, result_id=123, username='foo',
                           product_version='foo-1', comment='bla bla bla')
    r = client.get('/api/v1.0/waivers/%s' % waiver.id)
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert res_data['username'] == waiver.username
    assert res_data['result_id'] == waiver.result_id
    assert res_data['product_version'] == waiver.product_version
    assert res_data['waived'] is True
    assert res_data['comment'] == waiver.comment


def test_404_for_nonexistent_waiver(client, session):
    r = client.get('/api/v1.0/waivers/foo')
    assert r.status_code == 404


def test_get_waivers(client, session):
    for i in range(0, 10):
        create_waiver(session, result_id=i, username='foo %d' % i,
                      product_version='foo-%d' % i, comment='bla bla bla')
    r = client.get('/api/v1.0/waivers/')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 10


def test_pagination_waivers(client, session):
    for i in range(0, 30):
        create_waiver(session, result_id=i, username='foo %d' % i,
                      product_version='foo-%d' % i, comment='bla bla bla')
    r = client.get('/api/v1.0/waivers/?page=2')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 10
    assert '/waivers/?page=1' in res_data['prev']
    assert '/waivers/?page=3' in res_data['next']
    assert '/waivers/?page=1' in res_data['first']
    assert '/waivers/?page=3' in res_data['last']


def test_obsolete_waivers_are_excluded_by_default(client, session):
    create_waiver(session, result_id=123, username='foo',
                  product_version='foo-1')
    new_waiver = create_waiver(session, result_id=123, username='foo',
                               product_version='foo-1', waived=False)
    r = client.get('/api/v1.0/waivers/')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['id'] == new_waiver.id
    assert res_data['data'][0]['waived'] == new_waiver.waived


def test_get_obsolete_waivers(client, session):
    old_waiver = create_waiver(session, result_id=123, username='foo',
                               product_version='foo-1')
    new_waiver = create_waiver(session, result_id=123, username='foo',
                               product_version='foo-1', waived=False)
    r = client.get('/api/v1.0/waivers/?include_obsolete=1')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 2
    assert res_data['data'][0]['id'] == new_waiver.id
    assert res_data['data'][1]['id'] == old_waiver.id


def test_filtering_waivers_by_result_id(client, session):
    create_waiver(session, result_id=123, username='foo-1', product_version='foo-1')
    create_waiver(session, result_id=234, username='foo-2', product_version='foo-1')
    r = client.get('/api/v1.0/waivers/?result_id=123')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['result_id'] == 123


def test_filtering_waivers_by_multiple_result_ids(client, session):
    create_waiver(session, result_id=123, username='foo-1', product_version='foo-1')
    create_waiver(session, result_id=234, username='foo-2', product_version='foo-1')
    create_waiver(session, result_id=345, username='foo-2', product_version='foo-1')
    r = client.get('/api/v1.0/waivers/?result_id=123,345')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 2
    assert res_data['data'][0]['result_id'] == 345
    assert res_data['data'][1]['result_id'] == 123


def test_filtering_waivers_by_product_version(client, session):
    create_waiver(session, result_id=123, username='foo-1', product_version='release-1')
    create_waiver(session, result_id=124, username='foo-1', product_version='release-2')
    r = client.get('/api/v1.0/waivers/?product_version=release-1')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['product_version'] == 'release-1'


def test_filtering_waivers_by_username(client, session):
    create_waiver(session, result_id=123, username='foo', product_version='foo-1')
    create_waiver(session, result_id=124, username='bar', product_version='foo-2')
    r = client.get('/api/v1.0/waivers/?username=foo')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['username'] == 'foo'


def test_filtering_waivers_by_since(client, session):
    before1 = (datetime.datetime.utcnow() - datetime.timedelta(seconds=100)).isoformat()
    before2 = (datetime.datetime.utcnow() - datetime.timedelta(seconds=99)).isoformat()
    after = (datetime.datetime.utcnow() + datetime.timedelta(seconds=100)).isoformat()
    create_waiver(session, result_id=123, username='foo', product_version='foo-1')
    r = client.get('/api/v1.0/waivers/?since=%s' % before1)
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['result_id'] == 123

    r = client.get('/api/v1.0/waivers/?since=%s,%s' % (before1, after))
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['result_id'] == 123

    r = client.get('/api/v1.0/waivers/?since=%s' % (after))
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 0

    r = client.get('/api/v1.0/waivers/?since=%s,%s' % (before1, before2))
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 0


def test_jsonp(client, session):
    waiver = create_waiver(session, result_id=123, username='foo', product_version='foo-1')
    r = client.get('/api/v1.0/waivers/%s?callback=jsonpcallback' % waiver.id)
    assert r.mimetype == 'application/javascript'
    assert 'jsonpcallback' in r.get_data(as_text=True)
