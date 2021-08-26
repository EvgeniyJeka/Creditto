from credittomodels import Match
from credittomodels import Offer
from credittomodels import Bid
from SqlBasic import SqlBasic
from credittomodels import statuses


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
            f'{offer.offered_interest}, {offer.final_interest}, {offer.allow_partial_fill}, "{offer.date_added}", {offer.status})'

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
            f'{match.bid_id}, {match.offer_owner_id}, {match.bid_owner_id}, "{match.match_time}",' \
            f' {match.partial}, {match.final_interest}, -1)'

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

    def update_bid_status_sql(self, bid_id: int, new_status):
        """
        This method can be used to update bid status in SQL table 'bids'.
        Bid ID and new offer status is expected
        """
        query = f'update bids set status = {new_status} where bids.id = {bid_id};'
        self.cursor.execute(query)
        return True

    def cancel_remaining_bids_sql(self, offer_id, winning_bid_id):
        """
        This method can be used to cancel all bids on given offer except the one that was matched.
        The status of all bids on provided offer is changed to CANCELLED
        :param offer_id:
        :param winning_bid_id:
        """
        query = f'select id from bids where target_offer_id = {offer_id};'
        self.cursor.execute(query)
        # Fetching data from SQL and putting it to list, excluding the matched bid
        all_bids_filtered = [x[0] for x in self.cursor.fetchall() if x[0] != winning_bid_id]

        for bid in all_bids_filtered:
            self.update_bid_status_sql(bid, statuses.BidStatuses.CANCELLED.value)


if __name__ == '__main__':
    sqlr = SqlWriter()
