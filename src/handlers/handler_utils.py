from urllib.parse import parse_qs
import urllib
import logging
import requests
from datetime import datetime

# user defined packages
import gb

log = logging.getLogger(__name__)


def parse_input(uri):
    uri = uri.split("?")
    if len(uri) <= 1:
        print("No url params found")
        return {}
    params = uri[-1].split("&")
    res = {}
    for i, param in enumerate(params):
        param = param.split("=")
        try:
            res[param[0]] = int(urllib.parse.unquote(param[1]))
        except Exception as e:
            # log.error("Error parsing url params %s", uri, exc_info=True)
            res[param[0]] = urllib.parse.unquote(param[1])

    return res


def parse_urlencoded(request_body):
    temp = parse_qs(request_body)
    res = {}
    for key, val in temp.items():
        if isinstance(key, bytes):
            new_key = key.decode("utf8")
            new_val = temp[key][0].decode("utf8")
        else:
            new_key = key
            new_val = temp[key][0]
        res[new_key] = new_val
    return res