# SPDX-License-Identifier: GPL-2.0+

"""This module contains tests for :mod:`waiverdb.events`."""
from __future__ import unicode_literals
import mock
from waiverdb.models import Waiver


@mock.patch('waiverdb.events.fedmsg')
def test_publish_new_waiver_with_fedmsg(mock_fedmsg, session):
    waiver = Waiver(
        result_id=1,
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
            'result_id': 1,
            'username': 'jcline',
            'product_version': 'something',
            'waived': True,
            'comment': 'This is a comment',
            'timestamp': waiver.timestamp.isoformat(),
        }
    )
