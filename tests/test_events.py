# SPDX-License-Identifier: GPL-2.0+

"""This module contains tests for :mod:`waiverdb.events`."""
from __future__ import unicode_literals
import mock
from waiverdb.models import Waiver


@mock.patch('waiverdb.events.fedmsg')
def test_publish_new_waiver_with_fedmsg(mock_fedmsg, session):
    waiver = Waiver(
        subject={'subject.test': 'subject'},
        testcase='testcase1',
        username='jcline',
        product_version='something',
        waived=True,
        comment='This is a comment',
    )
    sesh = session()
    sesh.add(waiver)
    sesh.commit()
    mock_fedmsg.publish.assert_called_once_with(
        topic='waiver.new',
        msg={
            'id': waiver.id,
            'subject': {'subject.test': 'subject'},
            'testcase': 'testcase1',
            'username': 'jcline',
            'proxied_by': None,
            'product_version': 'something',
            'waived': True,
            'comment': 'This is a comment',
            'timestamp': waiver.timestamp.isoformat(),
        }
    )


@mock.patch('waiverdb.events.fedmsg')
def test_publish_new_waiver_with_fedmsg_for_proxy_user(mock_fedmsg, session):
    waiver = Waiver(
        subject={'subject.test': 'subject'},
        testcase='testcase1',
        username='jcline',
        product_version='something',
        waived=True,
        comment='This is a comment',
        proxied_by='bodhi'
    )
    sesh = session()
    sesh.add(waiver)
    sesh.commit()
    mock_fedmsg.publish.assert_called_once_with(
        topic='waiver.new',
        msg={
            'id': waiver.id,
            'subject': {'subject.test': 'subject'},
            'testcase': 'testcase1',
            'username': 'jcline',
            'proxied_by': 'bodhi',
            'product_version': 'something',
            'waived': True,
            'comment': 'This is a comment',
            'timestamp': waiver.timestamp.isoformat(),
        }
    )
