from getup.response import ResponseOK
from getup.api.admin import Status
import bottle

def get():
	return ResponseOK(Status(bottle.app().config))
