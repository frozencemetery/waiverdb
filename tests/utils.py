
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

from waiverdb.models import Waiver


def create_waiver(session, result_id, username, product_version, waived=True,
                  comment=None):
    waiver = Waiver(result_id, username, product_version, waived, comment)
    session.add(waiver)
    session.flush()
    return waiver
