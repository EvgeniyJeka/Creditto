from credittomodels import Match
from credittomodels import Offer
from credittomodels import Bid
from SqlBasic import SqlBasic
from credittomodels import statuses
from credittomodels import objects_mapped

# Refactor all methods - use SQL Alchemy to perform all SQL operations


class SqlWriter(SqlBasic):

    def __init__(self):
        super().__init__()
        #self.create_validate_tables(self.cursor)

    def insert_offer(self, offer: Offer):
        """
        This method can be used to insert new Offer to SQL table 'offers'.
        Offer object is expected
        """
        inserted_offer = objects_mapped.OfferMapped(id=offer.id, owner_id=offer.owner_id,
                                                    sum=offer.sum, duration=offer.duration,
                                                    offered_interest=offer.offered_interest,
                                                    final_interest=offer.final_interest,
                                                    allow_partial_fill=offer.allow_partial_fill,
                                                    date_added=offer.date_added,
                                                    status=offer.status)

        self.session.add(inserted_offer)
        self.session.commit()


    def insert_bid(self, bid: Bid):
        """
        This method can be used to insert new Bid to SQL table 'bids'.
        Bid object is expected
        """
        inserted_bid = objects_mapped.BidMapped(id=bid.id, owner_id=bid.owner_id, bid_interest=bid.bid_interest,
                                                target_offer_id=bid.target_offer_id, partial_only=bid.partial_only,
                                                date_added=bid.date_added, status=bid.status)

        self.session.add(inserted_bid)
        self.session.commit()


    def insert_match(self, match: Match):
        """
        Inserting received Match object fields to SQL table 'matches'
        :param match: Match object
        :return:
        """
        new_match_id = self.get_next_id('matches')
        inserted_match = objects_mapped.MatchesMapped(id=new_match_id,
                                                      offer_id=match.offer_id,
                                                      bid_id=match.bid_id,
                                                      offer_owner_id=match.offer_owner_id,
                                                      bid_owner_id=match.bid_owner_id,
                                                      match_time=match.match_time,
                                                      partial=match.partial,
                                                      final_interest=match.final_interest,
                                                      monthly_payment=match.monthly_payment)

        self.session.add(inserted_match)
        self.session.commit()

    def update_offer_status_sql(self, offer_id: int, new_status):
        """
        This method can be used to update offer status in SQL table 'offers'.
        Offer ID and new offer status is expected
        """
        updated_offer = self.session.query(objects_mapped.OfferMapped).filter(
            objects_mapped.OfferMapped.id == offer_id).all()[0]

        updated_offer.status = new_status
        self.session.commit()

        return True

    def update_offer_final_interest_sql(self, offer_id: int, final_interest):
        """
        This method can be used to update offer  final_interest in SQL table 'offers'.
        Offer ID and new offer status is expected
        """
        updated_offer = self.session.query(objects_mapped.OfferMapped).filter(
            objects_mapped.OfferMapped.id == offer_id).all()[0]

        updated_offer.final_interest = final_interest
        self.session.commit()

        return True

    def update_bid_status_sql(self, bid_id: int, new_status):
        """
        This method can be used to update bid status in SQL table 'bids'.
        Bid ID and new offer status is expected
        """

        updated_bid = self.session.query(objects_mapped.BidMapped).filter(
            objects_mapped.BidMapped.id == bid_id).all()[0]

        updated_bid.status = new_status
        self.session.commit()

        return True

    def cancel_remaining_bids_sql(self, offer_id, winning_bid_id):
        """
        This method can be used to cancel all bids on given offer except the one that was matched.
        The status of all bids on provided offer is changed to CANCELLED
        :param offer_id:
        :param winning_bid_id:
        """
        remaining_bids = self.session.query(objects_mapped.BidMapped).filter(
            objects_mapped.BidMapped.target_offer_id == offer_id).all()

        for bid in remaining_bids:

            if bid.id != winning_bid_id:
                self.update_bid_status_sql(bid.id, statuses.BidStatuses.CANCELLED.value)


if __name__ == '__main__':
    sqlr = SqlWriter()


    # # def __init__(self, offer_id: int, bid_id: int, offer_owner_id: int,
    # #              bid_owner_id: int, match_time: str, partial: int, final_interest: int, monthly_payment: Decimal = None,
    # #              sum: Decimal = None):
    #
    # from decimal import Decimal
    # ins_match = Match.Match(12, 13, 14, 15, "00:01", 1, Decimal(11), Decimal(12), Decimal(13))
    # ins_match.sum = Decimal(16)
    #
    # print(ins_match)
    #
    # sqlr.insert_match(ins_match)
