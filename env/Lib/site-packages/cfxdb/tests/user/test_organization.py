##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import uuid
from datetime import datetime

import flatbuffers
import pytest
import cbor2
import txaio

from cfxdb.user import Organization, OrganizationFbs

txaio.use_twisted()


def fill_org(org):
    org.oid = uuid.uuid4()
    org.label = 'My Org 1'
    org.description = 'Personal organization, created from unit test.'
    org.tags = ['previews', 'smb']
    org.name = 'homer23'
    org.otype = 1
    org.registered = datetime.utcnow()


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


@pytest.fixture(scope='function')
def org_fbs():
    org = OrganizationFbs()
    fill_org(org)
    return org


@pytest.fixture(scope='function')
def org_cbor():
    org = Organization()
    fill_org(org)
    return org


def test_org_fbs_roundtrip(org_fbs, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = org_fbs.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 192

    # create python object from bytes (flatbuffes)
    _org = OrganizationFbs.cast(data)

    # assert _org == org_fbs

    assert _org.oid == org_fbs.oid
    assert _org.label == org_fbs.label
    assert _org.description == org_fbs.description
    assert _org.tags == org_fbs.tags
    assert _org.name == org_fbs.name
    assert _org.otype == org_fbs.otype
    assert _org.registered == org_fbs.registered


def test_org_copy_fbs_to_cbor(org_fbs):
    org_cbor = Organization()
    org_cbor.copy(org_fbs)

    # assert org_cbor == org_fbs

    assert org_cbor.oid == org_fbs.oid
    assert org_cbor.label == org_fbs.label
    assert org_cbor.description == org_fbs.description
    assert org_cbor.tags == org_fbs.tags
    assert org_cbor.name == org_fbs.name
    assert org_cbor.otype == org_fbs.otype
    assert org_cbor.registered == org_fbs.registered


def test_org_cbor_roundtrip(org_cbor):
    # serialize to bytes (cbor) from python object
    obj = org_cbor.marshal()
    data = cbor2.dumps(obj)
    assert len(data) == 177

    # create python object from bytes (cbor)
    _obj = cbor2.loads(data)
    _org = Organization.parse(_obj)

    # assert _org == org_cbor

    assert _org.oid == org_cbor.oid
    assert _org.label == org_cbor.label
    assert _org.description == org_cbor.description
    assert _org.tags == org_cbor.tags
    assert _org.name == org_cbor.name
    assert _org.otype == org_cbor.otype
    assert _org.registered == org_cbor.registered


def test_org_copy_cbor_to_fbs(org_cbor):

    org_fbs = OrganizationFbs()
    org_fbs.copy(org_cbor)

    # assert org_fbs == org_cbor

    assert org_fbs.oid == org_cbor.oid
    assert org_fbs.label == org_cbor.label
    assert org_fbs.description == org_cbor.description
    assert org_fbs.tags == org_cbor.tags
    assert org_fbs.name == org_cbor.name
    assert org_fbs.otype == org_cbor.otype
    assert org_fbs.registered == org_cbor.registered
