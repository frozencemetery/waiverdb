# -*- coding: utf-8 -*-
#
# This file is part of WaiverDB.
# Copyright © 2017 Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License v.2, or (at your option) any later
# version.  This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY expressed or implied, including the
# implied warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.  You
# should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Any Red Hat trademarks that are incorporated in the source
# code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission
# of Red Hat, Inc.
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
        msg=waiver.__json__(),
    )
