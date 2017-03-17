# -*- coding: utf-8 -*-
#
# This file is part of WaiverDB.
# Copyright © 2017 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
"""This module contains tests for :mod:`waiverdb.events`."""
from __future__ import unicode_literals

import pytest

import mock

from waiverdb import events
from waiverdb.models import Waiver


@mock.patch('waiverdb.events.fedmsg', None)
def test_fedmsg_new_waiver_missing_fedmsg():
    with pytest.raises(RuntimeError):
        events.fedmsg_new_waiver(None)


@mock.patch('waiverdb.events.fedmsg')
def test_fedmsg_new_waiver(mock_fedmsg, session):
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
