# SPDX-License-Identifier: GPL-2.0+

import datetime
import functools
import stomp
from flask import request, url_for, jsonify, current_app
from flask_restful import marshal
from waiverdb.fields import waiver_fields
from werkzeug.exceptions import NotFound, HTTPException
from contextlib import contextmanager


def reqparse_since(since):
    """
    This parses the since(i.e. 2017-02-13T23:37:58.193281, 2017-02-16T23:37:58.193281)
    query parameter and returns a tuple.
    """
    start = None
    end = None
    if ',' in since:
        start, end = since.split(',')
    else:
        start = since
    if start:
        start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%f")
    if end:
        end = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%f")
    return start, end


def json_collection(query, page=1, limit=10):
    """
    Helper function for Flask request handlers which want to return
    a collection of resources as JSON.
    """
    try:
        p = query.paginate(page, limit)
    except NotFound:
        return {'data': [], 'prev': None, 'next': None, 'first': None, 'last': None}
    pages = {'data': marshal(p.items, waiver_fields)}
    query_pairs = request.args.copy()
    if query_pairs:
        # remove the page number
        query_pairs.pop('page', default=None)
    if p.has_prev:
        pages['prev'] = url_for(request.endpoint, page=p.prev_num, _external=True,
                                **query_pairs)
    else:
        pages['prev'] = None
    if p.has_next:
        pages['next'] = url_for(request.endpoint, page=p.next_num, _external=True,
                                **query_pairs)
    else:
        pages['next'] = None
    pages['first'] = url_for(request.endpoint, page=1, _external=True, **query_pairs)
    pages['last'] = url_for(request.endpoint, page=p.pages, _external=True, **query_pairs)
    return pages


def json_error(error):
    """
    Return error responses in JSON.

    :param error: One of Exceptions. It could be HTTPException, ConnectionError, or
    Timeout.
    :return: JSON error response.

    """
    if isinstance(error, HTTPException):
        response = jsonify(message=error.description)
        response.status_code = error.code
    else:
        # Could be ConnectionError or Timeout
        current_app.logger.exception('Returning 500 to user.')
        response = jsonify(message=str(error.message))
        response.status_code = 500

    return insert_headers(response)


def jsonp(func):
    """Wraps Jsonified output for JSONP requests."""
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            resp = jsonify(func(*args, **kwargs))
            resp.set_data('{}({})'.format(
                str(callback),
                resp.get_data()
            ))
            resp.mimetype = 'application/javascript'
            return resp
        else:
            return func(*args, **kwargs)
    return wrapped


@contextmanager
def stomp_connection():
    """
    Helper function for stomp connection.
    """
    if current_app.config.get('STOMP_CONFIGS'):
        configs = current_app.config.get('STOMP_CONFIGS')
        if 'destination' not in configs or not configs['destination']:
            raise RuntimeError('stomp was configured to publish messages, '
                               'but destination is not configured in STOMP_CONFIGS')
        if 'connection' not in configs or not configs['connection']:
            raise RuntimeError('stomp was configured to publish messages,, '
                               'but connection is not configured in STOMP_CONFIGS')
        conn = stomp.Connection(**configs['connection'])
        conn.start()
        conn.connect(**configs.get('credentials', {}))
        yield conn
        conn.disconnect()
    else:
        raise RuntimeError('stomp was configured to publish messages, '
                           'but STOMP_CONFIGS is not configured')


def insert_headers(response):
    """ Insert the CORS headers for the give reponse if there are any
    configured for the application.
    """
    if current_app.config.get('CORS_URL'):
        response.headers['Access-Control-Allow-Origin'] = \
            current_app.config['CORS_URL']
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Method'] = 'POST, OPTIONS'
    return response
