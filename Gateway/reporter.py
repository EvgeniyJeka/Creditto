
import pymysql
from datetime import datetime
import logging

from .Offer import Offer
from.SqlBasic import SqlBasic


class Reporter(SqlBasic):

    def __init__(self):
        super().__init__()
        self.create_validate_tables(self.cursor)

