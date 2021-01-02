import pymysql
from datetime import datetime
import logging

from models.Offer import Offer
from models.SqlBasic import SqlBasic


class SqlWriter(SqlBasic):

    def __init__(self):
        super().__init__()
        self.create_validate_tables(self.cursor)

    def insert_offer(self, offer: Offer):

        query = f'insert into offers values({offer.id}, {offer.owner_id}, {offer.sum}, {offer.duration}, ' \
            f'{offer.offered_interest}, {offer.allow_partial_fill}, "{offer.date_added}", {offer.status})'

        return self.cursor.execute(query)





# if __name__=='__main__':
#     swriter = SqlWriter()
#
#     print(swriter.get_next_id('offers', swriter.cursor))
#
#     #query = 'insert into offers values(3, 11, 260, 12, 0.05, 0, "2020-1-15", 1)'
#     #swriter.cursor.execute(query)


