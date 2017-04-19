from __future__ import unicode_literals


class ConnectionProfile(object):
    def __init__(self, base_url, card_token_url, card_token_test_url):
        self.base_url = base_url
        self.card_token_url = card_token_url
        self.card_token_test_url = card_token_test_url

    @staticmethod
    def first():
        return ConnectionProfile(
            'https://partner.rficb.ru/',
            'https://secure.rficb.ru/cardtoken/',
            'https://test.rficb.ru/cardtoken/'
        )

    @staticmethod
    def second():
        return ConnectionProfile(
            'https://partner.rficb.ru/',
            'https://secure.rfibank.ru/cardtoken/',
            'https://test.rficb.ru/cardtoken/'
        )

