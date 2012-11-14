# -*- coding: utf-8 -*-

from http import *
from app import App

class Response(dict):
	def __init__(self, data=None, code=HTTP_OK, message='OK'):
		self['status'] = dict(code=code, message=message)
		if isinstance(data, App):
			self['data'] = data._asdict()
		elif data is not None:
			self['data'] = data
