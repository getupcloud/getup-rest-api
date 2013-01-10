# -*- coding: utf-8 -*-

from error import ProviderError, DomainError, AppError
from openshift import OpenShift
from functools import wraps

def provider(wrapped):
	@wraps(wrapped)
	def wrapper(user, *vargs, **kvargs):
		assert user, 'invalid or missing user'
		prov = OpenShift(user['email'], user['authentication_token'])
		return wrapped(user=user, prov=prov, *vargs, **kvargs)
	return wrapper
