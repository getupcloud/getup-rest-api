# -*- coding: utf-8 -*-

from bottle import request
from getup import response
import broker, user

def get():
	return response.ResponseOK()

head = get
