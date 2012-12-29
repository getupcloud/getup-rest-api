# -*- coding: utf-8 -*-

import bottle
import httpagentparser as _hap

# 200
from httplib import OK
from httplib import CREATED
# 300
from httplib import MULTIPLE_CHOICES
# 400
from httplib import BAD_REQUEST
from httplib import UNAUTHORIZED
from httplib import FORBIDDEN
from httplib import NOT_FOUND
from httplib import METHOD_NOT_ALLOWED
# 500
from httplib import INTERNAL_SERVER_ERROR

HTTP_200 = HTTP_OK = OK
HTTP_201 = HTTP_CREATED = CREATED
HTTP_300 = HTTP_MULTIPLE_CHOICES = MULTIPLE_CHOICES
HTTP_400 = HTTP_BAD_REQUEST = BAD_REQUEST
HTTP_401 = HTTP_UNAUTHORIZED = UNAUTHORIZED
HTTP_403 = HTTP_FORBIDDEN = FORBIDDEN
HTTP_404 = HTTP_NOT_FOUND = NOT_FOUND
HTTP_405 = HTTP_METHOD_NOT_ALLOWED = METHOD_NOT_ALLOWED
HTTP_500 = HTTP_INTERNAL_SERVER_ERROR = INTERNAL_SERVER_ERROR

def is_browser(user_agent):
	if user_agent:
		ua = _hap.detect(user_agent)
		if ua:
			return ua.get('browser', {}).get('name', '')
	return ''
