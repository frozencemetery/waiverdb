# SPDX-License-Identifier: GPL-2.0+

from flask import Blueprint, request, current_app
from flask_restful import Resource, Api, reqparse, marshal_with, marshal
from werkzeug.exceptions import BadRequest, NotFound, UnsupportedMediaType
from sqlalchemy.sql.expression import func

from waiverdb import __version__
from waiverdb.models import db, Waiver
from waiverdb.utils import reqparse_since, json_collection, jsonp
from waiverdb.fields import waiver_fields
import waiverdb.auth

api_v1 = (Blueprint('api_v1', __name__))
api = Api(api_v1)

# RP contains request parsers (reqparse.RequestParser).
#    Parsers are added in each 'resource section' for better readability
RP = {}

RP['create_waiver'] = reqparse.RequestParser()
RP['create_waiver'].add_argument('result_id', type=int, required=True, location='json')
RP['create_waiver'].add_argument('waived', type=bool, required=True, location='json')
RP['create_waiver'].add_argument('product_version', type=str, required=True, location='json')
RP['create_waiver'].add_argument('comment', type=str, default=None, location='json')

RP['get_waivers'] = reqparse.RequestParser()
RP['get_waivers'].add_argument('result_id', location='args')
RP['get_waivers'].add_argument('product_version', location='args')
RP['get_waivers'].add_argument('username', location='args')
RP['get_waivers'].add_argument('include_obsolete', type=bool, default=False, location='args')
# XXX This matches the since query parameter in resultsdb but I think it would
# be good to use two parameters(since and until).
RP['get_waivers'].add_argument('since', location='args')
RP['get_waivers'].add_argument('page', default=1, type=int, location='args')
RP['get_waivers'].add_argument('limit', default=10, type=int, location='args')


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
        :query int result_id: Filter the waivers by result ID. Accepts one or
            more result IDs separated by commas.
        :query string product_version: Filter the waivers by product version.
        :query string username: Filter the waivers by username.
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
        if args['result_id']:
            query = query.filter(Waiver.result_id.in_(args['result_id'].split(',')))
        if args['product_version']:
            query = query.filter(Waiver.product_version == args['product_version'])
        if args['username']:
            query = query.filter(Waiver.username == args['username'])
        if args['since']:
            try:
                since_start, since_end = reqparse_since(args['since'])
            except:
                raise BadRequest("'since' parameter not in ISO8601 format")
            if since_start:
                query = query.filter(Waiver.timestamp >= since_start)
            if since_end:
                query = query.filter(Waiver.timestamp <= since_end)
        if not args['include_obsolete']:
            subquery = db.session.query(func.max(Waiver.id)).group_by(Waiver.result_id)
            query = query.filter(Waiver.id.in_(subquery))
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
               "result_id": 1,
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
               "result_id": 1,
               "timestamp": "2017-03-16T17:42:04.209638",
               "username": "jcline",
               "waived": false
           }

        :json int result_id: The result ID for the waiver.
        :json boolean waived: Whether or not the result is waived.
        :json string product_version: The product version string.
        :json string comment: A comment explaining the waiver.
        :statuscode 201: The waiver was successfully created.
        """
        user, headers = waiverdb.auth.get_user(request)
        args = RP['create_waiver'].parse_args()
        waiver = Waiver(args['result_id'], user, args['product_version'], args['waived'],
                        args['comment'])
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
        except:
            raise NotFound('Waiver not found')


class GetWaiversByResultIDs(Resource):
    @jsonp
    def post(self):
        """
        Return a list of waivers by filtering the waivers with a list of result ids.
        This accepts POST requests in order to handle a special case where a
        GET /waivers/ request has a long query string with many result ids that
        could cause 413 erros.

        **Sample request**:

        .. sourcecode:: http

           POST /api/v1.0/waivers/+by-result-ids HTTP/1.1
           Host: localhost:5004
           Accept-Encoding: gzip, deflate
           Accept: application/json
           Connection: keep-alive
           User-Agent: HTTPie/0.9.4
           Content-Type: application/json
           Content-Length: 40

           {
               "result_ids": [1,2]
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
                        "result_id": 2,
                        "timestamp": "2017-09-21T04:55:53.343368",
                        "username": "dummy",
                        "waived": true
                    },
                    {
                        "comment": "It's dead!",
                        "id": 4,
                        "product_version": "Parrot",
                        "result_id": 1,
                        "timestamp": "2017-09-21T04:55:51.936658",
                        "username": "dummy",
                        "waived": true
                    }
                ]
            }

        :jsonparam array result_ids: Filter the waivers by a list of result IDs.
        :jsonparam string product_version: Filter the waivers by product version.
        :jsonparam string username: Filter the waivers by username.
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
        if 'result_ids' in data and data['result_ids']:
            query = query.filter(Waiver.result_id.in_(data['result_ids']))
        if 'product_version' in data:
            query = query.filter(Waiver.product_version == data['product_version'])
        if 'username' in data:
            query = query.filter(Waiver.username == data['username'])
        if 'since' in data:
            try:
                since_start, since_end = reqparse_since(data['since'])
            except:
                raise BadRequest("'since' parameter not in ISO8601 format")
            if since_start:
                query = query.filter(Waiver.timestamp >= since_start)
            if since_end:
                query = query.filter(Waiver.timestamp <= since_end)
        if not data.get('include_obsolete', False):
            subquery = db.session.query(func.max(Waiver.id)).group_by(Waiver.result_id)
            query = query.filter(Waiver.id.in_(subquery))
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
api.add_resource(GetWaiversByResultIDs, '/waivers/+by-result-ids')
api.add_resource(AboutResource, '/about')
