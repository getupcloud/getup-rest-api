# -*- coding: utf-8 -*-

import os.path

def where():
	print 'certificates:', os.path.join(os.path.dirname(__file__), 'certs.pem')
	return os.path.join(os.path.dirname(__file__), 'certs.pem')
