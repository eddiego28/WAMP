##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import json

from .account import Accounts, IndexAccountsByUsername, IndexAccountsByEmail, IndexAccountsByWallet
from .userkey import UserKeys, IndexUserKeyByAccount
from .vaction import VerifiedActions


class Schema(object):
    """
    XBR Network backend database schema.
    """
    accounts: Accounts
    """
    Member accounts database table :class:`xbrnetwork.Accounts`.
    """

    idx_accounts_by_username: IndexAccountsByUsername
    """
    Index "by username" of member accounts :class:`xbrnetwork.IndexAccountsByUsername`.
    """

    idx_accounts_by_email: IndexAccountsByEmail
    """
    Index "by email" of member accounts :class:`xbrnetwork.IndexAccountsByEmail`.
    """

    idx_accounts_by_wallet: IndexAccountsByWallet
    """
    Index "by wallet" of member accounts :class:`xbrnetwork.IndexAccountsByWallet`.
    """

    verified_actions: VerifiedActions
    """
    Verified actions database table :class:`xbrnetwork.VerifiedActions`.
    """

    user_keys: UserKeys
    """
    User client keys database table :class:`xbrnetwork.UserKeys`.
    """

    idx_user_key_by_account: IndexUserKeyByAccount
    """
    Index "by pubkey" of user keys :class:`xbrnetwork.IndexUserKeyByAccount`.
    """

    EXPORTED = None
    """
    """
    def __init__(self, db):
        self.db = db

    def export(self, txn, fd):
        """

        :param txn:
        :param fd:
        :return:
        """
        recs = 0
        db_data = {}
        for table in self.EXPORTED:
            table_data = []
            for key, val in table.select(txn, return_keys=True, return_values=True):
                table_data.append((key, val.marshal() if val else None))
                recs += 1
            db_data[table.__name__] = table_data
        db_data = json.dumps(db_data, ensure_ascii=False)
        fd.write(db_data)
        return recs

    @staticmethod
    def attach(db):
        """
        Attach database schema to database instance.

        :param db: Database to attach schema to.
        :type db: :class:`zlmdb.Database`
        """
        schema = Schema(db)

        schema.accounts = db.attach_table(Accounts)

        schema.idx_accounts_by_username = db.attach_table(IndexAccountsByUsername)
        schema.accounts.attach_index('idx1', schema.idx_accounts_by_username,
                                     lambda account: account.username)

        schema.idx_accounts_by_email = db.attach_table(IndexAccountsByEmail)
        schema.accounts.attach_index('idx2', schema.idx_accounts_by_email, lambda account: account.email)

        schema.idx_accounts_by_wallet = db.attach_table(IndexAccountsByWallet)
        schema.accounts.attach_index('idx3', schema.idx_accounts_by_wallet,
                                     lambda account: account.wallet_address)

        schema.verified_actions = db.attach_table(VerifiedActions)

        schema.user_keys = db.attach_table(UserKeys)

        schema.idx_user_key_by_account = db.attach_table(IndexUserKeyByAccount)
        schema.user_keys.attach_index('idx1', schema.idx_user_key_by_account, lambda user_key:
                                      (user_key.owner, user_key.created))

        schema.EXPORTED = [schema.accounts, schema.verified_actions, schema.user_keys]

        return schema
