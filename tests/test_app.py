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
"""This module contains tests for :mod:`waiverdb.app`."""
from __future__ import unicode_literals

import mock

from waiverdb import app, config
from flask_sqlalchemy import SignallingSession


class NoZmqConfig(config.Config):
    ZEROMQ_PUBLISH = False
    AUTH_METHOD = None


class ZmqConfig(config.Config):
    ZEROMQ_PUBLISH = True
    AUTH_METHOD = None


@mock.patch('waiverdb.app.event.listen')
def test_register_events_no_zmq(mock_listen):
    app.create_app(NoZmqConfig)
    assert 0 == mock_listen.call_count


@mock.patch('waiverdb.app.event.listen')
def test_register_events_zmq(mock_listen):
    app.create_app(ZmqConfig)
    mock_listen.assert_called_once_with(
        SignallingSession, 'after_commit', app.fedmsg_new_waiver)
