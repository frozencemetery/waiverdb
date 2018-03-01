
# SPDX-License-Identifier: GPL-2.0+

from collections import OrderedDict
from waiverdb.models import Waiver


# https://pagure.io/waiverdb/issue/134
def test_waiver_subject_json_serialization_is_consistent(db):
    # With the default json.dumps serializer, the order of keys in the
    # serialized JSON object could vary because dict keys are iterated in
    # arbitrary order. Hence we have a custom serializer to guarantee the
    # serialization is predictable, regardless of iteration order.
    # In this test we therefore use OrderedDict and not dict, specifically so
    # we can guarantee that the iteration order is *not* the same in each
    # object.
    nvr = 'python-requests-1.2.3-1.fc26'
    subject = OrderedDict([('item', nvr), ('type', 'koji_build')])
    equivalent_subject = OrderedDict([('type', 'koji_build'), ('item', nvr)])
    waiver = Waiver(username='dcallagh', waived=True, comment='test', product_version='fedora-26',
                    testcase='dist.rpmlint', subject=subject)
    db.session.add(waiver)
    waiver = Waiver(username='dcallagh', waived=True, comment='test', product_version='fedora-26',
                    testcase='dist.rpmlint', subject=equivalent_subject)
    db.session.add(waiver)
    db.session.flush()
    query = Waiver.query.filter(Waiver.subject == {'item': nvr, 'type': 'koji_build'})
    # The query should select *both* the waivers above
    assert query.count() == 2
