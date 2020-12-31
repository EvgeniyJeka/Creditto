
class Offer(object):
    id = 1
    owner_id = None
    sum = None
    duration = None
    offered_interest = None
    status = None
    matching_bid = None

    def __init__(self, owner_id, sum, duration, offered_interest):

        # In future we will check the last offer ID assigned and take the next one
        self.id = Offer.id
        Offer.id += 1

        self.owner_id = owner_id
        self.sum = sum
        self.duration = duration
        self.offered_interest = offered_interest

    def __repr__(self) -> str:
        if self.status is None and  self.matching_bid is None:
            return f"Offer ID: {self.id}, Owner ID: {self.owner_id}, Sum: {self.sum}, Duration: {self.duration}," \
                f" Interest: {self.offered_interest}"
        else:
            return f"Offer ID: {self.id}, Owner ID: {self.owner_id}, Sum: {self.sum}, Duration: {self.duration}, " \
                f"Interest: {self.offered_interest}, Status: {self.status}, Matching Bid: {self.matching_bid}"



if __name__ == '__main__':
    of1 = Offer(1, 100, 5, 0.2)
    of2 = Offer(2, 110, 5, 0.2)
    of3 = Offer(3, 120, 5, 0.3)

    print(of1)
    print(of2)
    print(of3)





