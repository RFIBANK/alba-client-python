# -*- coding: utf-8 -*-


class AlbaCallback(object):

    def __init__(self, services):
        """
        services список сервисов
        """
        self.services = {
            str(service.service_id): service for service in services
        }

    def handle(self, post):
        """
        Обработка нотификаций
        """
        if 'service_id' not in post:
            raise AlbaException(
                u'Отсутствует обязательный параметр service_id')

        if post['service_id'] in self.services:
            service = self.services[post['service_id']]
            if service.check_callback_sign(post):
                self.callback(post)
            else:
                raise AlbaException("Ошибка в подписи")
        else:
            raise AlbaException(
                u"Неизвестный сервис: %s" % type(post['service_id']))

    def callback(self, data):
        """
        Обработка callback после проверки подписи
        """
        if data['command'] == 'process':
            self.callback_process(data)
        elif data['command'] == 'success':
            self.callback_success(data)
        elif data['command'] == 'recurrent_cancel':
            self.callback_recurrent_cancel(data)
        elif data['command'] == 'refund':
            self.callback_refund(data)
        else:
            raise AlbaException(
                u"Неожиданный тип уведомления: %s" % data['command'])

    def callback_process(self, data):
        """
        вызывается при любой (в том числе частичной) оплате сервиса
        """
        pass

    def callback_success(self, data):
        """
        вызывается при полной оплате сервиса
        """

    def callback_recurrent_cancel(self, data):
        """
        вызывается, когда держатель карты оменил подписку на рекурренты
        """
        pass

    def callback_refund(self, data):
        """
        результат проведения возврата
        """
        pass
