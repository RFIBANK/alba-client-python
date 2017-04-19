from __future__ import unicode_literals


class CardTokenRequest(object):
    def __init__(self, service_id, card, exp_month, exp_year, cvc,
                 card_holder=None):
        self.service_id = service_id
        self.card = card
        self.exp_month = exp_month
        self.exp_year = exp_year
        self.cvc = cvc
        self.card_holder = card_holder


class CardTokenResponse(object):
    def __init__(self, json_object=None):
        self.errors = {}
        self.token = ''

        if json_object:
            if json_object.get('status') == 'success':
                self.token = str(json_object.get('token'))
            else:
                if json_object.get('errors'):
                    json_errors = json_object.get('errors')
                    for key, errors_array in json_errors.items():
                        for e in errors_array:
                            if key not in self.errors:
                                self.errors.update({key: []})
                            self.errors[key].append(e)
