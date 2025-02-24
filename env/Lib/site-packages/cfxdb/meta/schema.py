##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from zlmdb import table
from zlmdb import MapUuidCbor, MapSlotUuidUuid

from .attribute import Attributes


#
# Docs metadata
#
@table('e11680d5-e20c-40b1-97d9-380b5ace1cb3', marshal=(lambda x: x), parse=(lambda x: x))
class Docs(MapUuidCbor):
    """
    * Database table: ``doc_oid -> doc``
    * Table type :class:`zlmdb.MapUuidCbor`
    * Key type :class:`uuid.UUID`
    * Record type :class:`cfxdb.mrealmschema.Doc`
    """


@table('d1de0b8c-3b6d-488b-8778-5bac8528ab4b')
class IndexObjectToDoc(MapSlotUuidUuid):
    """
    * Database index table ``(object_slot, object_oid) -> doc_oid``
    * Table type :class:`zlmdb.MapSlotUuidUuid`
    * Key type :class:`typing.Tuple[int, uuid.UUID]`
    * Indexed table :class:`cfxdb.mrealmschema.Docs`
    """


class Schema(object):
    """
    Generic metadata, like documentation, tags, comments and reactions that
    can be attach on any object with an UUID.
    """

    attributes: Attributes
    """
    Generic **meta data attributes** for objects in other tables.
    Primary key of this table is ``(table_oid, object_oid, attribute)``.
    """

    docs: Docs
    """
    Documentation attached to a database object.

    * Database table :class:`cfxdb.mrealmschema.Docs`
    """

    idx_object_to_doc: IndexObjectToDoc
    """
    Index on documentation: by documented object ID

    * Database table :class:`cfxdb.mrealmschema.IndexObjectToDoc`
    """
    def __init__(self, db):
        self.db = db

    @staticmethod
    def attach(db):
        """
        Attach database schema to database instance.

        :param db: Database to attach schema to.
        :type db: :class:`zlmdb.Database`
        """
        schema = Schema(db)

        schema.attributes = db.attach_table(Attributes)

        schema.docs = db.attach_table(Docs)
        schema.idx_object_to_doc = db.attach_table(IndexObjectToDoc)
        schema.docs.attach_index('idx1', schema.idx_object_to_doc, lambda obj: obj.oid)

        return schema
