# -*- coding: utf-8 -*-


class AlbaException(Exception):
    def __init__(self, message, errors=None):
        super(AlbaException, self).__init__(message)
        self.errors = errors or {}


class UniqueError(AlbaException):
    pass


class AuthError(AlbaException):
    pass


class MissArgumentError(AlbaException, ValueError):
    pass


CODE2EXCEPTION = {
    'unknown': AlbaException,
    'common': AlbaException,
    'unique': UniqueError,
    'auth': AuthError,
}
