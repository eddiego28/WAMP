##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from cfxdb.xbr.consent import Consents, IndexConsentByMemberAddress

from cfxdb.xbrmm.channel import PaymentChannels, IndexPaymentChannelByDelegate, \
    IndexPaymentChannelByActor, PaymentChannelBalances, PayingChannels, IndexPayingChannelByDelegate, \
    IndexPayingChannelByRecipient, PayingChannelBalances

from cfxdb.xbrmm.offer import Offers, IndexOfferByKey
from cfxdb.xbrmm.transaction import Transactions
from cfxdb.xbrmm.ipfs_file import IPFSFiles
from cfxdb.xbrmm.userkey import UserKeys, IndexUserKeyByMember


class Schema(object):
    """
    CFC edge database schema for ZLMDB.
    """
    def __init__(self, db):
        self.db = db

    consents: Consents
    """
    XBR data consents.
    """

    idx_consent_by_member_adr: IndexConsentByMemberAddress
    """
    Consents-by-members-address index with ``(member_adr|bytes[20], joined|int) -> member_adr|UUID`` mapping.
    """

    payment_channels: PaymentChannels
    """
    Payment channels for XBR consumer delegates.
    """

    idx_payment_channel_by_delegate: IndexPaymentChannelByDelegate
    """
    Maps from XBR consumer delegate address to the currently active payment
    channel address for the given consumer delegate.
    """

    idx_payment_channel_by_actor: IndexPaymentChannelByActor
    """
    Maps from XBR consumer actor address to the currently active payment
    channel address for the given consumer actor.
    """

    payment_balances: PaymentChannelBalances
    """
    Current off-chain balances within payment channels.
    """

    paying_channels: PayingChannels
    """
    Paying channels for XBR provider delegates.
    """

    idx_paying_channel_by_delegate: IndexPayingChannelByDelegate
    """
    Maps from XBR provider delegate address to the currently active paying
    channel address for the given provider delegate.
    """

    idx_paying_channel_by_recipient: IndexPayingChannelByRecipient
    """
    Maps from XBR recipient address to the currently active paying
    channel address for the given recipient.
    """

    paying_balances: PayingChannelBalances
    """
    Current off-chain balances within paying channels.
    """

    offers: Offers
    """
    Data encryption key offers.
    """

    idx_offer_by_key: IndexOfferByKey
    """
    Index of key offers by key ID (rather than offer ID, as the object table
    is indexed by).
    """

    transactions: Transactions
    """
    """

    user_keys: UserKeys
    """
    User client keys database table :class:`xbrmm.UserKeys`.
    """

    idx_user_key_by_member: IndexUserKeyByMember
    """
    Index "by pubkey" of user keys :class:`xbrmm.IndexUserKeyByMember`.
    """

    ipfs_files: IPFSFiles
    """
    IPFS files download log table :class:`xbrmm.IPFSFiles`.
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

        schema.consents = db.attach_table(Consents)

        schema.idx_consent_by_member_adr = db.attach_table(IndexConsentByMemberAddress)

        schema.payment_channels = db.attach_table(PaymentChannels)

        schema.idx_payment_channel_by_delegate = db.attach_table(IndexPaymentChannelByDelegate)
        schema.payment_channels.attach_index('idx1', schema.idx_payment_channel_by_delegate, lambda channel:
                                             (bytes(channel.delegate), channel.timestamp))

        schema.idx_payment_channel_by_actor = db.attach_table(IndexPaymentChannelByActor)
        schema.payment_channels.attach_index('idx2', schema.idx_payment_channel_by_actor, lambda channel:
                                             (bytes(channel.actor), channel.timestamp))

        schema.payment_balances = db.attach_table(PaymentChannelBalances)

        schema.paying_channels = db.attach_table(PayingChannels)

        schema.idx_paying_channel_by_delegate = db.attach_table(IndexPayingChannelByDelegate)
        schema.paying_channels.attach_index('idx1', schema.idx_paying_channel_by_delegate, lambda channel:
                                            (bytes(channel.delegate), channel.timestamp))

        schema.idx_paying_channel_by_recipient = db.attach_table(IndexPayingChannelByRecipient)
        schema.paying_channels.attach_index('idx2', schema.idx_paying_channel_by_recipient, lambda channel:
                                            (bytes(channel.recipient), channel.timestamp))

        schema.paying_balances = db.attach_table(PayingChannelBalances)

        schema.offers = db.attach_table(Offers)
        schema.idx_offer_by_key = db.attach_table(IndexOfferByKey)
        schema.offers.attach_index('idx1', schema.idx_offer_by_key, lambda offer: offer.key)

        schema.user_keys = db.attach_table(UserKeys)

        schema.idx_user_key_by_member = db.attach_table(IndexUserKeyByMember)
        schema.user_keys.attach_index('idx1', schema.idx_user_key_by_member, lambda user_key:
                                      (user_key.owner, user_key.created))

        schema.transactions = db.attach_table(Transactions)

        schema.ipfs_files = db.attach_table(IPFSFiles)

        return schema
