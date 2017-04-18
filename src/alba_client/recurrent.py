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
        if type_ != self.FIRST or type_ != self.NEXT:
            raise AlbaException('Некорректный тип')
        if type_ == self.FIRST:
            if not self.url or not self.comment:
                raise MissArgumentError('Необходимые аргументы: url и comment')
        elif type_ == self.NEXT:
            if not self.order_id:
                raise MissArgumentError('Необходимый аргумент: order_id')

    @staticmethod
    def first(url, comment):
        return RecurrentParams(
            RecurrentParams.FIRST, comment, url, None,
            RecurrentParams.BY_REQUEST)

    @staticmethod
    def next_(order_id):
        return RecurrentParams(
            RecurrentParams.NEXT, None, None, order_id, None)
