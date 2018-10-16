#Isaac Alboucai
#Databases

from sqlalchemy import create_engine
#from sqlalchemy.ext.automap import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
import pymysql
from sqlalchemy import func
from sqlalchemy.sql import text
from sqlalchemy import and_
import datetime
    
Base = declarative_base()

class Sailors(Base):
	__tablename__ = 'sailors'
	sid = Column('sid',Integer,primary_key=True)
	sname = Column('sname',String)
	rating = Column('rating',Integer)
	age = Column('age',Integer)

class Boats(Base):
	__tablename__ = 'boats'
	bid = Column('bid',Integer,primary_key=True)
	bname = Column('bname',String)
	color = Column('color',String)
	length = Column('length',Integer)

class Reserves(Base):
	__tablename__ = 'reserves'
	sid = Column('sid',Integer,primary_key=True)
	bid = Column('bid',Integer,primary_key=True)
	day = Column('day',Date,primary_key=True)


pymysql.install_as_MySQLdb()

engine = create_engine('mysql://root:password@localhost/sailor_db')


Session = sessionmaker(bind=engine)
session = Session()

#session.query(func.count(Reserves)).filter()
def test_boats_res_num():
	test = []

	with engine.connect() as con:

		statement = text("""SELECT B.bid, COUNT(*) AS 'count'
					FROM boats B JOIN reserves R on B.bid = R.bid
					GROUP BY B.bname, B.bid
					ORDER BY b.bid""")
		ret = con.execute(statement)
		for row in ret:
			test += [(row.bid,row.count)]


	boats = session.query(Boats)
	boatfreq = []
	for boat in boats:
		freq = session.query(func.count(Reserves.bid).label('count')).filter(Reserves.bid == boat.bid).scalar()
		if freq > 0:
			boatfreq += [(boat.bid,freq)]
	assert boatfreq == test



def test_boat_w_maxres():
	boats = session.query(Boats)
	maxval = 0
	maxboats = []
	for boat in boats:
		val = session.query(func.count(Reserves.bid).label('count')).filter(Reserves.bid == boat.bid).scalar()
		if val > maxval:
			maxval = val
			maxboats = []
			maxboats += [boat.bid]
		elif val == maxval:
			maxboats += [boat.bid]
	assert maxboats[0] == 104


def test_avg_age_rating_10():
	assert session.query(func.avg(Sailors.age).label('average')).filter(Sailors.rating == 10).scalar() == 35


x = datetime.datetime(1998, 10, 10)

#PART 3
def daily_inven_control(date):
	boatsreserved = []
	sailorsreserved = []
	boatsavail = []
	sailorsavail = []
	reserves = session.query(Reserves).filter(Reserves.day == date)
	for res in reserves:
		boatsreserved += [(res.bid)]
		sailorsreserved += [(res.sid)]
	boats = session.query(Boats).filter(Boats.bid.notin_(boatsreserved)).all()
	sailors = session.query(Sailors).filter(Sailors.sid.notin_(sailorsreserved)).all()

	for boat in boats:
		boatsavail += [(boat.bid,boat.bname,boat.length)]
	for sailor in sailors:
		sailorsavail += [(sailor.sid,sailor.sname,sailor.rating)]

	return boatsavail,sailorsavail

b,s = daily_inven_control(x)
#print(b)
#print(s)


def wages_owed(startdate,enddate):
	sailors = session.query(Sailors)
	sailorpay = []
	for sailor in sailors:
		sailorwage = 15*sailor.rating
		numres = session.query(func.count(Reserves.bid)).filter(and_(Reserves.sid == sailor.sid,Reserves.day < startdate,Reserves.day > enddate)).scalar()
		sailorpay += [(sailor.sid,sailor.sname,sailorwage*numres)]
	return sailorpay


y = datetime.datetime(1988,11,10)
w =wages_owed(x,y)

print(w)

def cost_per_day(date):
	








