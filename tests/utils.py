# SPDX-License-Identifier: GPL-2.0+

from waiverdb.models import Waiver


def create_waiver(session, subject, testcase, username, product_version, waived=True,
                  comment=None, proxied_by=None):
    waiver = Waiver(subject, testcase, username, product_version, waived, comment,
                    proxied_by)
    session.add(waiver)
    session.flush()
    return waiver
