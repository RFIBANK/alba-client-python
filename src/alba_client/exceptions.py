# -*- coding: utf-8 -*-


class AlbaException(Exception):
    pass


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
