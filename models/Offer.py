from statuses import OfferStatuses, Types
from datetime import datetime


class Offer(object):
    id = 1
    owner_id = None
    sum = None
    duration = None
    offered_interest = None
    status = None
    matching_bid = None

    def __init__(self, id, owner_id, sum, duration, offered_interest, allow_partial_fill, date_added=None, status=None):

        # In future we will check the last offer ID assigned and take the next one
        self.id = id

        self.type = Types.OFFER.value

        self.owner_id = owner_id
        self.sum = sum
        self.duration = duration
        self.offered_interest = offered_interest

        self.allow_partial_fill = allow_partial_fill

        # Current time is added on object creation. Should not be added on object deserialization
        if date_added is None:
            self.date_added = str(datetime.now())
        else:
            self.date_added = datetime.strptime(date_added, '%Y-%m-%d %H:%M:%S.%f')

        # Default status NEW is added on object creation. Should not be added on object deserialization
        if status is None:
            self.status = OfferStatuses.OPEN.value
        else:
            self.status = status


    def __repr__(self) -> str:
        if self.matching_bid is None:
            return f"Offer ID: {self.id}, Owner ID: {self.owner_id}, Sum: {self.sum}, Duration: {self.duration}," \
                f" Interest: {self.offered_interest}, Partial Fill Allowed: {self.allow_partial_fill}," \
                f" Date Added: {self.date_added} " \
                f"Status: {self.status}"
        else:
            return f"Offer ID: {self.id}, Owner ID: {self.owner_id}, Sum: {self.sum}, Duration: {self.duration}, " \
                f"Interest: {self.offered_interest}, Partial Fill Allowed: {self.allow_partial_fill}, " \
                f"Date Added: {self.date_added} " \
                f"Status: {self.status}, Matching Bid: {self.matching_bid}"



if __name__ == '__main__':
    of1 = Offer(1, 100, 5, 0.2)
    of2 = Offer(2, 110, 5, 0.2)
    of3 = Offer(3, 120, 5, 0.3)

    print(of1)
    print(of2)
    print(of3)





