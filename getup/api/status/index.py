# -*- coding: utf-8 -*-

import bottle
from getup import aaa, model
#from getup.response import response

def get():
	return model.Status(bottle.app().config)
