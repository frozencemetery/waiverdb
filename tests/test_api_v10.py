# SPDX-License-Identifier: GPL-2.0+

import json
from .utils import create_waiver
import datetime
from requests import ConnectionError, HTTPError
from mock import patch, Mock
from waiverdb import __version__


@patch('waiverdb.auth.get_user', return_value=('foo', {}))
def test_create_waiver(mocked_get_user, client, session):
    data = {
        'subject': {'subject.test': 'subject'},
        'testcase': 'testcase1',
        'product_version': 'fool-1',
        'waived': True,
        'comment': 'it broke',
    }
    r = client.post('/api/v1.0/waivers/', data=json.dumps(data),
                    content_type='application/json')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 201
    assert res_data['username'] == 'foo'
    assert res_data['subject'] == {'subject.test': 'subject'}
    assert res_data['testcase'] == 'testcase1'
    assert res_data['product_version'] == 'fool-1'
    assert res_data['waived'] is True
    assert res_data['comment'] == 'it broke'


@patch('waiverdb.api_v1.get_resultsdb_result')
@patch('waiverdb.auth.get_user', return_value=('foo', {}))
def test_create_waiver_legacy(mocked_get_user, mocked_resultsdb, client, session):
    mocked_resultsdb.return_value = {
        'data': {
            'type': ['koji_build'],
            'item': ['somebuild'],
        },
        'testcase': {'name': 'sometest'}
    }

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
    assert res_data['subject'] == {'type': 'koji_build', 'item': 'somebuild'}
    assert res_data['testcase'] == 'sometest'
    assert res_data['product_version'] == 'fool-1'
    assert res_data['waived'] is True
    assert res_data['comment'] == 'it broke'


@patch('waiverdb.api_v1.get_resultsdb_result')
@patch('waiverdb.auth.get_user', return_value=('foo', {}))
def test_create_waiver_with_original_spec_nvr_subject(mocked_get_user, mocked_resultsdb, client,
                                                      session):
    mocked_resultsdb.return_value = {
        'data': {
            'original_spec_nvr': ['somedata'],
        },
        'testcase': {'name': 'sometest'}
    }

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
    assert res_data['subject'] == {'original_spec_nvr': 'somedata'}
    assert res_data['testcase'] == 'sometest'
    assert res_data['product_version'] == 'fool-1'
    assert res_data['waived'] is True
    assert res_data['comment'] == 'it broke'


@patch('waiverdb.api_v1.get_resultsdb_result', side_effect=HTTPError(response=Mock(status=404)))
@patch('waiverdb.auth.get_user', return_value=('foo', {}))
def test_create_waiver_with_unknown_result_id(mocked_get_user, mocked_resultsdb, client, session):
    data = {
        'result_id': 123,
        'product_version': 'fool-1',
        'waived': True,
        'comment': 'it broke',
    }
    mocked_resultsdb.return_value.status_code = 404
    r = client.post('/api/v1.0/waivers/', data=json.dumps(data),
                    content_type='application/json')
    res_data = json.loads(r.get_data(as_text=True))
    assert res_data['message'].startswith('Failed looking up result in Resultsdb:')


@patch('waiverdb.auth.get_user', return_value=('foo', {}))
def test_create_waiver_with_no_testcase(mocked_get_user, client):
    data = {
        'subject': {'foo': 'bar'},
        'waived': True,
        'product_version': 'the-best',
    }
    r = client.post('/api/v1.0/waivers/', data=json.dumps(data),
                    content_type='application/json')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 400
    # XXX - when we ditch result_id and make subject and testcase required
    # again, this assertion will change back to the original.
#   assert 'Missing required parameter in the JSON body' in res_data['message']['testcase']
    assert 'Either result_id or subject/testcase are required arguments.' in res_data['message']


@patch('waiverdb.auth.get_user', return_value=('foo', {}))
def test_create_waiver_with_malformed_subject(mocked_get_user, client):
    data = {
        'subject': 'asd',
        'testcase': 'qqq',
    }
    r = client.post('/api/v1.0/waivers/', data=json.dumps(data),
                    content_type='application/json')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 400
    assert 'Must be a valid dict' in res_data['message']['subject']


@patch('waiverdb.auth.get_user', return_value=('foo', {}))
def test_non_superuser_cannot_create_waiver_for_other_users(mocked_get_user, client):
    data = {
        'subject': {'subject.test': 'subject'},
        'testcase': 'testcase1',
        'product_version': 'fool-1',
        'waived': True,
        'comment': 'it broke',
        'username': 'bar',
    }
    r = client.post('/api/v1.0/waivers/', data=json.dumps(data),
                    content_type='application/json')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 403
    assert 'user foo does not have the proxyuser ability' == res_data['message']


@patch('waiverdb.auth.get_user', return_value=('bodhi', {}))
def test_superuser_can_create_waiver_for_other_users(mocked_get_user, client, session):
    data = {
        'subject': {'subject.test': 'subject'},
        'testcase': 'testcase1',
        'product_version': 'fool-1',
        'waived': True,
        'comment': 'it broke',
        'username': 'bar',
    }
    r = client.post('/api/v1.0/waivers/', data=json.dumps(data),
                    content_type='application/json')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 201
    # a waiver should be created for bar by bodhi
    assert res_data['username'] == 'bar'
    assert res_data['proxied_by'] == 'bodhi'


def test_get_waiver(client, session):
    # create a new waiver
    waiver = create_waiver(session, subject={'subject.test': 'subject'},
                           testcase='testcase1', username='foo',
                           product_version='foo-1', comment='bla bla bla')
    r = client.get('/api/v1.0/waivers/%s' % waiver.id)
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert res_data['username'] == waiver.username
    assert res_data['subject'] == waiver.subject
    assert res_data['testcase'] == waiver.testcase
    assert res_data['product_version'] == waiver.product_version
    assert res_data['waived'] is True
    assert res_data['comment'] == waiver.comment


def test_404_for_nonexistent_waiver(client, session):
    r = client.get('/api/v1.0/waivers/foo')
    assert r.status_code == 404
    res_data = json.loads(r.get_data(as_text=True))
    message = (
        'The requested URL was not found on the server.  If you entered the '
        'URL manually please check your spelling and try again.')
    assert res_data['message'] == message


@patch('waiverdb.api_v1.AboutResource.get', side_effect=ConnectionError)
def test_500(mocked, client, session):
    r = client.get('/api/v1.0/about')
    assert r.status_code == 500
    res_data = json.loads(r.get_data(as_text=True))
    assert res_data['message'] == ''


def test_get_waivers(client, session):
    for i in range(0, 10):
        create_waiver(session, subject={"subject%d" % i: "%d" % i},
                      testcase="case %d" % i, username='foo %d' % i,
                      product_version='foo-%d' % i, comment='bla bla bla')
    r = client.get('/api/v1.0/waivers/')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 10


def test_pagination_waivers(client, session):
    for i in range(0, 30):
        create_waiver(session, subject={"subject%d" % i: "%d" % i},
                      testcase="case %d" % i, username='foo %d' % i,
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
    create_waiver(session, subject={'subject.test': 'subject'},
                  testcase='testcase1', username='foo',
                  product_version='foo-1')
    new_waiver = create_waiver(session, subject={'subject.test': 'subject'},
                               testcase='testcase1', username='foo',
                               product_version='foo-1', waived=False)
    r = client.get('/api/v1.0/waivers/')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['id'] == new_waiver.id
    assert res_data['data'][0]['waived'] == new_waiver.waived


def test_get_obsolete_waivers(client, session):
    old_waiver = create_waiver(session, subject={'subject.test': 'subject'},
                               testcase='testcase1', username='foo',
                               product_version='foo-1')
    new_waiver = create_waiver(session, subject={'subject.test': 'subject'},
                               testcase='testcase1', username='foo',
                               product_version='foo-1', waived=False)
    r = client.get('/api/v1.0/waivers/?include_obsolete=1')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 2
    assert res_data['data'][0]['id'] == new_waiver.id
    assert res_data['data'][1]['id'] == old_waiver.id


def test_filtering_waivers_by_subject_and_testcase(client, session):
    create_waiver(session, subject={'subject.test1': 'subject1'},
                  testcase='testcase1', username='foo-1', product_version='foo-1')
    create_waiver(session, subject={'subject.test2': 'subject2'},
                  testcase='testcase2', username='foo-2', product_version='foo-1')

    param = json.dumps([{'subject': {'subject.test1': 'subject1'}, 'testcase': 'testcase1'}])
    r = client.get('/api/v1.0/waivers/?results=%s' % param)
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['subject'] == {'subject.test1': 'subject1'}
    assert res_data['data'][0]['testcase'] == 'testcase1'


def test_filtering_waivers_by_subject_and_testcase_with_other_json_order(client, session):
    create_waiver(session, subject={'subject.test1': 'subject1'},
                  testcase='testcase1', username='foo-1', product_version='foo-1')

    param = json.dumps([{'testcase': 'testcase1', 'subject': {'subject.test1': 'subject1'}}])
    r = client.get('/api/v1.0/waivers/?results=%s' % param)
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['subject'] == {'subject.test1': 'subject1'}
    assert res_data['data'][0]['testcase'] == 'testcase1'


def test_filtering_waivers_by_multiple_results_subjects_and_testcases(client, session):
    create_waiver(session, subject={'subject.test1': 'subject1'},
                  testcase='testcase1', username='foo-1', product_version='foo-1')
    create_waiver(session, subject={'subject.test2': 'subject2'},
                  testcase='testcase2', username='foo-2', product_version='foo-1')
    create_waiver(session, subject={'subject.test3': 'subject3'},
                  testcase='testcase3', username='foo-2', product_version='foo-1')
    param = json.dumps([{'subject': {'subject.test1': 'subject1'}, 'testcase': 'testcase1'},
                        {'subject': {'subject.test2': 'subject2'}, 'testcase': 'testcase2'}])
    r = client.get('/api/v1.0/waivers/?results=%s' % param)
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 2
    assert res_data['data'][0]['subject'] == {'subject.test2': 'subject2'}
    assert res_data['data'][0]['testcase'] == 'testcase2'
    assert res_data['data'][1]['subject'] == {'subject.test1': 'subject1'}
    assert res_data['data'][1]['testcase'] == 'testcase1'


def test_filtering_waivers_by_subject_without_testcase(client, session):
    create_waiver(session, subject={'subject.test1': 'subject1'},
                  testcase='testcase1', username='foo-1', product_version='foo-1')
    create_waiver(session, subject={'subject.test2': 'subject2'},
                  testcase='testcase2', username='foo-2', product_version='foo-1')

    param = json.dumps([{'subject': {'subject.test1': 'subject1'}}])
    r = client.get('/api/v1.0/waivers/?results=%s' % param)
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['subject'] == {'subject.test1': 'subject1'}
    assert res_data['data'][0]['testcase'] == 'testcase1'


def test_filtering_waivers_by_product_version(client, session):
    create_waiver(session, subject={'subject.test1': 'subject1'},
                  testcase='testcase1', username='foo-1', product_version='release-1')
    create_waiver(session, subject={'subject.test2': 'subject2'},
                  testcase='testcase2', username='foo-1', product_version='release-2')
    r = client.get('/api/v1.0/waivers/?product_version=release-1')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['product_version'] == 'release-1'


def test_filtering_waivers_by_username(client, session):
    create_waiver(session, subject={'subject.test1': 'subject1'},
                  testcase='testcase1', username='foo', product_version='foo-1')
    create_waiver(session, subject={'subject.test2': 'subject2'},
                  testcase='testcase2', username='bar', product_version='foo-2')
    r = client.get('/api/v1.0/waivers/?username=foo')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['username'] == 'foo'


def test_filtering_waivers_by_since(client, session):
    before1 = (datetime.datetime.utcnow() - datetime.timedelta(seconds=100)).isoformat()
    before2 = (datetime.datetime.utcnow() - datetime.timedelta(seconds=99)).isoformat()
    after = (datetime.datetime.utcnow() + datetime.timedelta(seconds=100)).isoformat()
    create_waiver(session, subject={'subject.test1': 'subject1'},
                  testcase='testcase1', username='foo', product_version='foo-1')
    r = client.get('/api/v1.0/waivers/?since=%s' % before1)
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['subject'] == {'subject.test1': 'subject1'}
    assert res_data['data'][0]['testcase'] == 'testcase1'

    r = client.get('/api/v1.0/waivers/?since=%s,%s' % (before1, after))
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['subject'] == {'subject.test1': 'subject1'}
    assert res_data['data'][0]['testcase'] == 'testcase1'

    r = client.get('/api/v1.0/waivers/?since=%s' % (after))
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 0

    r = client.get('/api/v1.0/waivers/?since=%s,%s' % (before1, before2))
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 0


def test_filtering_waivers_by_malformed_since(client, session):
    create_waiver(session, subject={'subject.test1': 'subject1'},
                  testcase='testcase1', username='foo', product_version='foo-1')
    wrong_since = 123
    r = client.get('/api/v1.0/waivers/?since=%s' % wrong_since)
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 400
    assert res_data['message'] == "'since' parameter not in ISO8601 format"


def test_filtering_waivers_by_proxied_by(client, session):
    create_waiver(session, subject={'subject.test1': 'subject1'},
                  testcase='testcase1', username='foo-1', product_version='foo-1',
                  proxied_by='bodhi')
    create_waiver(session, subject={'subject.test2': 'subject2'},
                  testcase='testcase2', username='foo-2', product_version='foo-1')
    r = client.get('/api/v1.0/waivers/?proxied_by=bodhi')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 1
    assert res_data['data'][0]['subject'] == {'subject.test1': 'subject1'}
    assert res_data['data'][0]['testcase'] == 'testcase1'


def test_jsonp(client, session):
    waiver = create_waiver(session, subject={'subject.test1': 'subject1'},
                           testcase='testcase1', username='foo', product_version='foo-1')
    r = client.get('/api/v1.0/waivers/%s?callback=jsonpcallback' % waiver.id)
    assert r.mimetype == 'application/javascript'
    assert 'jsonpcallback' in r.get_data(as_text=True)


def test_healthcheck(client):
    r = client.get('healthcheck')
    assert r.status_code == 200
    assert r.get_data(as_text=True) == 'Health check OK'


def test_get_waivers_with_post_request(client, session):
    """
    This tests that users can get waivers by sending a POST request with a long
    list of result subject/testcase.
    """
    results = []
    for i in range(1, 51):
        results.append({'subject': {'subject%d' % i: '%d' % i},
                        'testcase': 'case %d' % i})
        create_waiver(session, subject={"subject%d" % i: "%d" % i},
                      testcase="case %d" % i, username='foo %d' % i,
                      product_version='foo-%d' % i, comment='bla bla bla')
    data = {
        'results': results
    }
    r = client.post('/api/v1.0/waivers/+by-subjects-and-testcases', data=json.dumps(data),
                    content_type='application/json')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert len(res_data['data']) == 50
    subjects = []
    testcases = []
    for i in reversed(range(1, 51)):
        subjects.append({'subject%d' % i: '%d' % i})
        testcases.append('case %d' % i)
    assert [w['subject'] for w in res_data['data']] == subjects
    assert set([w['testcase'] for w in res_data['data']]) == set(testcases)
    assert all(w['username'].startswith('foo') for w in res_data['data'])
    assert all(w['product_version'].startswith('foo-') for w in res_data['data'])


def test_get_waivers_with_post_malformed_since(client, session):
    create_waiver(session, subject={'subject.test1': 'subject1'},
                  testcase='testcase1', username='foo', product_version='foo-1')
    data = {
        'since': 123
    }
    r = client.post('/api/v1.0/waivers/+by-subjects-and-testcases', data=json.dumps(data),
                    content_type='application/json')
    res_data = json.loads(r.get_data(as_text=True))
    assert r.status_code == 400
    assert res_data['message'] == "'since' parameter not in ISO8601 format"


def test_about_endpoint(client):
    r = client.get('/api/v1.0/about')
    output = json.loads(r.get_data(as_text=True))
    assert r.status_code == 200
    assert output['version'] == __version__
    assert output['auth_method'] == client.application.config['AUTH_METHOD']
