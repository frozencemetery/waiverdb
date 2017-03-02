
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal_with
from werkzeug.exceptions import HTTPException, BadRequest, NotFound
from sqlalchemy.sql.expression import func

from waiverdb.models import db, Waiver
from waiverdb.utils import reqparse_since, json_collection
from waiverdb.fields import waiver_fields

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

    def get(self):
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

    @marshal_with(waiver_fields)
    def post(self):
        args = RP['create_waiver'].parse_args()
        # hardcode the username for now
        username = 'mjia'
        waiver = Waiver(args['result_id'], username, args['product_version'], args['waived'],
                args['comment'])
        db.session.add(waiver)
        db.session.commit()
        return waiver, 201


class WaiverResource(Resource):
    @marshal_with(waiver_fields)
    def get(self, waiver_id):
        try:
            return Waiver.query.get_or_404(waiver_id)
        except:
            raise NotFound('Waiver not found')

# set up the Api resource routing here
api.add_resource(WaiversResource, '/waivers/')
api.add_resource(WaiverResource, '/waivers/<int:waiver_id>')
