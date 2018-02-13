# SPDX-License-Identifier: GPL-2.0+

import json

import requests
from flask import Blueprint, request, current_app
from flask_restful import Resource, Api, reqparse, marshal_with, marshal
from werkzeug.exceptions import BadRequest, UnsupportedMediaType, Forbidden, ServiceUnavailable
from sqlalchemy.sql.expression import func

from waiverdb import __version__
from waiverdb.models import db, Waiver
from waiverdb.utils import reqparse_since, json_collection, jsonp
from waiverdb.fields import waiver_fields
import waiverdb.auth

api_v1 = (Blueprint('api_v1', __name__))
api = Api(api_v1)
requests_session = requests.Session()


def valid_dict(value):
    if not isinstance(value, dict):
        raise ValueError("Must be a valid dict, not %r" % value)
    return value


def get_resultsdb_result(result_id):
    response = requests_session.request('GET', '{0}/results/{1}'.format(
        current_app.config['RESULTSDB_API_URL'], result_id),
        headers={'Content-Type': 'application/json'},
        timeout=60)
    response.raise_for_status()
    return response.json()


# RP contains request parsers (reqparse.RequestParser).
#    Parsers are added in each 'resource section' for better readability
RP = {}
RP['create_waiver'] = reqparse.RequestParser()
RP['create_waiver'].add_argument('subject', type=valid_dict, location='json')
RP['create_waiver'].add_argument('testcase', type=str, location='json')
RP['create_waiver'].add_argument('result_id', type=int, location='json')
RP['create_waiver'].add_argument('waived', type=bool, required=True, location='json')
RP['create_waiver'].add_argument('product_version', type=str, required=True, location='json')
RP['create_waiver'].add_argument('comment', type=str, default=None, location='json')
RP['create_waiver'].add_argument('username', type=str, default=None, location='json')

RP['get_waivers'] = reqparse.RequestParser()
RP['get_waivers'].add_argument('results', location='args')
RP['get_waivers'].add_argument('product_version', location='args')
RP['get_waivers'].add_argument('username', location='args')
RP['get_waivers'].add_argument('include_obsolete', type=bool, default=False, location='args')
# XXX This matches the since query parameter in resultsdb but I think it would
# be good to use two parameters(since and until).
RP['get_waivers'].add_argument('since', location='args')
RP['get_waivers'].add_argument('page', default=1, type=int, location='args')
RP['get_waivers'].add_argument('limit', default=10, type=int, location='args')
RP['get_waivers'].add_argument('proxied_by', location='args')


class WaiversResource(Resource):
    @jsonp
    def get(self):
        """
        Get waiver records.

        **Sample request**:

        .. sourcecode:: http

           GET /api/v1.0/waivers/ HTTP/1.1
           Host: localhost:5004
           User-Agent: curl/7.51.0
           Accept: application/json

        **Sample response**:

        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: application/json
           Content-Length: 184
           Server: Werkzeug/0.12.1 Python/2.7.13
           Date: Thu, 16 Mar 2017 13:53:14 GMT

           {
               "data": [],
               "first": "http://localhost:5004/api/v1.0/waivers/?page=1",
               "last": "http://localhost:5004/api/v1.0/waivers/?page=0",
               "next": null,
               "prev": null
           }


        :query int page: The page to get.
        :query int limit: Limit the number of items returned.
        :query string results: Filter the waivers by result. Accepts a list of
            dictionaries, with one key 'subject' and one key 'testcase'.
        :query string product_version: Filter the waivers by product version.
        :query string username: Filter the waivers by username.
        :query string proxied_by: Filter the waivers by the users who are
            allowed to create waivers on behalf of other users.
        :query string since: An ISO 8601 formatted datetime (e.g. 2017-03-16T13:40:05+00:00)
            to filter results by. Optionally provide a second ISO 8601 datetime separated
            by a comma to retrieve a range (e.g. 2017-03-16T13:40:05+00:00,
            2017-03-16T13:40:15+00:00)
        :query boolean include_obsolete: If true, obsolete waivers will be included.
        :statuscode 200: If the query was valid and no problems were encountered.
            Note that the response may still contain 0 waivers.
        :statuscode 400: The request was malformed and could not be processed.
        """
        args = RP['get_waivers'].parse_args()
        query = Waiver.query.order_by(Waiver.timestamp.desc())

        if args['results']:
            results = json.loads(args['results'])
            for d in results:
                if d.get('subject', None):
                    if not isinstance(d.get('subject', None), dict):
                        raise BadRequest("'results' parameter should be a list \
                                          of dictionaries with subject and testcase")
                if d.get('testcase', None):
                    if not isinstance(d.get('testcase', None), basestring):
                        raise BadRequest("'results' parameter should be a list \
                                      of dictionaries with subject and testcase")
            query = Waiver.by_results(query, results)
        if args['product_version']:
            query = query.filter(Waiver.product_version == args['product_version'])
        if args['username']:
            query = query.filter(Waiver.username == args['username'])
        if args['proxied_by']:
            query = query.filter(Waiver.proxied_by == args['proxied_by'])
        if args['since']:
            try:
                since_start, since_end = reqparse_since(args['since'])
            except ValueError:
                raise BadRequest("'since' parameter not in ISO8601 format")
            except TypeError:
                raise BadRequest("'since' parameter not in ISO8601 format")
            if since_start:
                query = query.filter(Waiver.timestamp >= since_start)
            if since_end:
                query = query.filter(Waiver.timestamp <= since_end)
        if not args['include_obsolete']:
            subquery = db.session.query(func.max(Waiver.id)).group_by(Waiver.subject,
                                                                      Waiver.testcase)
            query = query.filter(Waiver.id.in_(subquery))
        query = query.order_by(Waiver.timestamp.desc())
        return json_collection(query, args['page'], args['limit'])

    @jsonp
    @marshal_with(waiver_fields)
    def post(self):
        """
        Create a new waiver.

        **Sample request**:

        .. sourcecode:: http

           POST /api/v1.0/waivers/ HTTP/1.1
           Host: localhost:5004
           Accept-Encoding: gzip, deflate
           Accept: application/json
           Connection: keep-alive
           User-Agent: HTTPie/0.9.4
           Content-Type: application/json
           Content-Length: 91

           {
               "subject": {"productmd.compose.id": "Fedora-9000-19700101.n.18"},
               "testcase": "compose.install_no_user",
               "waived": false,
               "product_version": "Parrot",
               "comment": "It's dead!"
           }



        **Sample response**:

        .. sourcecode:: http

           HTTP/1.0 201 CREATED
           Content-Length: 228
           Content-Type: application/json
           Date: Thu, 16 Mar 2017 17:42:04 GMT
           Server: Werkzeug/0.12.1 Python/2.7.13

           {
               "comment": "It's dead!",
               "id": 15,
               "product_version": "Parrot",
               "subject": {"productmd.compose.id": "Fedora-9000-19700101.n.18"},
               "testcase": "compose.install_no_user",
               "timestamp": "2017-03-16T17:42:04.209638",
               "username": "jcline",
               "waived": false,
               "proxied_by": null
           }

        :json object subject: The result subject for the waiver.
        :json string testcase: The result testcase for the waiver.
        :json boolean waived: Whether or not the result is waived.
        :json string product_version: The product version string.
        :json string comment: A comment explaining the waiver.
        :json string username: Username on whose behalf the caller is proxying.
        :statuscode 201: The waiver was successfully created.
        """

        user, headers = waiverdb.auth.get_user(request)
        args = RP['create_waiver'].parse_args()
        proxied_by = None
        if args.get('username'):
            if user not in current_app.config['SUPERUSERS']:
                raise Forbidden('user %s does not have the proxyuser ability' % user)
            proxied_by = user
            user = args['username']

        # XXX - remove this in a future release (it was for temp backwards compat)
        if args['result_id']:
            if args['subject'] or args['testcase']:
                raise BadRequest('Only result_id or subject and '
                                 'testcase are allowed.  Not both.')
            try:
                result = get_resultsdb_result(args['result_id'])
            except requests.HTTPError as e:
                if e.response.status_code == 404:
                    raise BadRequest('Result id not found in Resultsdb')
                else:
                    raise ServiceUnavailable('Failed looking up result in Resultsdb: %s' % e)
            except Exception as e:
                raise ServiceUnavailable('Failed looking up result in Resultsdb: %s' % e)
            if 'original_spec_nvr' in result['data']:
                subject = {'original_spec_nvr': result['data']['original_spec_nvr'][0]}
            else:
                if result['data']['type'][0] == 'koji_build' or \
                   result['data']['type'][0] == 'bodhi_update':
                    SUBJECT_KEYS = ['item', 'type']
                    subject = dict([(k, v[0]) for k, v in result['data'].items()
                                    if k in SUBJECT_KEYS])
                else:
                    raise BadRequest('It is not possible to submit a waiver by '
                                     'id for this result. Please try again specifying '
                                     'a subject and a testcase.')
            args['subject'] = subject
            args['testcase'] = result['testcase']['name']

        if not args['subject'] or not args['testcase']:
            raise BadRequest('Either result_id or subject/testcase '
                             'are required arguments.')

        waiver = Waiver(args['subject'], args['testcase'], user,
                        args['product_version'], args['waived'], args['comment'], proxied_by)
        db.session.add(waiver)
        db.session.commit()
        return waiver, 201, headers


class WaiverResource(Resource):
    @jsonp
    @marshal_with(waiver_fields)
    def get(self, waiver_id):
        """
        Get a single waiver by waiver ID.

        :param int waiver_id: The waiver's database ID.

        :statuscode 200: The waiver was found and returned.
        :statuscode 404: No waiver exists with that ID.
        """
        try:
            return Waiver.query.get_or_404(waiver_id)
        except Exception as NotFound:
            raise type(NotFound)('Waiver not found')


class GetWaiversBySubjectsAndTestcases(Resource):
    @jsonp
    def post(self):
        """
        Return a list of waivers by filtering the waivers with a
        list of result subjects and testcases.
        This accepts POST requests in order to handle a special
        case where a GET /waivers/ request has a long query string with many
        result subjects/testcases that could cause 413 errors.

        **Sample request**:

        .. sourcecode:: http

           POST /api/v1.0/waivers/+by-subjects-and-testcases HTTP/1.1
           Host: localhost:5004
           Accept-Encoding: gzip, deflate
           Accept: application/json
           Connection: keep-alive
           User-Agent: HTTPie/0.9.4
           Content-Type: application/json
           Content-Length: 40

           {
                "results": [
                    {
                        "subject": {"productmd.compose.id": "Fedora-9000-19700101.n.18"},
                        "testcase": "compose.install_no_user"
                    },
                    {
                        "subject": {"item": "gzip-1.9-1.fc28", "type": "koji_build"},
                        "testcase": "dist.rpmlint"
                    }
                ]
           }

        **Sample response**:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Length: 562
            Content-Type: application/json
            Date: Thu, 21 Sep 2017 04:58:37 GMT
            Server: Werkzeug/0.11.10 Python/2.7.13

            {
                "data": [
                    {
                        "comment": "It's dead!",
                        "id": 5,
                        "product_version": "Parrot",
                        "subject": {"productmd.compose.id": "Fedora-9000-19700101.n.18"},
                        "testcase": "compose.install_no_user",
                        "timestamp": "2017-09-21T04:55:53.343368",
                        "username": "dummy",
                        "waived": true,
                        "proxied_by": null
                    },
                    {
                        "comment": "It's dead!",
                        "id": 4,
                        "product_version": "Parrot",
                        "subject": {"item": "gzip-1.9-1.fc28", "type": "koji_build"},
                        "testcase": "dist.rpmlint",
                        "timestamp": "2017-09-21T04:55:51.936658",
                        "username": "dummy",
                        "waived": true,
                        "proxied_by": null
                    }
                ]
            }

        :jsonparam array results: Filter the waivers by a list of dictionaries
            with result subjects and testcase.
        :jsonparam string product_version: Filter the waivers by product version.
        :jsonparam string username: Filter the waivers by username.
        :jsonparam string proxied_by: Filter the waivers by the users who are
            allowed to create waivers on behalf of other users.
        :jsonparam string since: An ISO 8601 formatted datetime (e.g. 2017-03-16T13:40:05+00:00)
            to filter results by. Optionally provide a second ISO 8601 datetime separated
            by a comma to retrieve a range (e.g. 2017-03-16T13:40:05+00:00,
            2017-03-16T13:40:15+00:00)
        :jsonparam boolean include_obsolete: If true, obsolete waivers will be included.
        :statuscode 200: If the query was valid and no problems were encountered.
            Note that the response may still contain 0 waivers.
        """
        if not request.get_json():
            raise UnsupportedMediaType('No JSON payload in request')
        data = request.get_json()
        query = Waiver.query.order_by(Waiver.timestamp.desc())
        if data.get('results'):
            for d in data['results']:
                if d.get('subject', None):
                    if not isinstance(d.get('subject', None), dict):
                        raise BadRequest("'results' parameter should be a list \
                                          of dictionaries with subject and testcase")
                if d.get('testcase', None):
                    if not isinstance(d.get('testcase', None), basestring):
                        raise BadRequest("'results' parameter should be a list \
                                          of dictionaries with subject and testcase")
            query = Waiver.by_results(query, data['results'])
        if 'product_version' in data:
            query = query.filter(Waiver.product_version == data['product_version'])
        if 'username' in data:
            query = query.filter(Waiver.username == data['username'])
        if 'proxied_by' in data:
            query = query.filter(Waiver.proxied_by == data['proxied_by'])
        if 'since' in data:
            try:
                since_start, since_end = reqparse_since(data['since'])
            except ValueError:
                raise BadRequest("'since' parameter not in ISO8601 format")
            except TypeError:
                raise BadRequest("'since' parameter not in ISO8601 format")
            if since_start:
                query = query.filter(Waiver.timestamp >= since_start)
            if since_end:
                query = query.filter(Waiver.timestamp <= since_end)
        if not data.get('include_obsolete', False):
            subquery = db.session.query(func.max(Waiver.id)).group_by(Waiver.subject,
                                                                      Waiver.testcase)
            query = query.filter(Waiver.id.in_(subquery))

        query = query.order_by(Waiver.timestamp.desc())
        return {'data': marshal(query.all(), waiver_fields)}


class AboutResource(Resource):
    @jsonp
    def get(self):
        """
        Returns the current running version and the method used for authentication.

        **Sample response**:

        .. sourcecode:: none

          HTTP/1.0 200 OK
          Content-Length: 55
          Content-Type: application/json
          Date: Tue, 31 Oct 2017 04:29:19 GMT
          Server: Werkzeug/0.11.10 Python/2.7.13

          {
            "auth_method": "OIDC",
            "version": "0.3.1"
          }

        :statuscode 200: Currently running waiverdb software version and authentication
                         are returned.
        """
        return {'version': __version__, 'auth_method': current_app.config['AUTH_METHOD']}


# set up the Api resource routing here
api.add_resource(WaiversResource, '/waivers/')
api.add_resource(WaiverResource, '/waivers/<int:waiver_id>')
api.add_resource(GetWaiversBySubjectsAndTestcases, '/waivers/+by-subjects-and-testcases')
api.add_resource(AboutResource, '/about')
