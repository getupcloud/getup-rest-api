# -*- coding: utf-8 -*-

import bottle
from bottle.ext import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

def make_url(config):
	query = { 'charset': config['encoding'] }
	if config['server'] == 'mysql':
		if 'socket' in config:
			config['hostname'] = 'localhost'
			query['unix_socket'] = config['socket']

	url_params = {
		  'drivername': config['server'],
		  'host': config.get('hostname', 'localhost'),
		  'username': config['username'],
		  'password': config['password'],
		  'database': config['basename'],
	}
	if 'port' in config:
		url_params['port'] = config['port']

	url = URL(query=query, **url_params)
	return url

def make_engine(config):
	return create_engine(make_url(config), **config.get('sqlalchemy', {}))
