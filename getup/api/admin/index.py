# -*- coding: utf-8 -*-

from bottle import request
from getup.response import ResponseOK

def get():
	return ResponseOK()

head = get
