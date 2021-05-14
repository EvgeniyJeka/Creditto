from statuses import BidStatuses, Types
from datetime import datetime


class Bid(object):
    id = 1
    owner_id = None
    bid_interest = None
    status = None
    target_offer = None
    sum = None
    partial_only = None
    partial_sum = 0

    def __init__(self, id, owner_id, bid_interest, target_offer_id, partial_only, partial_sum=None,
                 date_added=None, status=None):

        self.id = id
        self.type = Types.BID.value

        self.owner_id = owner_id
        self.bid_interest = bid_interest
        self.target_offer_id = target_offer_id

        if partial_only:
            self.partial_only = 1
            self.partial_sum = partial_sum

        else:
            self.partial_only = 0

        # Current time is added on object creation. Should not be added on object deserialization
        if date_added is None:
            self.date_added = str(datetime.now())
        else:
            self.date_added = datetime.strptime(date_added, '%Y-%m-%d %H:%M:%S.%f')

        # Default status NEW is added on object creation. Should not be added on object deserialization
        if status is None:
            self.status = BidStatuses.PLACED.value
        else:
            self.status = status

    def __repr__(self):

        if self.partial_only and self.partial_sum:
            return f"Owner ID: {self.owner_id}, Bid Interest: {self.bid_interest}, Target Offer ID: {self.target_offer_id}, " \
                f"Bid Status: {self.status}, Partial Bid: {self.partial_only}, Sum suggested: {self.partial_sum},  " \
                f"Date Added: {self.date_added}, Status: {self.status}"
        else:
            return f"Owner ID: {self.owner_id}, Bid Interest: {self.bid_interest}, Target Offer ID: {self.target_offer_id}, " \
                f"Bid Status: {self.status}, Partial Bid: {self.partial_only}, Date Added: {self.date_added}, " \
                f"Status: {self.status} "
