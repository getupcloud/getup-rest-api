# -*- coding: utf-8 -*-

from bottle import request
from getup import response

def get():
	return response.ResponseOK()

head = get
