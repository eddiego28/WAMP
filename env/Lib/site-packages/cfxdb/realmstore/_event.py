##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import pprint

from zlmdb import table, MapOidTimestampFlatBuffers

from cfxdb.gen.realmstore import Event as EventGen


class Event(object):
    """
    Persisted event database object.
    """
    def __init__(self, from_fbs=None):
        self._from_fbs = from_fbs

        self._timestamp = None
        self._subscription = None
        self._publication = None
        self._receiver = None
        self._retained = None
        self._acknowledged_delivery = None

    def marshal(self):
        obj = {
            'timestamp': self.timestamp,
            'subscription': self.subscription,
            'publication': self.publication,
            'receiver': self.receiver,
            'retained': self.retained,
            'acknowledged_delivery': self.acknowledged_delivery,
        }
        return obj

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    @property
    def timestamp(self):
        """
        Timestamp when the event was sent to the receiver. Epoch time in ns.

        :returns: Epoc time in ns.
        :rtype: int
        """
        if self._timestamp is None and self._from_fbs:
            self._timestamp = self._from_fbs.Timestamp()
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        assert type(value) == int
        self._timestamp = value

    @property
    def subscription(self):
        """
        The subscription ID this event is dispatched under.

        :returns: The subscription ID.
        :rtype: int
        """
        if self._subscription is None and self._from_fbs:
            self._subscription = self._from_fbs.Subscription()
        return self._subscription

    @subscription.setter
    def subscription(self, value):
        assert type(value) == int
        self._subscription = value

    @property
    def publication(self):
        """
        The publication ID of the dispatched event.

        :returns: The publication ID.
        :rtype: int
        """
        if self._publication is None and self._from_fbs:
            self._publication = self._from_fbs.Publication()
        return self._publication

    @publication.setter
    def publication(self, value):
        assert type(value) == int
        self._publication = value

    @property
    def receiver(self):
        """
        The WAMP session ID of the receiver.

        :returns: The receiver ID.
        :rtype: int
        """
        if self._receiver is None and self._from_fbs:
            self._receiver = self._from_fbs.Receiver()
        return self._receiver

    @receiver.setter
    def receiver(self, value):
        assert type(value) == int
        self._receiver = value

    @property
    def retained(self):
        """
        Whether the message was retained by the broker on the topic, rather than just published.

        :returns: retained flag
        :rtype: bool
        """
        if self._retained is None and self._from_fbs:
            self._retained = self._from_fbs.Retained()
        return self._retained

    @retained.setter
    def retained(self, value):
        assert type(value) == bool
        self._retained = value

    @property
    def acknowledged_delivery(self):
        """
        Whether this Event was to be acknowledged by the receiver.

        :returns: acknowledged delivery flag
        :rtype: bool
        """
        if self._acknowledged_delivery is None and self._from_fbs:
            self._acknowledged_delivery = self._from_fbs.AcknowledgedDelivery()
        return self._acknowledged_delivery

    @acknowledged_delivery.setter
    def acknowledged_delivery(self, value):
        assert type(value) == bool
        self._acknowledged_delivery = value

    @staticmethod
    def cast(buf):
        return Event(EventGen.Event.GetRootAsEvent(buf, 0))

    def build(self, builder):

        # now start and build a new object ..
        EventGen.EventStart(builder)

        EventGen.EventAddTimestamp(builder, self.timestamp)
        EventGen.EventAddSubscription(builder, self.subscription)
        EventGen.EventAddPublication(builder, self.publication)
        EventGen.EventAddReceiver(builder, self.receiver)

        if self.retained is not None:
            EventGen.EventAddRetained(builder, self.retained)
        if self.acknowledged_delivery is not None:
            EventGen.EventAddAcknowledgedDelivery(builder, self.acknowledged_delivery)

        # finish the object.
        final = EventGen.EventEnd(builder)

        return final


@table('40a9df31-6065-496f-809f-027a1879654c', build=Event.build, cast=Event.cast)
class Events(MapOidTimestampFlatBuffers):
    """
    Persisted events archive.


    Map :class:`zlmdb.MapOid3FlatBuffers` from ``(subscription, time_ns)`` to :class:`cfxdb.eventstore.Event`.
    """
