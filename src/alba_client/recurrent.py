# coding=utf-8
from __future__ import unicode_literals

from .exceptions import AlbaException, MissArgumentError


class RecurrentParams(object):
    FIRST = 'first'
    NEXT = 'next'
    BY_REQUEST = 'byrequest'

    def __init__(self, type_, comment, url, order_id, period):
        self.type = type_
        self.comment = comment
        self.url = url
        self.order_id = order_id
        self.period = period
        if type_ == self.FIRST:
            if not self.url or not self.comment:
                raise MissArgumentError('Необходимые аргументы: url и comment')
        elif type_ == self.NEXT:
            if not self.order_id:
                raise MissArgumentError('Необходимый аргумент: order_id')

    @classmethod
    def first_pay(cls, url, comment):
        return cls(cls.FIRST, comment, url, None, cls.BY_REQUEST)

    @classmethod
    def next_pay(cls, order_id):
        return cls(cls.NEXT, None, None, order_id, None)
