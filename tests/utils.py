# SPDX-License-Identifier: GPL-2.0+

from waiverdb.models import Waiver


def create_waiver(session, result_id, username, product_version, waived=True,
                  comment=None):
    waiver = Waiver(result_id, username, product_version, waived, comment)
    session.add(waiver)
    session.flush()
    return waiver
