

import pymysql
from datetime import datetime
import logging

from models.Offer import Offer
from models.SqlBasic import SqlBasic


class Reporter(SqlBasic):

    def __init__(self):
        super().__init__()
        self.create_validate_tables(self.cursor)

