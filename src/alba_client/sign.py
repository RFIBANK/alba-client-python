# -*- coding: utf-8 -*-
import urllib
import base64
import hashlib
import hmac
import urlparse

DEFAULT_SIGN_EXCLUDE = ['check', 'mac', 'check_gate_internal']


def sign(method, url, params, secret_key, exclude=DEFAULT_SIGN_EXCLUDE):
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
        url_parsed.hostname,
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
