import pymysql
import logging
from sqlalchemy import exc, PrimaryKeyConstraint
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from local_config import SqlConfig
import sqlalchemy as db


class SqlBasic(object):
    hst = SqlConfig.SQL_HOST.value
    usr = SqlConfig.SQL_USER.value
    pwd = SqlConfig.SQL_PASSWORD.value
    db_name = SqlConfig.DB_NAME.value
    cursor = None

    def __init__(self):
        self.cursor, self.engine = self.connect_me(self.hst, self.usr, self.pwd, self.db_name)
        self.create_validate_tables()


    # Connect to DB
    def connect_me(self, hst, usr, pwd, db_name):
        """
        This method is used to establish a connection to MySQL DB.
        Credentials , host and DB name are taken from "config.ini" file.

        :param hst: host
        :param usr: user
        :param pwd: password
        :param db_name: DB name
        :return: SqlAlchemy connection (cursor)
        """
        import sqlalchemy
        try:

            url = f'mysql+pymysql://{usr}:{pwd}@{hst}:3306/{db_name}'

            # Create an engine object.
            engine = create_engine(url, echo=True)

            # Create database if it does not exist.
            if not database_exists(engine.url):
                create_database(engine.url)
                cursor = engine.connect()
                return cursor, engine
            else:
                # Connect the database if exists.
                cursor = engine.connect()
                return cursor, engine

        # Wrong Credentials error
        except sqlalchemy.exc.OperationalError as e:
            logging.critical("SQL DB -  Can't connect, verify credentials and host, verify the server is available")
            logging.critical(e)

        # General error
        except Exception as e:
            logging.critical("SQL DB - Failed to connect, reason is unclear")
            logging.critical(e)

    def create_table_from_scratch(self, table_name, column_names, primary_key):
        """
        This method can be used to create a new SQL table from scratch.
        :param file_name: Table name, str
        :param column_names: Table columns list
        :param table_data: table data, list - each element will become a record in the table
        :return: dict (confirmation message or error message)
        """

        logging.info(f"SQL Module: Creating a new table from scratch -  '{table_name}'")
        tables = self.engine.table_names()

        # Creating new table to store the file content if not exist.
        if table_name not in tables:
            logging.info(f"{table_name} table is missing! Creating the {table_name} table")
            metadata = db.MetaData()

            # Creating table - column names are provided in a tuple
            columns_list = [db.Column(x[0], x[1]) for x in column_names]

            # SQL Alchemy table instance is passed to the "fill_table" method
            db.Table(table_name, metadata, *columns_list, PrimaryKeyConstraint(primary_key), extend_existing=True)
            metadata.create_all(self.engine)

            logging.info(f"SQL Module: Table {table_name} was created")
            return {"SQL Module": f"Table {table_name} was created"}

        else:
            return {"error": f"Can't create a new table - table with name {table_name} already exists"}

    def create_validate_tables(self):
        """
        This method can be used to validate, that all needed table are exist.
        If they aren't the method will create them
        :param engine: Sql Alchemy engine
        """
        tables = self.engine.table_names()

        # Creating the 'offers' table if not exists - column for each "Offer" object property.
        if 'offers' not in tables:
            logging.warning("Logs: 'offers' table is missing! Creating the 'offers' table")

            column_names = (('id', db.BIGINT), ('owner_id', db.INT), ('sum', db.String(255)),
                            ('duration', db.INT), ('offered_interest', db.String(255)),
                            ('final_interest', db.String(255)), ('allow_partial_fill', db.INT),
                            ('date_added', db.String(255)), ('status', db.INT))

            self.create_table_from_scratch('offers', column_names, 'id')

        # Creating the 'bids' table if not exists - column for each "Bid" object property.
        if 'bids' not in tables:
            logging.warning("Logs: 'bids' table is missing! Creating the 'bids' table")

            column_names = (('id', db.BIGINT), ('owner_id', db.INT), ('bid_interest', db.String(255)),
                            ('target_offer_id', db.BIGINT), ('partial_only', db.INT),
                            ('date_added', db.String(255)), ('status', db.INT))

            self.create_table_from_scratch('bids', column_names, 'id')

        # Creating the 'offers' table if not exists - column for each "Offer" object property.
        if 'matches' not in tables:
            logging.warning("Logs: 'matches' table is missing! Creating the 'bids' table")

            column_names = (('id', db.BIGINT), ('offer_id', db.BIGINT), ('bid_id', db.BIGINT),
                            ('offer_owner_id', db.INT), ('bid_owner_id', db.INT),
                            ('match_time', db.String(255)), ('partial', db.INT),
                            ('sum', db.String(255)), ('final_interest', db.String(255)),
                            ('monthly_payment', db.String(255)))

            self.create_table_from_scratch('matches', column_names, 'id')

        #         query = "CREATE TABLE matches (id bigint, offer_id bigint, bid_id bigint, offer_owner_id int, bid_owner_id int, " \
        #                 "match_time varchar(255), partial int, sum varchar(255), final_interest varchar(255), " \
        #                 "monthly_payment varchar(255)," \
        #                 " PRIMARY KEY (ID));"






    # # Validates that all the required tables exist, if they aren't - the method creates them.
    # def create_validate_tables(self, cursor):
    #     """
    #     This method can be used to validate, that all needed table are exist.
    #     If they aren't the method will create them
    #     :param cursor: sql cursor
    #     """
    #     cursor.execute('show tables')
    #     tups = cursor.fetchall()
    #
    #     tables = [tup[0] for tup in tups]
    #
    #     # Creating the 'offers' table if not exists - column for each "Offer" object property.
    #     if 'offers' not in tables:
    #         logging.warning("Logs: 'offers' table is missing! Creating the 'offers' table")
    #         query = "CREATE TABLE offers (id bigint, owner_id int, sum varchar(255), " \
    #                 "duration int, offered_interest varchar(255), final_interest varchar(255), allow_partial_fill int, date_added varchar(255), " \
    #                 "status int, PRIMARY KEY (ID));"
    #
    #         cursor.execute(query)
    #
    #     # Creating the 'bids' table if not exists - column for each "Bid" object property.
    #     if 'bids' not in tables:
    #         logging.warning("Logs: 'bids' table is missing! Creating the 'bids' table")
    #         query = "CREATE TABLE bids (id bigint, owner_id int, bid_interest varchar(255), target_offer_id bigint, " \
    #                 "partial_only int, date_added varchar(255), status int, PRIMARY KEY (ID));"
    #
    #         cursor.execute(query)
    #
    #     if 'matches' not in tables:
    #         logging.warning("Logs: 'matches' table is missing! Creating the 'bids' table")
    #         query = "CREATE TABLE matches (id bigint, offer_id bigint, bid_id bigint, offer_owner_id int, bid_owner_id int, " \
    #                 "match_time varchar(255), partial int, sum varchar(255), final_interest varchar(255), " \
    #                 "monthly_payment varchar(255)," \
    #                 " PRIMARY KEY (ID));"
    #
    #         cursor.execute(query)
    #
    #     if 'local_config' not in tables:
    #         logging.warning("Logs: 'local_config' table is missing! Creating the 'local_config' table")
    #         query = "CREATE TABLE local_config (id bigint, property varchar(255), " \
    #                 "value  varchar(255), description varchar(255), PRIMARY KEY (ID));"
    #
    #         cursor.execute(query)
    #         logging.warning("Logs: ADDING THE DEFAULT CONFIG")
    #
    #         query = f'insert into local_config values(1, "matching_logic", 1, "selected matching algorithm")'
    #         cursor.execute(query)
    #         query = f'insert into local_config values(2, "tail_digits", 4, "max tail digits allowed, rounding config")'
    #         cursor.execute(query)
    #         logging.warning("Logs: SETTING THE DEFAULT CONFIG")

if __name__ == '__main__':
    print("Test")
    sql_basic = SqlBasic()