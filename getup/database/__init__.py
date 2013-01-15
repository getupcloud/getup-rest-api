# -*- coding: utf-8 -*-

import bottle
from bottle.ext import sqlalchemy
from sqlalchemy import text, MetaData, Table, Column, Integer, String, TIMESTAMP
from engine import make_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AccountTable(Base):
	__tablename__ = 'accounting'
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer)
	time = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
	name = Column(String(32), default='event')
	value = Column(String(1024), default='')

user_cols = [
		'id',
		'name',
		'email',
		'created_at',
		'admin',
		'blocked',
		'authentication_token',
	]

Accounting = Users = Keys = None

def start(app):
	if 'engine' not in app.config.database:
		app.config.database['engine'] = make_engine(app.config.database)
		app.install(sqlalchemy.Plugin(app.config.database['engine'],
			create=False,
			commit=True,
			use_kwargs=False))

		# create accounting table
		engine = app.config.database['engine']
		if not engine.has_table(AccountTable.__tablename__):
			AccountTable.metadata.create_all(engine)

		# instanciate ORM
		global Users, Keys, Accounting
		## tables from gitlab
		Users = table(bottle.app(), 'users')
		Keys = table(bottle.app(), 'keys')
		## our accounting table
		Accounting = table(bottle.app(), AccountTable.__tablename__)

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
	return query.execute().fetchone()

def keys(user, **where):
	query = _make_query(Keys, user_id=user['id'], **where)
	return query.execute()

def accounting(user, event_name, event_value):
	Accounting.insert().values(user_id=user['id'], name=event_name, value=event_value).execute()

if __name__ == '__main__':
	import getup.config
	getup.config.loadconfig(bottle.app())
	#start(app)
	#u = user('bcqvzVxP8yokasKHfP5w')
#else:
	#start(bottle.app())
	# tables
	#Users = table(bottle.app(), 'users')
	#Keys = table(bottle.app(), 'keys')
