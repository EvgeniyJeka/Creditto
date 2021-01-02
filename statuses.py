from enum import Enum


class OfferStatuses(Enum):
    OPEN = 1
    MATCHED = 2
    PARTIALLY_MATCHED = 3
    CANCELLED = 4
    REMOVED = 5
    HIDDEN = 6

class BidStatuses(Enum):
    PLACED = 1
    MATCHED = 2
    CANCELLED = 3
    REMOVED = 4
    HIDDEN = 5

class Types(Enum):
    OFFER = 'offer'
    BID = 'bid'
    MATCH = 'match'