
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
from flask_restful import reqparse
from werkzeug.exceptions import HTTPException

from waiverdb.models import db, Waiver
from waiverdb.utils import to_json

api = Blueprint('api_v1', __name__)

# RP contains request parsers (reqparse.RequestParser).
#    Parsers are added in each 'resource section' for better readability
RP = {}

RP['create_waiver'] = reqparse.RequestParser()
RP['create_waiver'].add_argument('result_id', type=int, required=True, location='json')
RP['create_waiver'].add_argument('waived', type=bool, required=True, location='json')
RP['create_waiver'].add_argument('product_version', type=str, required=True, location='json')
RP['create_waiver'].add_argument('comment', type=str, default=None, location='json')

@api.route('/waivers/', methods=['POST'])
@to_json
def create_waiver():
    try:
        args = RP['create_waiver'].parse_args()
    except HTTPException as error:
        return error.data, error.code

    # hardcode the username for now
    username = 'mjia'

    waiver = Waiver(args['result_id'], username, args['product_version'], args['waived'],
            args['comment'])

    db.session.add(waiver)
    db.session.commit()
    return waiver, 201
