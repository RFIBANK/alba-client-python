import hashlib
import requests_mock
from unittest import TestCase

from six import text_type

from alba_client import AlbaService, AlbaException
from alba_client.recurrent import RecurrentParams


class ServiceTestCase(TestCase):
    def setUp(self):
        self.service = AlbaService('10000', 'secret')

    def test_correct_create_card_token(self):
        with requests_mock.mock() as m:
            m.post(
                self.service.connection_profile['card_token_test_url']
                + 'create', json={'status': 'success', 'token': 'test'})
            token = self.service.create_card_token(
                '4300000000000777', '1', '22', '123', test=True,
                card_holder='Cardholder Name')
            self.assertEqual(token, 'test')

    def test_wrong_create_card_token(self):
        with requests_mock.mock() as m:
            m.post(self.service.connection_profile['card_token_test_url']
                   + 'create', exc=AlbaException('Invalid data'))
            with self.assertRaises(AlbaException):
                self.service.create_card_token(
                    '4652060573334999', '01', '17', '067', test=True)

    def test_create_service_with_custom_connection_profile_and_loger(self):
        service = AlbaService(
            '10000', 'secret',
            connection_profile=AlbaService.SECOND_CONNECTION_PROFILE,
            logger='logger')
        self.assertEqual(
            service.connection_profile['card_token_url'],
            AlbaService.SECOND_CONNECTION_PROFILE['card_token_url'])
        self.assertEqual(service.logger, 'logger')

    def test_correct_init_payment(self):
        with requests_mock.mock() as m:
            m.post(self.service.connection_profile['base_url'] + 'alba/input/',
                   json={'status': 'success', 'tid': 100})
            response = self.service.init_payment(
                'mc', 200, 'Test', 'test@test.ru', '79091234567')
            self.assertEqual(response['status'], 'success')
            self.assertEqual(response['tid'], 100)

    def test_correct_init_payment_with_order_id_and_comment(self):
        with requests_mock.mock() as m:
            m.post(self.service.connection_profile['base_url'] + 'alba/input/',
                   json={'status': 'success', 'tid': 100})
            response = self.service.init_payment(
                'mc', 200, 'Test', 'test@test.ru', '79091234567', order_id=100,
                comment='Комментарий')
            self.assertEqual(response['status'], 'success')
            self.assertEqual(response['tid'], 100)

    def test_correct_init_first_recurrent_payment(self):
        with requests_mock.mock() as m:
            m.post(self.service.connection_profile['base_url'] + 'alba/input/',
                   json={'status': 'success', 'tid': 100})
            recurrent_params = RecurrentParams.first_pay(
                'http://test.ru', 'Комментарий')
            response = self.service.init_payment(
                'spg_test', 200, 'Test', 'test@test.ru', '79091234567',
                order_id=100, recurrent_params=recurrent_params,
                card_token='token')
            self.assertEqual(response['status'], 'success')
            self.assertEqual(response['tid'], 100)

    def test_correct_init_next_recurrent_payment(self):
        with requests_mock.mock() as m:
            m.post(self.service.connection_profile['base_url'] + 'alba/input/',
                   json={'status': 'success', 'tid': 100})
            recurrent_params = RecurrentParams.next_pay(100)
            response = self.service.init_payment(
                'spg_test', 200, 'Test', 'test@test.ru', '79091234567',
                recurrent_params=recurrent_params, card_token='token')
            self.assertEqual(response['status'], 'success')
            self.assertEqual(response['tid'], 100)

    def test_correct_init_payment_with_bank_params_and_commission(self):
        with requests_mock.mock() as m:
            m.post(self.service.connection_profile['base_url'] + 'alba/input/',
                   json={'status': 'success', 'tid': 100})
            bank_params = {'param': 'test', 'param2': 'test'}
            response = self.service.init_payment(
                'mc', 200, 'Test', 'test@test.ru', '79091234567',
                commission=10, bank_params=bank_params)
            self.assertEqual(response['status'], 'success')
            self.assertEqual(response['tid'], 100)

    def test_init_first_recurrent_payment_without_url_and_comment(self):
        with requests_mock.mock() as m:
            m.post(self.service.connection_profile['base_url'] + 'alba/input/',
                   json={'status': 'success', 'tid': 100})
            with self.assertRaises(AlbaException):
                recurrent_params = RecurrentParams(
                    'first', None, None, None, 'byrequest')
                self.service.init_payment(
                    'spg_test', 200, 'Test', 'test@test.ru', '79091234567',
                    order_id=100, recurrent_params=recurrent_params,
                    card_token='token')

    def test_init_next_recurrent_payment_without_order_id(self):
        with requests_mock.mock() as m:
            m.post(self.service.connection_profile['base_url'] + 'alba/input/',
                   json={'status': 'success', 'tid': 100})
            with self.assertRaises(AlbaException):
                recurrent_params = RecurrentParams(
                    'next', None, None, None, None)
                self.service.init_payment(
                    'spg_test', 200, 'Test', 'test@test.ru', '79091234567',
                    order_id=100, recurrent_params=recurrent_params,
                    card_token='token')

    def test_init_payment_wrong_phone(self):
        with requests_mock.mock() as m:
            m.post(self.service.connection_profile['base_url'] + 'alba/input/',
                   exc=AlbaException('Данный оператор не поддерживает оплату '
                                     'мобильной коммерции'))
            with self.assertRaises(AlbaException):
                self.service.init_payment(
                    'mc', 200, 'Test', 'test@test.ru', '79191234567')

    def test_get_transaction_details_by_tid(self):
        with requests_mock.mock() as m:
            url = self.service.connection_profile['base_url'] + "alba/details/"
            m.post(url, json={
                'status': 'success', 'transaction_status': 'payed',
                'tid': '100', 'income_total': 200
            })
            details = self.service.transaction_details(tid=100)
            self.assertEqual(details['status'], 'success')
            self.assertEqual(details['transaction_status'], 'payed')
            self.assertEqual(details['tid'], '100')
            self.assertEqual(details['income_total'], 200)

    def test_get_transaction_details_by_order_id(self):
        with requests_mock.mock() as m:
            url = self.service.connection_profile['base_url'] + "alba/details/"
            m.post(url, json={
                'status': 'success', 'transaction_status': 'payed',
                'tid': '100', 'income_total': 200
            })
            details = self.service.transaction_details(order_id=100)
            self.assertEqual(details['status'], 'success')
            self.assertEqual(details['transaction_status'], 'payed')
            self.assertEqual(details['tid'], '100')
            self.assertEqual(details['income_total'], 200)

    def test_get_transaction_details_without_params(self):
        with self.assertRaises(AlbaException):
            self.service.transaction_details()

    def test_get_gate_details(self):
        with requests_mock.mock() as m:
            url = (self.service.connection_profile['base_url']
                   + "alba/gate_details/")
            m.get(url, json={
                'status': 'success', 'name': 'Мобильный платёж',
                'init_payment': '1', 'percent': 85
            })
            gate_details = self.service.gate_details('mc')
            self.assertEqual(gate_details['status'], 'success')
            self.assertEqual(gate_details['name'], 'Мобильный платёж')
            self.assertEqual(gate_details['init_payment'], '1')
            self.assertEqual(gate_details['percent'], 85)

    def test_connection_error(self):
        with requests_mock.mock() as m:
            m.post(self.service.connection_profile['base_url'] + 'alba/input/',
                   status_code=404)
            with self.assertRaises(AlbaException):
                self.service.init_payment(
                    'mc', 200, 'Test', 'test@test.ru', '79091234567')

    def test_error_response(self):
        with requests_mock.mock() as m:
            m.post(self.service.connection_profile['base_url'] + 'alba/input/',
                   json={'status': 'error', 'msg': 'Some error'})
            with self.assertRaises(AlbaException):
                self.service.init_payment(
                    'mc', 200, 'Test', 'test@test.ru', '79091234567')

    def test_get_pay_types(self):
        with requests_mock.mock() as m:
            check = hashlib.md5((
                    text_type(
                        self.service.service_id) +
                    self.service.secret).encode('utf-8'))
            check = check.hexdigest()
            url = ("%salba/pay_types/?service_id=%s&check=%s" %
                   (self.service.connection_profile['base_url'],
                    self.service.service_id, check))
            m.get(url, json={'status': 'success', 'types': ['mc']})
            pay_types = self.service.pay_types()
            self.assertIn('mc', pay_types)

    def test_correct_refund(self):
        with requests_mock.mock() as m:
            url = self.service.connection_profile['base_url'] + "alba/refund/"
            m.post(url, json={'status': 'success', 'payback_id': 1000})
            response = self.service.refund(10, amount=1000, test=True,
                                           reason='Some reason')
            self.assertEqual(response['status'], 'success')
            self.assertEqual(response['payback_id'], 1000)

    def test_wrong_refund(self):
        with requests_mock.mock() as m:
            url = self.service.connection_profile['base_url'] + "alba/refund/"
            m.post(url, json={'status': 'error', 'message': 'Some error'})
            response = self.service.refund(10, test=True)
            self.assertEqual(response['status'], 'error')
            self.assertEqual(response['message'], 'Some error')

    def test_check_callback_sign(self):
        order = ['tid', 'name', 'comment', 'partner_id', 'service_id',
                 'order_id', 'type', 'cost', 'income_total', 'income',
                 'partner_income', 'system_income', 'command', 'phone_number',
                 'email', 'resultStr', 'date_created', 'version']
        post = {'tid': '1000', 'name': 'test'}
        params = [post.get(field, '') for field in order]
        params.append(self.service.secret)
        post_check = hashlib.md5(
            (''.join(params)).encode('utf-8')).hexdigest()
        post['check'] = post_check
        check = self.service.check_callback_sign(post)
        self.assertTrue(check)
