# -*- coding: utf-8 -*-


class AlbaException(Exception):
    pass


class UniqueError(AlbaException):
    pass


class AuthError(AlbaException):
    pass


CODE2EXCEPTION = {
    'unknown': AlbaException,
    'unique': UniqueError,
    'auth': AuthError,
}
