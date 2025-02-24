##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from .activation_token import ActivationToken
from .organization import Organization
from .user import User
from .user_mrealm_role import UserMrealmRole


class Schema(object):
    """
    user database schema for ZLMDB.
    """
    def __init__(self, db):
        self.db = db

    activation_tokens: ActivationToken
    """
    CFC user activation tokens.
    """

    organizations: Organization
    """
    CFC organization.
    """

    users: User
    """
    CFC users.
    """

    user_mrealm_roles: UserMrealmRole
    """
    CFC user roles.
    """

    @staticmethod
    def attach(db):
        """
        Factory to create a schema from attaching to a database. The schema tables
        will be automatically mapped as persistant maps and attached to the
        database slots.

        :param db: zlmdb.Database
        :return: object of Schema
        """
        schema = Schema(db)

        schema.activation_tokens = db.attach_table(ActivationToken)

        schema.organizations = db.attach_table(Organization)

        schema.users = db.attach_table(User)

        schema.user_mrealm_roles = db.attach_table(UserMrealmRole)

        return schema
