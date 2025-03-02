import requests
from urllib.parse import urlparse, parse_qs
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)

class web_client_request_types(object):
    GET = 1
    POST = 2

def get_param_names(url: str) -> list:
    return list(parse_qs(urlparse(url).query).keys())


def build_params(url: str, url_params: dict) -> str:
    """ Naive function to blindly update url params, assuming param values to update are named <param> and have corresponding value in url_params """
    for key, value in url_params.items():
        url = url.replace('<%s>' % key,  str(value))

    return url

def request(url: str, request_type: int = web_client_request_types.GET,
            session=None, overwrite_session_params=False, url_params: dict=None, proxies=None, headers=None, cookies=None, verify=False, _json=None, timeout=320) -> requests.Response:

    if url_params is not None:
        url = build_params(
            url=url,
            url_params=url_params,
        )

    if request_type == web_client_request_types.GET:
        request_fun = requests.get

    elif request_type == web_client_request_types.POST:
        request_fun = requests.post
    else:
        raise Exception('Unsupported request type id: %s' % str(request_type))

    if session is None:
        return request_fun(url=url, proxies=proxies, cookies=cookies, headers=headers, verify=verify, json=_json, timeout=timeout)
    else:
        if overwrite_session_params:
            return request_fun(url=url, proxies=proxies, cookies=cookies, headers=headers, verify=verify, json=_json, timeout=timeout)
        else:
            return request_fun(url=url, verify=verify, json=_json, timeout=timeout)

    return None

TestMode = False
if TestMode:

    print(build_params(
        url='https://example.com/<collection_id>?limit=<limit>',
        url_params={'collection_id': '667', 'limit': 100},
    ))

    print(request(
        request_type=web_client_request_types.GET,
        url='https://example.com/<collection_id>?limit=<limit>',
        url_params={'collection_id': '667', 'limit': 100},
    ))
