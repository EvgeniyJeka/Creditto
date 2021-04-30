import pymysql
from datetime import datetime
import logging



class SqlBasic(object):
    #hst = '127.0.0.1'
    hst = 'kafka_2_cabin_db_1'
    usr = 'root'
    pwd = '123456'
    db_name = 'creditto'
    cursor = None

    def __init__(self):
        self.cursor = self.connect_me(self.hst, self.usr, self.pwd, self.db_name)
        self.create_validate_tables(self.cursor)

    # Connect to DB
    def connect_me(self, hst, usr, pwd, db_name):
        """
        This method can be used to connect to MYSQL DB.
        :param hst: SQL Host
        :param usr: Username
        :param pwd: Password
        :param db_name: DB Name
        :return: SQL cursor
        """
        try:
            conn = pymysql.connect(host=hst, user=usr, password=pwd, db=db_name, autocommit='True')
            cursor = conn.cursor()
            return cursor

        # Wrong Credentials error
        except pymysql.err.OperationalError as e:
            print("Wrong Credentials or Host")
            print(e)

        # Wrong DB name error
        except pymysql.err.InternalError:
            print("Unknown Database")

    # Validates that all the required tables exist, if they aren't - the method creates them.
    def create_validate_tables(self, cursor):
        """
        This method can be used to validate, that all needed table are exist.
        If they aren't the method will create them
        :param cursor: sql cursor
        """
        cursor.execute('show tables')
        tups = cursor.fetchall()

        tables = [tup[0] for tup in tups]

        # Creating the 'offers' table if not exists - column for each "Offer" object property.
        if 'offers' not in tables:
            logging.warning("Logs: 'offers' table is missing! Creating the 'offers' table")
            query = "CREATE TABLE offers (id int, owner_id int, sum varchar(255), " \
                    "duration int, offered_interest varchar(255), allow_partial_fill int, date_added varchar(255), " \
                    "status int);"

            cursor.execute(query)

        # Creating the 'bids' table if not exists - column for each "Bid" object property.
        if 'bids' not in tables:
            logging.warning("Logs: 'bids' table is missing! Creating the 'bids' table")
            query = "CREATE TABLE bids (id int, owner_id int, bid_interest varchar(255), target_offer_id int, " \
                    "partial_only int, date_added varchar(255), status int);"

            cursor.execute(query)


