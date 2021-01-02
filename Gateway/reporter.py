

import pymysql
from datetime import datetime
import logging

from models.Offer import Offer
from models.SqlBasic import SqlBasic


class Reporter(SqlBasic):

    def __init__(self):
        super().__init__()
        self.create_validate_tables(self.cursor)

    def get_next_id(self, table_name):
        """
        This method can be used to get the next valid number that can be used as ID for new record in given table
        :param table_name: existing table, str
        :param cursor: sql cursor
        :return: int
        """
        try:
            query = f"select id from {table_name} order by id desc;"
            result = self.cursor.execute(query)
            return result + 1

        except pymysql.err.ProgrammingError as e:
            logging.error(f"SqlWriter: Table {table_name} doesn't exsits: {e}")