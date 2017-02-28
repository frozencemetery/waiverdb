
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from flask_restful import fields

waiver_fields = {
    'id': fields.Integer,
    'result_id': fields.Integer,
    'username': fields.String,
    'product_version': fields.String,
    'waived': fields.Boolean,
    'comment': fields.String,
    'timestamp': fields.DateTime(dt_format='iso8601'),
}
