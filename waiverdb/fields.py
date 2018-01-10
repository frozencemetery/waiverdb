# SPDX-License-Identifier: GPL-2.0+

from flask_restful import fields


waiver_fields = {
    'id': fields.Integer,
    'subject': fields.Raw,
    'testcase': fields.String,
    'username': fields.String,
    'proxied_by': fields.String,
    'product_version': fields.String,
    'waived': fields.Boolean,
    'comment': fields.String,
    'timestamp': fields.DateTime(dt_format='iso8601'),
}
