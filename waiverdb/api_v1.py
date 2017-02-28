
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

from waiverdb.models import db, Waiver
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


class WaiversResource(Resource):
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
