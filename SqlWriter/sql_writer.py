import pymysql
from datetime import datetime
import logging

from models import Match
from models.Offer import Offer
from models.Bid import Bid
from models.SqlBasic import SqlBasic


class SqlWriter(SqlBasic):

    def __init__(self):
        super().__init__()
        self.create_validate_tables(self.cursor)

    def insert_offer(self, offer: Offer):
        """
        This method can be used to insert new Offer to SQL table 'offers'.
        Offer object is expected
        """
        query = f'insert into offers values({offer.id}, {offer.owner_id}, {offer.sum}, {offer.duration}, ' \
            f'{offer.offered_interest}, {offer.allow_partial_fill}, "{offer.date_added}", {offer.status})'

        self.cursor.execute(query)
        return True

    def insert_bid(self, bid: Bid):
        """
        This method can be used to insert new Bid to SQL table 'bids'.
        Bid object is expected
        """
        query = f'insert into bids values({bid.id}, {bid.owner_id}, {bid.bid_interest}, {bid.target_offer_id}, ' \
            f'{bid.partial_only}, "{bid.date_added}", {bid.status})'

        self.cursor.execute(query)
        return True

    def insert_match(self, match: Match):
        """
        Inserting received Match object fields to SQL table 'matches'
        :param match: Match object
        :return:
        """
        new_match_id = self.get_next_id('matches')

        query = f'insert into matches values({new_match_id}, {match.offer_id}, ' \
            f'{match.bid_id}, {match.offer_owner_id}, {match.bid_owner_id}, "{match.match_time}", {match.partial}, -1)'

        self.cursor.execute(query)
        return True


    def update_offer_status_sql(self, offer_id: int, new_status):
        """
        This method can be used to update offer status in SQL table 'offers'.
        Offer ID and new offer status is expected
        """
        query = f'update offers set status = {new_status} where offers.id = {offer_id};'
        self.cursor.execute(query)
        return True

    # TBD
    def update_bid_status_sql(self, bid_id: int, new_status):
        # Bid status update
        pass

    def update_unmatched_bids_status_sql(self, offer_id: int, matched_bid: int):
        # Bid status update after match - unmatched bids
        pass





if __name__=='__main__':
    # a = [(1,2), (5,7), (9,4)]
    # a.sort(key=lambda x: x[1], reverse=True)
    # print(a)
    print(datetime.now())


