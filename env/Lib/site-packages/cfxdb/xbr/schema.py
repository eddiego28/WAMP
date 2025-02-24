##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from .actor import Actors
from .api import Apis, IndexApiByCatalog
from .block import Blocks
from .catalog import Catalogs, IndexCatalogsByOwner

from cfxdb.xbr.consent import Consents, IndexConsentByMemberAddress

from cfxdb.xbrmm.channel import PaymentChannels, IndexPaymentChannelByDelegate, \
    IndexPaymentChannelByActor, PaymentChannelBalances, PayingChannels, IndexPayingChannelByDelegate, \
    IndexPayingChannelByRecipient, PayingChannelBalances

from .market import Markets, IndexMarketsByOwner, IndexMarketsByActor, IndexMarketsByMaker
from .member import Members
from cfxdb.xbrmm.offer import Offers, IndexOfferByKey
from .token import TokenApprovals, TokenTransfers
from cfxdb.xbrmm.transaction import Transactions


class Schema(object):
    """
    CFC edge database schema for ZLMDB.
    """
    def __init__(self, db):
        self.db = db

    blocks: Blocks
    """
    Ethereum blocks basic information.
    """

    token_approvals: TokenApprovals
    """
    Token approvals archive.
    """

    token_transfers: TokenTransfers
    """
    Token transfers archive.
    """

    members: Members
    """
    XBR network members.
    """

    catalogs: Catalogs
    """
    XBR network catalogs.
    """

    idx_catalogs_by_owner: IndexCatalogsByOwner
    """
    Index ``(member_oid, created) -> catalog_oid``.
    """

    apis: Apis
    """
    XBR network apis.
    """

    idx_apis_by_catalog: IndexApiByCatalog
    """
    Index ``catalog_oid -> api_oid``.
    """

    markets: Markets
    """
    XBR markets.
    """

    idx_markets_by_owner: IndexMarketsByOwner
    """
    Index ``(owner_adr, created) -> market_oid``.
    """

    idx_markets_by_actor: IndexMarketsByActor
    """
    Index ``(actor_adr, joined) -> market_oid``.
    """

    idx_markets_by_maker: IndexMarketsByMaker
    """
    Index ``maker_adr -> market_oid``.
    """

    actors: Actors
    """
    XBR market actors.
    """

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
    Maps from XBR (buyer) actor address to the currently active payment
    channel address for the given actor.
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
    Maps from XBR seller actor address to the currently active paying
    channel address for the given actor.
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

        schema.apis = db.attach_table(Apis)

        schema.idx_apis_by_catalog = db.attach_table(IndexApiByCatalog)

        schema.blocks = db.attach_table(Blocks)

        schema.catalogs = db.attach_table(Catalogs)

        schema.idx_catalogs_by_owner = db.attach_table(IndexCatalogsByOwner)

        schema.catalogs.attach_index('idx1', schema.idx_catalogs_by_owner, lambda catalog:
                                     (catalog.owner, catalog.timestamp))

        schema.consents = db.attach_table(Consents)

        schema.idx_consent_by_member_adr = db.attach_table(IndexConsentByMemberAddress)

        schema.token_approvals = db.attach_table(TokenApprovals)

        schema.token_transfers = db.attach_table(TokenTransfers)

        schema.members = db.attach_table(Members)

        schema.markets = db.attach_table(Markets)

        schema.idx_markets_by_owner = db.attach_table(IndexMarketsByOwner)

        schema.markets.attach_index('idx1', schema.idx_markets_by_owner, lambda market:
                                    (market.owner, market.timestamp))

        schema.actors = db.attach_table(Actors)
        schema.idx_markets_by_actor = db.attach_table(IndexMarketsByActor)

        # FIXME: we manually maintain the index, and hence must mark the pmap as an index manually
        # schema.idx_markets_by_actor._index_attached_to = schema.actors
        # schema.actors.attach_index('idx1', schema.idx_markets_by_actor, lambda actor:
        #                            (actor.actor, actor.timestamp))

        schema.idx_markets_by_maker = db.attach_table(IndexMarketsByMaker)
        schema.markets.attach_index('idx3', schema.idx_markets_by_maker, lambda market: market.maker)

        schema.payment_channels = db.attach_table(PaymentChannels)

        schema.idx_payment_channel_by_delegate = db.attach_table(IndexPaymentChannelByDelegate)
        schema.payment_channels.attach_index(
            'idx1', schema.idx_payment_channel_by_delegate, lambda payment_channel:
            (bytes(payment_channel.delegate), payment_channel.timestamp))

        schema.idx_payment_channel_by_actor = db.attach_table(IndexPaymentChannelByActor)
        schema.payment_channels.attach_index(
            'idx2', schema.idx_payment_channel_by_actor, lambda payment_channel:
            (bytes(payment_channel.actor), payment_channel.timestamp))

        schema.payment_balances = db.attach_table(PaymentChannelBalances)

        schema.paying_channels = db.attach_table(PayingChannels)

        schema.idx_paying_channel_by_delegate = db.attach_table(IndexPayingChannelByDelegate)
        schema.paying_channels.attach_index(
            'idx1', schema.idx_paying_channel_by_delegate, lambda paying_channel:
            (bytes(paying_channel.delegate), paying_channel.timestamp))

        schema.idx_paying_channel_by_recipient = db.attach_table(IndexPayingChannelByRecipient)
        schema.paying_channels.attach_index(
            'idx2', schema.idx_paying_channel_by_recipient, lambda paying_channel:
            (bytes(paying_channel.recipient), paying_channel.timestamp))

        schema.paying_balances = db.attach_table(PayingChannelBalances)

        schema.offers = db.attach_table(Offers)
        schema.idx_offer_by_key = db.attach_table(IndexOfferByKey)
        schema.offers.attach_index('idx1', schema.idx_offer_by_key, lambda offer: offer.key)

        schema.transactions = db.attach_table(Transactions)

        return schema
