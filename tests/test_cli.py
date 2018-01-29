# SPDX-License-Identifier: GPL-2.0+
import pytest
import json
from mock import Mock, patch
from click.testing import CliRunner
from waiverdb.cli import cli as waiverdb_cli


def test_misconfigured_auth_method(tmpdir):
    p = tmpdir.join('client.conf')
    p.write("""
[waiverdb]
api_url=http://localhost:5004/api/v1.0
        """)
    runner = CliRunner()
    args = ['-C', p.strpath]
    result = runner.invoke(waiverdb_cli, args)
    assert result.exit_code == 1
    assert result.output == 'Error: The config option "auth_method" is required\n'


def test_misconfigured_api_url(tmpdir):
    p = tmpdir.join('client.conf')
    p.write("""
[waiverdb]
auth_method=OIDC
        """)
    runner = CliRunner()
    args = ['-C', p.strpath]
    result = runner.invoke(waiverdb_cli, args)
    assert result.exit_code == 1
    assert result.output == 'Error: The config option "api_url" is required\n'


def test_misconfigured_resultdb_api_url(tmpdir):
    p = tmpdir.join('client.conf')
    p.write("""
[waiverdb]
auth_method=dummy
api_url=http://localhost:5004/api/v1.0
        """)
    runner = CliRunner()
    args = ['-C', p.strpath]
    result = runner.invoke(waiverdb_cli, args)
    assert result.exit_code == 1
    assert result.output == 'Error: The config option "resultsdb_api_url" is required\n'


def test_misconfigured_oidc_id_provider(tmpdir):
    p = tmpdir.join('client.conf')
    p.write("""
[waiverdb]
auth_method=OIDC
api_url=http://localhost:5004/api/v1.0
        """)
    runner = CliRunner()
    args = ['-C', p.strpath]
    result = runner.invoke(waiverdb_cli, args)
    assert result.exit_code == 1
    assert result.output == 'Error: The config option "oidc_id_provider" is required\n'


def test_misconfigured_oidc_client_id(tmpdir):
    p = tmpdir.join('client.conf')
    p.write("""
[waiverdb]
auth_method=OIDC
api_url=http://localhost:5004/api/v1.0
oidc_id_provider=https://id.stg.fedoraproject.org/openidc/
        """)
    runner = CliRunner()
    args = ['-C', p.strpath]
    result = runner.invoke(waiverdb_cli, args)
    assert result.exit_code == 1
    assert result.output == 'Error: The config option "oidc_client_id" is required\n'


def test_misconfigured_oidc_scopes(tmpdir):
    p = tmpdir.join('client.conf')
    p.write("""
[waiverdb]
auth_method=OIDC
api_url=http://localhost:5004/api/v1.0
oidc_id_provider=https://id.stg.fedoraproject.org/openidc/
oidc_client_id=waiverdb
        """)
    runner = CliRunner()
    args = ['-C', p.strpath]
    result = runner.invoke(waiverdb_cli, args)
    assert result.exit_code == 1
    assert result.output == 'Error: The config option "oidc_scopes" is required\n'


def test_no_product_version(tmpdir):
    p = tmpdir.join('client.conf')
    p.write("""
[waiverdb]
auth_method=OIDC
api_url=http://localhost:5004/api/v1.0
oidc_id_provider=https://id.stg.fedoraproject.org/openidc/
oidc_client_id=waiverdb
oidc_scopes=
    openid
resultsdb_api_url=http://localhost:5001/api/v2.0
        """)
    runner = CliRunner()
    args = ['-C', p.strpath]
    result = runner.invoke(waiverdb_cli, args)
    assert result.exit_code == 1
    assert result.output == 'Error: Please specify product version\n'


def test_no_subject(tmpdir):
    p = tmpdir.join('client.conf')
    p.write("""
[waiverdb]
auth_method=OIDC
api_url=http://localhost:5004/api/v1.0
oidc_id_provider=https://id.stg.fedoraproject.org/openidc/
oidc_client_id=waiverdb
oidc_scopes=
    openid
resultsdb_api_url=http://localhost:5001/api/v2.0
        """)
    runner = CliRunner()
    args = ['-C', p.strpath, '-p', 'fedora-26']
    result = runner.invoke(waiverdb_cli, args)
    assert result.exit_code == 1
    assert result.output == 'Error: Please specify one subject\n'


def test_no_testcase(tmpdir):
    p = tmpdir.join('client.conf')
    p.write("""
[waiverdb]
auth_method=OIDC
api_url=http://localhost:5004/api/v1.0
oidc_id_provider=https://id.stg.fedoraproject.org/openidc/
oidc_client_id=waiverdb
oidc_scopes=
    openid
resultsdb_api_url=http://localhost:5001/api/v2.0
        """)
    runner = CliRunner()
    args = ['-C', p.strpath, '-p', 'fedora-26', '-s', 'subject']
    result = runner.invoke(waiverdb_cli, args)
    assert result.exit_code == 1
    assert result.output == 'Error: Please specify testcase\n'


def test_oidc_auth_is_enabled(tmpdir):
    # Skip if waiverdb is rebuilt for an environment where Kerberos authentication
    # is used and python-openidc-client is not available.
    pytest.importorskip('openidc_client')
    with patch('openidc_client.OpenIDCClient.send_request') as mock_oidc_req:
        mock_rv = Mock()
        mock_rv.json.return_value = {
            "comment": "It's dead!",
            "id": 15,
            "product_version": "Parrot",
            "subject": {"subject.test": "test", "s": "t"},
            "testcase": "test.testcase",
            "timestamp": "2017-010-16T17:42:04.209638",
            "username": "foo",
            "waived": True
        }
        mock_oidc_req.return_value = mock_rv
        p = tmpdir.join('client.conf')
        p.write("""
[waiverdb]
auth_method=OIDC
api_url=http://localhost:5004/api/v1.0
oidc_id_provider=https://id.stg.fedoraproject.org/openidc/
oidc_client_id=waiverdb
oidc_scopes=
    openid
resultsdb_api_url=http://localhost:5001/api/v2.0
            """)
        runner = CliRunner()
        args = ['-C', p.strpath, '-p', 'Parrot', '-s', '{"subject.test": "test", "s": "t"}',
                '-t', 'test.testcase', '-c', "It's dead!"]
        result = runner.invoke(waiverdb_cli, args)
        exp_json = {
            "subject": {"subject.test": "test", "s": "t"},
            "testcase": "test.testcase",
            'waived': True,
            'product_version': 'Parrot',
            'comment': "It's dead!"
        }
        mock_oidc_req.assert_called_once_with(
            url='http://localhost:5004/api/v1.0/waivers/',
            data=json.dumps(exp_json),
            scopes=['openid'],
            timeout=60,
            headers={'Content-Type': 'application/json'})
        assert result.exit_code == 0
        assert result.output == 'Created waiver 15 for result with subject {"subject.test": "test", "s": "t"} and testcase test.testcase\n' # noqa


def test_kerberos_is_enabled(tmpdir):
    # Skip if waiverdb is rebuilt for an environment where OIDC authentication
    # is used and python-requests-kerberos is not available.
    pytest.importorskip('requests_kerberos')
    with patch('requests.request') as mock_request:
        mock_rv = Mock()
        mock_rv.json.return_value = {
            "comment": "It's dead!",
            "id": 15,
            "product_version": "Parrot",
            "subject": {"subject.test": "test", "s": "t"},
            "testcase": "test.testcase",
            "timestamp": "2017-010-16T17:42:04.209638",
            "username": "foo",
            "waived": True
        }
        mock_request.return_value = mock_rv
        p = tmpdir.join('client.conf')
        p.write("""
[waiverdb]
auth_method=Kerberos
api_url=http://localhost:5004/api/v1.0
resultsdb_api_url=http://localhost:5001/api/v2.0
            """)
        runner = CliRunner()
        args = ['-C', p.strpath, '-p', 'Parrot', '-s', '{"subject.test": "test", "s": "t"}',
                '-t', 'test.testcase', '-c', "It's dead!"]
        result = runner.invoke(waiverdb_cli, args)
        mock_request.assert_called_once()
        assert result.output == 'Created waiver 15 for result with subject {"subject.test": "test", "s": "t"} and testcase test.testcase\n' # noqa


def test_submit_waiver_with_id(tmpdir):
    with patch('requests.request') as mock_request:
        mock_rv = Mock()
        mock_rv.json.return_value = {
            "comment": "It's dead!",
            "data": {"item": ["htop-1.0-1.fc22"], "type": ["bodhi_update"]},
            "id": 15,
            "product_version": "Parrot",
            "testcase": {"name": "test.testcase"},
            "timestamp": "2017-010-16T17:42:04.209638",
            "username": "foo",
            "waived": True
        }
        mock_request.return_value = mock_rv
        p = tmpdir.join('client.conf')
        p.write("""
[waiverdb]
auth_method=dummy
api_url=http://localhost:5004/api/v1.0
resultsdb_api_url=http://localhost:5001/api/v2.0
        """)
        runner = CliRunner()
        args = ['-C', p.strpath, '-p', 'Parrot', '-r', '123',
                '-c', "It's dead!"]
        result = runner.invoke(waiverdb_cli, args)
        mock_request.assert_called()
        assert result.output == 'Created waiver 15 for result with id 123\n'


def test_submit_waiver_with_multiple_ids(tmpdir):
    with patch('requests.request') as mock_request:
        mock_rv = Mock()
        mock_rv.json.return_value = {
            "comment": "It's dead!",
            "data": {"item": ["htop-1.0-1.fc22"], "type": ["bodhi_update"]},
            "id": 15,
            "testcase": {"name": "test.testcase"},
            "timestamp": "2017-010-16T17:42:04.209638",
            "username": "foo",
            "waived": True
        }
        mock_request.return_value = mock_rv
        p = tmpdir.join('client.conf')
        p.write("""
[waiverdb]
auth_method=dummy
api_url=http://localhost:5004/api/v1.0
resultsdb_api_url=http://localhost:5001/api/v2.0
        """)
        runner = CliRunner()
        args = ['-C', p.strpath, '-p', 'Parrot', '-r', '123', '-r', '456',
                '-c', "It's dead!"]
        result = runner.invoke(waiverdb_cli, args)
        mock_request.assert_called()

        assert result.output == 'Created waiver 15 for result with id 123\n\
Created waiver 15 for result with id 456\n'


def test_malformed_submission_with_id_and_subject_and_testcase(tmpdir):
        runner = CliRunner()
        p = tmpdir.join('client.conf')
        p.write("""
[waiverdb]
auth_method=dummy
api_url=http://localhost:5004/api/v1.0
resultsdb_api_url=http://localhost:5001/api/v2.0
        """)
        args = ['-C', p.strpath, '-p', 'Parrot', '-r', '123', '-s',
                '{"subject.test": "test", "s": "t"}', '-c', "It's dead!"]
        result = runner.invoke(waiverdb_cli, args)
        assert result.output == 'Error: Please specify result_id or subject/testcase. Not both\n'


def test_submit_waiver_for_original_spec_nvr_result(tmpdir):
    with patch('requests.request') as mock_request:
        mock_rv = Mock()
        mock_rv.json.return_value = {
            "comment": "It's dead!",
            "original_spec_nvr": "test",
            "id": 15,
            "product_version": "Parrot",
            "testcase": {"name": "test.testcase"},
            "timestamp": "2017-010-16T17:42:04.209638",
            "username": "foo",
            "waived": True
        }
        mock_request.return_value = mock_rv
        p = tmpdir.join('client.conf')
        p.write("""
[waiverdb]
auth_method=dummy
api_url=http://localhost:5004/api/v1.0
resultsdb_api_url=http://localhost:5001/api/v2.0
            """)
        runner = CliRunner()
        args = ['-C', p.strpath, '-p', 'Parrot', '-r', '123',
                '-c', "It's dead!"]
        result = runner.invoke(waiverdb_cli, args)
        mock_request.assert_called()
        assert result.output == 'Created waiver 15 for result with id 123\n'
