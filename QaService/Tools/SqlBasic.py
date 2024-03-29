import logging
from sqlalchemy import exc, or_, and_
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
import sqlalchemy as db
from credittomodels import objects_mapped
import sqlalchemy

try:
    from Config import base_config
except ModuleNotFoundError:
    from ..Config import base_config


class SqlBasic(object):

    hst = base_config.BaseConfig.SQL_HOST
    usr = base_config.BaseConfig.SQL_USER
    pwd = base_config.BaseConfig.SQL_PASSWORD
    db_name = base_config.BaseConfig.SQL_DB_NAME
    system_warmup_delay = base_config.BaseConfig.MYSQL_DB_WARMUP_DELAY
    cursor = None

    def __init__(self):
        self.cursor, self.engine = self.connect_me(self.hst, self.usr, self.pwd, self.db_name)

        # Initiating a session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
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

        try:

            url = f'mysql+pymysql://{usr}:{pwd}@{hst}:3306/{db_name}'

            # Create an engine object.
            engine = create_engine(url, echo=False, isolation_level="READ UNCOMMITTED")

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


    def create_validate_tables(self):
        """
        This method can be used to validate, that all needed table are exist.
        If they aren't the method will create them
        :param engine: Sql Alchemy engine
        """
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        tables = metadata.tables.keys()

        # Creating the 'offers' table if not exists - column for each "Offer" object property.
        if 'offers' not in tables:
            logging.warning("Logs: 'offers' table is missing! Creating the 'offers' table")
            self.offers_table = objects_mapped.OfferMapped()
            objects_mapped.Base.metadata.create_all(self.engine)

        # Creating the 'bids' table if not exists - column for each "Bid" object property.
        if 'bids' not in tables:
            logging.warning("Logs: 'bids' table is missing! Creating the 'bids' table")
            self.bids_table = objects_mapped.BidMapped()
            objects_mapped.Base.metadata.create_all(self.engine)

        # Creating the 'offers' table if not exists - column for each "Match" object property.
        if 'matches' not in tables:
            logging.warning("Logs: 'matches' table is missing! Creating the 'matches' table")
            self.matches_table = objects_mapped.MatchesMapped()

        # Creating the 'local_config' table if not exists
        if 'local_config' not in tables:
            logging.warning("Logs: 'local_config' table is missing! Creating the 'local_config' table")
            self.local_config_table = objects_mapped.LocalConfigMapped()
            objects_mapped.Base.metadata.create_all(self.engine)

            # Inserting a record
            configuration = [objects_mapped.LocalConfigMapped(id=1, property="matching_logic",
                                               value=1, description="selected matching algorithm"),
                             objects_mapped.LocalConfigMapped(id=2, property="tail_digits",
                                               value=4, description="max tail digits allowed, rounding config")]

            self.session.add_all(configuration)
            self.session.commit()


    def get_columns(self, table):
        """
        Returns a list of column names
        @param table: existing table, str
        @return: list of str
        """
        try:
            metadata = db.MetaData()
            table_ = db.Table(table, metadata,  autoload_replace=True, autoload_with=self.engine)

            return table_.columns.keys()

        except Exception as e:
            logging.error(f" Failed to fetch column names of table {table} - {e}")
            return False


    def get_table_content(self, table):
        """
        Get table content from DB
        :param table: table name, String
        :return: tuple
        """

        metadata = db.MetaData()
        table_ = db.Table(table, metadata,  autoload_replace=True, autoload_with=self.engine)

        query = db.select(table_)
        ResultProxy = self.cursor.execute(query)
        result = ResultProxy.fetchall()

        return result

    def get_offer_data_alchemy(self, offer_id: int):
        """
        This method can be used to extract data on a selected offer from SQL DB
        :param offer_id: int
        :return: dict
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("offers", metadata,  autoload_replace=True, autoload_with=self.engine)

            query = db.select(table_).where(table_.columns.id == offer_id)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return self.pack_to_dict(result, "offers")

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def get_offer_by_status_internal(self, offer_status: int):
        """
        Returns offer status from SQL DB by offer ID, internal usage only
        :param offer_status: int
        :return: tuple
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("offers", metadata,  autoload_replace=True, autoload_with=self.engine)

            query = db.select(table_).where(table_.columns.status == offer_status)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return result

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def get_bids_by_offer_alchemy(self, offer_id: int):
        """
        Returns bids by offer ID - all bids are placed on given offer
        :param offer_id: int
        :return: dict
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("bids", metadata,  autoload_replace=True, autoload_with=self.engine)

            query = db.select(table_).where(table_.columns.target_offer_id == offer_id)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return self.pack_to_dict(result, "bids")

        except Exception as e:
            logging.error(f"SQL Module: Failed to get bids data from SQL - {e}")

    def get_bid_data_alchemy(self, bid_id: int):
        """
        Returns data on the selected bid
        :param bid_id: int
        :return: dict
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("bids", metadata,  autoload_replace=True, autoload_with=self.engine)

            query = db.select(table_).where(table_.columns.id == bid_id)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return self.pack_to_dict(result, "bids")

        except Exception as e:
            logging.error(f"SQL Module: Failed to get bids data from SQL - {e}")

    def get_offers_by_status_alchemy(self, status: int):
        """
         Fetches offers from SQL DB by provided status.
         Returns a list of dicts - each dict contains data on one offer.
         Returns an empty list if there are no offers in SQL DB with requested status.
         Special case: status '-1' is received - all offers are returned in that case.
        :param status: int
        :return: list of dicts
        """
        if status == -1:
            data = self.get_table_content("offers")
        else:
            data = self.get_offer_by_status_internal(status)

        return self.pack_to_dict(data, "offers")

    def get_bids_by_lender_alchemy(self, lender_id: int):
        """
        Returns all bids placed by the provided lender
        :param lender_id: int
        :return: dict
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("bids", metadata, autoload_replace=True, autoload_with=self.engine)

            query = db.select(table_).where(table_.columns.owner_id == lender_id)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return self.pack_to_dict(result, "bids")

        except Exception as e:
            logging.error(f"SQL Module: Failed to get bids data from SQL - {e}")

    def get_offers_by_borrower_alchemy(self, borrower_id: int):
        """
        Returns all offers placed by the given borrower
        :param borrower_id:
        :return:
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("offers", metadata,  autoload_replace=True, autoload_with=self.engine)

            query = db.select(table_).where(table_.columns.owner_id == borrower_id)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return self.pack_to_dict(result, "offers")

        except Exception as e:
            logging.error(f"SQL Module: Failed to get  data from SQL - {e}")

    def get_matches_by_owner_alchemy(self, owner_id: int):
        """
        Returns matches by owner ID - the owner can be lender OR borrower
        :param owner_id: int
        :return: dict
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("matches", metadata,  autoload_replace=True, autoload_with=self.engine)

            query = db.select(table_).where(or_(table_.columns.offer_owner_id == owner_id, table_.columns.bid_owner_id == owner_id))
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return self.pack_to_dict(result, "matches")

        except Exception as e:
            logging.error(f"SQL Module: Failed to get  data from SQL - {e}")

    def get_match_by_offer_id_alchemy(self, offer_id: int):
        try:

            metadata = db.MetaData()
            table_ = db.Table("matches", metadata,  autoload_replace=True, autoload_with=self.engine)

            query = db.select(table_).where(table_.columns.offer_id == offer_id)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return self.pack_to_dict(result, "matches")

        except Exception as e:
            logging.error(f"SQL Module: Failed to get  data from SQL - {e}")

    def get_relevant_offers(self):
        """
        Returns all offers in status OPEN and PARTIALLY_MATCHED from SQL DB
        :return: list of tuples
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("offers", metadata,  autoload_replace=True, autoload_with=self.engine)

            query = db.select(table_).where(
                or_(table_.columns.status == 1, table_.columns.status == 3))
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return result

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def get_relevant_bids(self, target_offer_id):
        """
        Returns all bids in status OPEN placed on given offer
        :param target_offer_id: int
        :return: list of tuples
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("bids", metadata, autoload_replace=True, autoload_with=self.engine)

            query = db.select(table_).where(
                and_(table_.columns.status == 1, table_.columns.target_offer_id == target_offer_id))
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return result

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def fetch_config_from_db(self, config_param):
        """
        This method can be used to fetch local config params from SQL DB table 'local_config'
        :param config_param: requested config property, string
        :return: current config (value), string
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("local_config", metadata,  autoload_replace=True, autoload_with=self.engine)

            query = db.select(table_).where(table_.columns.property == config_param)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return int(self.pack_to_dict(result, "local_config")[0]['value'])

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def get_next_id(self, table_name):
        """
        This method can be used to get the next valid number that can be used as ID for new record in given table
        :param table_name: existing table, str
        :param cursor: sql cursor
        :return: int
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table(table_name, metadata,  autoload_replace=True, autoload_with=self.engine)

            query = db.select(table_)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            result.sort(key=lambda x: x[0], reverse=True)

            return result[0][0] + 1

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def get_users_by_role(self, role_id: int):
        """
        Returns all users in given role
        :param role_id: int
        :return: list of tuples
        """
        try:

            metadata = db.MetaData()
            table_ = db.Table("users", metadata,  autoload_replace=True, autoload_with=self.engine)

            query = db.select(table_).where(table_.columns.role_id == role_id)
            ResultProxy = self.cursor.execute(query)
            result = ResultProxy.fetchall()

            return result

        except Exception as e:
            logging.error(f"SQL Module: Failed to get offer data from SQL - {e}")

    def pack_to_dict(self, data, table):
        """
        This method can be used to extract data from SQL table and pack it to list of dicts
        @param query: query to execute
        @param table: SQL table
        @return: list of dicts
        """
        try:
            columns = self.get_columns(table)

            if data is None:
                logging.warning(f"Couldn't find the requested data by provided param")
                return []

            elif len(data) == 1:
                cnt = 0
                result = {}
                for column in columns:
                    result[column] = data[0][cnt]
                    cnt += 1
                return [result]

            result = []
            for contact in data:
                cnt = 0
                record = {}
                for column in columns:
                    record[column] = contact[cnt]
                    cnt += 1
                result.append(record)
            return result

        except Exception as e:
            logging.error(f"Failed to pack data from SQL, {e}")
            raise e

    def set_config_in_db(self, id, new_config):

        updated_config = self.session.query(objects_mapped.LocalConfigMapped).filter(
            objects_mapped.LocalConfigMapped.id == id)[0]

        updated_config.value = new_config
        self.session.commit()

    def get_bids_by_offer(self, offer_id):
        return self.get_bids_by_offer_alchemy(offer_id)


# if __name__ == '__main__':
#     sq_mn = SqlBasic()
#     print(sq_mn.get_users_by_role(2))