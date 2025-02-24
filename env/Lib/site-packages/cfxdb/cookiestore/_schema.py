##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import zlmdb
from cfxdb.cookiestore._cookie import Cookies, IndexCookiesByValue


class CookieStoreSchema(object):
    """
    Persistent cookie store.
    """
    def __init__(self, db):
        self.db = db

    cookies: Cookies
    """
    Cookies persisted in this cookie store.
    """

    idx_cookies_by_value: IndexCookiesByValue
    """
    Index of cookies by cookie value.
    """

    @staticmethod
    def attach(db: zlmdb.Database) -> 'CookieStoreSchema':
        """
        Factory to create a schema from attaching to a database. The schema tables
        will be automatically mapped as persistent maps and attached to the
        database slots.
        """
        schema = CookieStoreSchema(db)

        schema.cookies = db.attach_table(Cookies)

        schema.idx_cookies_by_value = db.attach_table(IndexCookiesByValue)
        schema.cookies.attach_index('idx1', schema.idx_cookies_by_value, lambda cookie: cookie.value)

        return schema
