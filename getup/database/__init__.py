# -*- coding: utf-8 -*-

import bottle
from bottle.ext import sqlalchemy
from sqlalchemy import MetaData, Table
from engine import make_engine
#from getup import api

user_cols = [
		'id',
		'name',
		'email',
		'created_at',
		'admin',
		'blocked',
		'authentication_token',
	]

Users = Keys = None

def start(app):
	if 'engine' not in app.config.database:
		app.config.database['engine'] = make_engine(app.config.database)
		app.install(sqlalchemy.Plugin(app.config.database['engine'],
			create=False,
			commit=True,
			use_kwargs=False))
		global Users
		Users = table(bottle.app(), 'users')
		global Keys
		Keys = table(bottle.app(), 'keys')

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
