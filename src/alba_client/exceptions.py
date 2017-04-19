# -*- coding: utf-8 -*-


class AlbaException(Exception):
    def __init__(self, msg, errors=None):
        self.msg = msg
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
