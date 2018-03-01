# SPDX-License-Identifier: GPL-2.0+

import json
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql.psycopg2 import _PGJSON
from sqlalchemy.sql.elements import ColumnElement, Null
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.sqltypes import Text
from flask_sqlalchemy import SQLAlchemy


json_serializer = json.encoder.JSONEncoder(sort_keys=True, separators=(',', ':')).encode


# Note that we have to inherit from the psycopg2-specific _PGJSON type,
# instead of the more general Postgres-specific JSON type. That's because
# SQLAlchemy helpfully "adapts" the general JSON type to _PGJSON when it sees
# we are using psycopg2, thereby defeating our customisations below.
# Inheriting from _PGJSON tells SQLAlchemy not do that adaptation.
# The magic occurs in SQLALchemy adapt_type() and PGDialect_psycopg2.colspecs.
class EqualityComparableJSONType(_PGJSON):
    """
    Like the standard JSON column type, but supports equality comparison of
    entire JSON structures. Postgres doesn't permit this natively on the JSON
    type so we have to instead cast to TEXT before comparing (and therefore we
    have to also go to lengths to ensure the JSON we feed in is consistently
    serialized).
    """

    class Comparator(JSON.Comparator):

        def __eq__(self, other):
            # If the RHS is a SQL expression, just assume its SQL type is
            # already JSON and thus CAST(AS TEXT) it as well.
            if isinstance(other, ColumnElement):
                rhs = cast(other, Text)
            else:
                rhs = json_serializer(other)
            return cast(self.expr, Text) == rhs

    comparator_factory = Comparator

    def bind_processor(self, dialect):
        def process(value):
            # JSON.NULL is a sentinel object meaning JSON "null" (SQLAlchemy 1.1+ only)
            if hasattr(self, 'NULL') and value is self.NULL:
                value = None
            elif isinstance(value, Null) or (value is None and self.none_as_null):
                return None
            return json_serializer(value)
        return process

    def result_processor(self, dialect, coltype):
        if dialect._has_native_json:  # pylint: disable=W0212
            return None

        def process(value):
            if value is None:
                return None
            return json.loads(value)
        return process


db = SQLAlchemy()
