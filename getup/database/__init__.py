# -*- coding: utf-8 -*-

import bottle
#from bottle.ext import sqlalchemy
from sqlalchemy import text, MetaData, Table, Column, Integer, String, TIMESTAMP, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from engine import make_engine
import sqlalchemy.ext

Base = declarative_base()

class AccountingTable(Base):
	__tablename__ = 'accounting'
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer)
	time = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
	name = Column(String(32), default='event')
	value = Column(String(1024), default='')

class UsersTable(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	email = Column(String, nullable=False)
	encrypted_password = Column(String, nullable=False)
	name = Column(String, nullable=False)
	admin = Column(BOOLEAN, nullable=False)
	authentication_token = Column(String, nullable=False)
	blocked = Column(BOOLEAN, nullable=False)
	username = Column(String, nullable=False)

class KeysTable(Base):
	__tablename__ = 'keys'
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer)
	key = Column(String)
	title = Column(String)
	identifier = Column(String)

Accounting = Users = Keys = None

def _create_table(engine, *tables):
	for table in tables:
		if not engine.has_table(table.__tablename__):
			table.metadata.create_all(engine)

def start(app):
	if 'engine' not in app.config.database:
		app.config.database['engine'] = make_engine(app.config.database)

	# create accounting table
	engine = app.config.database['engine']

	_create_table(engine, AccountingTable)

	# create gitlab tables if using sqlite. this means we are testing.
	if engine.url.drivername == 'sqlite':
		_create_table(engine, UsersTable, KeysTable)

	# instanciate ORM
	global Accounting
	global Users, Keys ## tables from gitlab
	Users = table(bottle.app(), UsersTable.__tablename__)
	Users, Keys, Accounting = [ table(bottle.app(), t.__tablename__) for t in [ UsersTable, KeysTable, AccountingTable ] ]

def table(app, name):
	engine = app.config.database['engine']
	meta = MetaData(bind=engine)
	table = Table(name, meta, autoload=True, autoload_with=engine)
	return table #, meta

def _make_query(table, **where):
	query = table.select()
	for k, v in filter(lambda (x, y): x and y, where.iteritems()):
		clause = (getattr(table.c, k) == v)
		query = query.where(clause)
	return query

def user(**where):
	assert where, 'missing where clauses'
	query = _make_query(Users, **where)
	try:
		return query.execute().fetchone()
	except sqlalchemy.exc.ProgrammingError:
		return None

def keys(user, **where):
	query = _make_query(Keys, user_id=user['id'], **where)
	try:
		return query.execute()
	except sqlalchemy.exc.ProgrammingError:
		return None

def accounting(user, event_name, event_value):
	Accounting.insert().values(user_id=user['id'], name=event_name, value=event_value).execute()
