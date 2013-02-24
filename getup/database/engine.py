# -*- coding: utf-8 -*-

from sqlalchemy import create_engine

def make_engine(config):
	url = config.pop('url')
	return create_engine(url, **config.parameters)
