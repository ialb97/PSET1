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
	cost = Column('cost',Integer)
	price = Column('price',Integer)

class Reserves(Base):
	__tablename__ = 'reserves'
	sid = Column('sid',Integer,primary_key=True)
	bid = Column('bid',Integer,primary_key=True)
	day = Column('day',Date,primary_key=True)
	daytime = Column('daytime',String,primary_key=True)


pymysql.install_as_MySQLdb()

engine = create_engine('mysql://root:password@localhost/sailor_db3')


Session = sessionmaker(bind=engine)
session = Session()


def daily_inven_control(date):
	boatsreserved = []
	sailorsreserved = []
	boatsavailday = []
	sailorsavailday = []
	boatsavailnoon = []
	sailorsavailnoon = []
	reservesmorn = session.query(Reserves).filter(and_(Reserves.day == date,Reserves.daytime == 'morning'))
	reservesnoon = session.query(Reserves).filter(and_(Reserves.day == date,Reserves.daytime == 'afternoon'))
	for res in reservesmorn:
		boatsreserved += [(res.bid)]
		sailorsreserved += [(res.sid)]
	boatsmorn = session.query(Boats).filter(Boats.bid.notin_(boatsreserved)).all()
	sailorsmorn = session.query(Sailors).filter(Sailors.sid.notin_(sailorsreserved)).all()


	boatsreserved = []
	sailorsreserved = []
	for res in reservesnoon:
		boatsreserved += [(res.bid)]
		sailorsreserved += [(res.sid)]
	boatsnoon = session.query(Boats).filter(Boats.bid.notin_(boatsreserved)).all()
	sailorsnoon = session.query(Sailors).filter(Sailors.sid.notin_(sailorsreserved)).all()

	for boat in boatsmorn:
		boatsavailday += [(boat.bid,boat.bname,boat.length)]
	for boat in boatsnoon:
		boatsavailnoon += [(boat.bid,boat.bname,boat.length)]
	for sailor in sailorsmorn:
		sailorsavailday += [(sailor.sid,sailor.sname,sailor.rating)]
	for sailor in sailorsnoon:
		sailorsavailnoon += [(sailor.sid,sailor.sname,sailor.rating)]

	return boatsavailday,boatsavailnoon,sailorsavailday,sailorsavailnoon
x = datetime.datetime(1998, 10, 10)
bd,bn,sd,sn = daily_inven_control(x)
print(bd)
print(bn)
print(sd)
print(sn)

def wages_owed(startdate,enddate):
	sailors = session.query(Sailors)
	sailorpay = []
	for sailor in sailors:
		sailorwage = 15*sailor.rating
		numres = session.query(func.count(Reserves.bid)).filter(and_(Reserves.sid == sailor.sid,Reserves.day < startdate,Reserves.day > enddate)).scalar()
		sailorpay += [(sailor.sid,sailor.sname,sailorwage*numres)]
	return sailorpay


def company_cost(startdate,enddate):
	total = 0
	sailors = session.query(Sailors)
	boats = session.query(Boats)
	for sailor in sailors:
		sailorwage = 15*sailor.rating
		numres = session.query(func.count(Reserves.bid)).filter(and_(Reserves.sid == sailor.sid,Reserves.day < startdate,Reserves.day > enddate)).scalar()
		total += numres*sailorwage
	for boat in boats:
		boatcost = boat.cost
		numres = session.query(func.count(Reserves.bid)).filter(and_(Reserves.sid == sailor.sid,Reserves.day < startdate,Reserves.day > enddate)).scalar()
		total += numres*boatcost
	return total

y = datetime.datetime(1988,11,10)
w =wages_owed(x,y)
t = company_cost(x,y)

print(w)
print(t)

def Revenue(startdate,enddate):
	total = 0
	boats = session.query(Boats)
	for boat in boats:
		boatprice = boat.price
		numres = session.query(func.count(Reserves.bid)).filter(and_(Reserves.bid == boat.bid,Reserves.day < startdate,Reserves.day > enddate)).scalar()
		total += boatprice*numres
	return total

r = Revenue(x,y)
print(r)







