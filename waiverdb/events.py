# SPDX-License-Identifier: GPL-2.0+
"""
This module contains a set of `SQLAlchemy event`_ hooks.

To use these hooks, you must register them with SQLAlchemy
using the :func:`sqlalchemy.event.listen` function.

.. _SQLALchemy events:
    https://docs.sqlalchemy.org/en/latest/orm/events.html
"""
from __future__ import unicode_literals

import logging

from flask_restful import marshal
import fedmsg
import stomp
import json
from waiverdb.fields import waiver_fields
from waiverdb.models import Waiver
from waiverdb.utils import stomp_connection
from flask import current_app

_log = logging.getLogger(__name__)


def publish_new_waiver(session):
    """
    A post-commit event hook that emits messages to a message bus. The messages
    can be published by either fedmsg-hub with zmq or stomp.

    This event is designed to be registered with a session factory::

        >>> from sqlalchemy.event import listen
        >>> listen(MyScopedSession, 'after_commit', publish_new_waiver)

    The emitted message will look like::

        {
          "username": "jcline",
          "i": 4,
          "timestamp": 1489686124,
          "msg_id": "2017-80e46243-e6f5-46df-8dcd-4d17809eb298",
          "topic": "org.fedoraproject.dev.waiverdb.waiver.new",
          "msg": {
            "comment": "Because I said so",
            "username": "http://jcline.id.fedoraproject.org/",
            "waived": true,
            "timestamp": "2017-03-16T17:42:04.209638",
            "product_version": "Satellite 6.3",
            "result_id": 1,
            "id": 15
          }
        }

    Args:
        session (sqlalchemy.orm.Session): The session that was committed to the
            database. This session is not active and cannot emit SQL.

    """
    _log.debug('The publish_new_waiver SQLAlchemy event has been activated.')
    if current_app.config['MESSAGE_PUBLISHER'] == 'stomp':
        with stomp_connection() as conn:
            stomp_configs = current_app.config.get('STOMP_CONFIGS')
            for row in session.identity_map.values():
                if isinstance(row, Waiver):
                    _log.debug('Publishing a message for %r', row)
                    msg = json.dumps(marshal(row, waiver_fields))
                    kwargs = dict(body=msg, headers={}, destination=stomp_configs['destination'])
                    if stomp.__version__[0] < 4:
                        kwargs['message'] = kwargs.pop('body')  # On EL7, different sig.
                    conn.send(**kwargs)
    else:
        for row in session.identity_map.values():
            if isinstance(row, Waiver):
                _log.debug('Publishing a message for %r', row)
                fedmsg.publish(topic='waiver.new', msg=marshal(row, waiver_fields))
