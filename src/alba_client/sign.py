# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from six import text_type
from six.moves.urllib.parse import urlparse, quote

import base64
import hashlib
import hmac

DEFAULT_SIGN_EXCLUDE = ['check', 'mac', 'check_gate_internal']


def sign(method, url, params, secret_key, exclude=DEFAULT_SIGN_EXCLUDE):
    """
    Типовой метод для подписи HTTP запросов
    """
    url_parsed = urlparse(url)
    keys = [param for param in params if param not in exclude]
    keys.sort()

    result = []
    for key in keys:
        value = quote(
            text_type(params.get(key) or '').encode('utf-8'),
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
        secret_key.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).digest()
    signature = base64.b64encode(digest)
    return signature
