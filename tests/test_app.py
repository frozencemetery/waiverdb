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


class DisabledMessagingConfig(config.Config):
    MESSAGE_BUS_PUBLISH = False
    AUTH_METHOD = None
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class EnabledMessagedConfig(config.Config):
    MESSAGE_BUS_PUBLISH = True
    AUTH_METHOD = None
    SQLALCHEMY_TRACK_MODIFICATIONS = True


@mock.patch('waiverdb.app.event.listen')
def test_disabled_messaging_should_not_register_events(mock_listen):
    app.create_app(DisabledMessagingConfig)
    assert 0 == mock_listen.call_count


@mock.patch('waiverdb.app.event.listen')
def test_enabled_messaging_should_register_events(mock_listen):
    app.create_app(EnabledMessagedConfig)
    mock_listen.assert_called_once_with(
        SignallingSession, 'after_commit', app.publish_new_waiver)
