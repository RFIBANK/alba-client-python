# -*- coding: utf-8 -*-
import logging
import urllib
import requests
import base64
import hashlib
import hmac
import urlparse
import json


class AlbaException(Exception):
    pass


def sign(method, url, params, secret_key, exclude=['check', 'mac']):
    """
    Типовой метод для подписи HTTP запросов
    """
    url_parsed = urlparse.urlparse(url)
    keys = [param for param in params if param not in exclude]
    keys.sort()

    result = []
    for key in keys:
        value = urllib.quote(
            unicode(params.get(key) or '').encode('utf-8'),
            safe='~'
        )
        result.append('{}={}'.format(key, value))

    data = "\n".join([
        method,
        url_parsed.netloc,
        url_parsed.path,
        "&".join(result)
    ])

    digest = hmac.new(
        secret_key,
        data,
        hashlib.sha256
    ).digest()
    signature = base64.b64encode(digest)
    return signature


class AlbaService(object):
    BASE_URL = 'https://partner.rficb.ru/'

    def __init__(self, service_id, secret, logger=None):
        """
        service_id идентификатор сервиса
        secret секретный ключ сервиса
        """
        self.service_id = service_id
        self.secret = secret
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    def _request(self, url, method, data):
        try:
            self.logger.debug(u'Sent {} request with params {}'
                              .format(method.upper(), data))

            if method == 'get':
                response = requests.get(url, params=data)
            else:
                response = requests.post(url, data)

            if response.status_code != 200:
                self.logger.debug(u'Server unavailable: {}'
                                  .format(response.status_code))
                raise AlbaException(u"Север не доступен: {}"
                                    .format(response.status_code))
        except requests.ConnectionError, e:
            raise AlbaException(e)

        self.logger.debug(u'Server response: {}'.format(response.content))

        json_response = json.loads(response.content)
        if json_response['status'] == 'error':
            msg = json_response.get('msg', json_response.get('message'))
            code = json_response.get('code', 'unknown')
            raise AlbaException(msg)

        return json_response

    def _get(self, url, data=None):
        return self._request(url, 'get', data)

    def _post(self, url, data=None):
        return self._request(url, 'post', data)

    def pay_types(self):
        """
        Полуение списка доступных способов оплаты для сервиса
        """
        check = hashlib.md5(str(self.service_id) + self.secret).hexdigest()
        url = ("%sa1lite/pay_types/?service_id=%s&check=%s" %
               (self.BASE_URL, self.service_id, check))
        return self._get(url)['types']

    def init_payment(self, pay_type, cost, name, email, phone, order_id=False):
        """
        Инициация оплаты
        pay_type способ оплаты
        cost сумма платежа
        name наименование товара
        email e-mail покупателя
        order_id идентификатор заказа
        """
        fields = {
            "cost": cost,
            "name": name,
            "email": email,
            "phone_number": phone,
            "background": "1",
            "type": pay_type,
            "service_id": self.service_id,
            "version": "2.0"
        }
        if order_id is not False:
            fields['order_id'] = order_id

        url = self.BASE_URL + "a1lite/input/"
        fields['check'] = sign("POST", url, fields, self.secret)

        return self._post(url, fields)

    def transaction_details(self, tid):
        """
        Получение информации о транзакции
        tid идентификатор транзакции
        """
        params = {'api_key': self.secret, 'tid': tid}
        url = self.BASE_URL + "a1lite/details/"
        answer = self._post(url, params)
        return answer

    def refund(self, tid, amount):
        """
        проведение возврата
        gate короткое имя шлюза
        """
        fields = {'api_key': self.secret,
                  'amount': amount,
                  'tid': tid}
        url = self.BASE_URL + "a1lite/refund/"
        answer = self._post(url, fields)
        return answer

    def gate_details(self, gate):
        """
        получение информации о шлюзе
        gate короткое имя шлюза
        """
        params = {'api_key': self.secret, 'gate': gate}
        url = self.BASE_URL + "a1lite/gate_details/"
        answer = self._get(url, params)
        return answer

    def check_callback_sign(self, post):
        """
        Обработка нотификации
        array $post Массив $_POST параметров
        """
        order = ['tid',
                 'name',
                 'comment',
                 'partner_id',
                 'service_id',
                 'order_id',
                 'type',
                 'cost',
                 'income_total',
                 'income',
                 'partner_income',
                 'system_income',
                 'command',
                 'phone_number',
                 'email',
                 'resultStr',
                 'date_created',
                 'version']
        params = [post.get(field, '') for field in order]
        params.append(self.secret)
        return hashlib.md5(''.join(params)).hexdigest() == post['check']


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
