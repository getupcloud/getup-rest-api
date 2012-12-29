# -*- coding: utf-8 -*-

import bottle
from getup import aaa, response, model

@aaa.authoritative_user
def get(user):
	return response.ResponseOK([ model.User(user) ])
