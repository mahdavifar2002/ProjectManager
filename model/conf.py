import os
import uuid
from datetime import datetime
import jdatetime

from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Boolean
from sqlalchemy import and_, or_, desc
from sqlalchemy import func
from sqlalchemy import select

db_name = "project_manager"
db_user_name = "alireza"
db_user_pass = "96321"
db_url = "alireza"
db_port = "3306"

# Communicates directly to SQL
engine = create_engine("mysql://{0}:{1}@{2}:{3}/{4}".format(db_user_name, db_user_pass, db_url, db_port, db_name),
                       isolation_level="READ UNCOMMITTED")
# engine = create_engine('mysql://root:root@127.0.0.1:3306', convert_unicode=True)
# Maps classes to database tables
Base = declarative_base()

# establishes all conversations with the database
# and represents a "staging zone" for all the objects
# loaded into the database session object.

db_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# db_session = scoped_session(db_session)

# Any change made against the objects in the
# session won't be persisted into the database
# until you call session.commit(). If you're not
# happy about the changes, you can revert all of
# them back to the last commit by calling session.rollback()
session = db_session()


def create_db():
    global engine

    engine = create_engine("mysql://{0}:{1}@{2}:{3}".format(db_user_name, db_user_pass, db_url, db_port),
                           isolation_level="READ UNCOMMITTED")

    # Creates database only if it does not exist
    with engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS {0}".format(db_name)))
        conn.execute(text("USE {0}".format(db_name)))

    engine = create_engine("mysql://{0}:{1}@{2}:{3}/{4}".format(db_user_name, db_user_pass, db_url, db_port, db_name),
                           isolation_level="READ UNCOMMITTED")


def init_db():
    # Create the DB in MySQL before initializing it
    create_db()

    # Creates all the tables in the database
    # Will skip already created tables
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine

    print("---Initialized DB!---")


def drop_db():
    # Drops database only if it exists
    with engine.connect() as conn:
        conn.execute(text("DROP DATABASE IF EXISTS {0}".format(db_name)))

    print("---Dropped DB!---")


def save_to_db(record):
    try:
        session.add(record)
        session.commit()
    except Exception as e:
        print(e)


def db_time():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT NOW();"))

    for row in result:
        return row[0]


def time_diff_in_second(t1: datetime, t2: datetime):
    return t1.timestamp() - t2.timestamp()


def delta_human_readable(delta: relativedelta):
    attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
    return ['%d %s' % (getattr(delta, attr), attr if getattr(delta, attr) > 1 else attr[:-1])
            for attr in attrs if getattr(delta, attr)][0]


def date_human_readable(date: datetime):
    now = db_time()
    return delta_human_readable(relativedelta(now, date))

def generate_filename(username: str, exention: str):
    now = jdatetime.datetime.fromgregorian(datetime=datetime.now()).strftime("%Y-%m-%d_%H-%M-%S")
    uuid4 = str(uuid.uuid4())[:4]

    filename = now + "_" + username + "_" + uuid4 + "." + exention
    return filename