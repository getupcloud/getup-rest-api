# -*- coding: utf-8 -*-

from httplib import OK
from httplib import METHOD_NOT_ALLOWED

HTTP_200 = HTTP_OK = OK
HTTP_405 = HTTP_METHOD_NOT_ALLOWED = METHOD_NOT_ALLOWED

__all__ = [
	'HTTP_200', 'HTTP_OK',
	'HTTP_405', 'HTTP_METHOD_NOT_ALLOWED',
]
