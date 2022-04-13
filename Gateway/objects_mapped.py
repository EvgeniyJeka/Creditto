
import sqlalchemy as db
from sqlalchemy import create_engine, or_, and_
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class OfferMapped(Base):
    __tablename__ = 'offers'

    id = Column('id', db.BIGINT, primary_key=True)
    owner_id = Column('owner_id', db.INT)
    sum = Column('sum', db.String(255))

    duration = Column('duration', db.INT)
    offered_interest = Column('offered_interest', db.String(255))
    final_interest = Column('final_interest', db.String(255))

    allow_partial_fill = Column('allow_partial_fill', db.INT)
    date_added = Column('date_added', db.String(255))
    status = Column('status', db.INT)


class BidMapped(Base):
    __tablename__ = 'bids'

    id = Column('id', db.BIGINT, primary_key=True)
    owner_id = Column('owner_id', db.INT)
    bid_interest = Column('bid_interest', db.String(255))

    target_offer_id = Column('target_offer_id', db.BIGINT)
    partial_only = Column('partial_only', db.INT)
    date_added = Column('date_added', db.String(255))

    status = Column('status', db.INT)



class MatchesMapped(Base):
    __tablename__ = 'matches'

    id = Column('id', db.BIGINT, primary_key=True)
    offer_id = Column('offer_id', db.BIGINT)
    bid_id = Column('bid_id', db.BIGINT)

    offer_owner_id = Column('offer_owner_id', db.INT)
    bid_owner_id = Column('bid_owner_id', db.INT)
    match_time = Column('match_time', db.String(255))

    partial = Column('partial', db.INT)
    sum = Column('sum', db.String(255))
    final_interest = Column('final_interest', db.String(255))

    monthly_payment = Column('monthly_payment', db.String(255))



class LocalConfigMapped(Base):
    __tablename__  = 'local_config'

    id = Column('id', db.BIGINT, primary_key=True)
    property = Column('property', db.String(255))
    value = Column('value', db.String(255))

    description = Column('description', db.String(255))


