from collections import defaultdict
from typing import Optional

import requests
from bs4 import BeautifulSoup


requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'


headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Origin': 'https://kkp2.atrbpn.go.id',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://kkp2.atrbpn.go.id/Account/Index?ReturnUrl=%2f',
    'Accept-Language': 'en-US,en;q=0.9,id-ID;q=0.8,id;q=0.7',
}


class LatestResponse:
    def __init__(self):
        self.resp : Optional[requests.Response] = None

    def set_response(self, resp: requests.Response):
        self.resp = resp


latest_response : LatestResponse = LatestResponse()


def set_response(function):
    def inner(*args, **kwargs):
        self = args[0]
        ret = function(*args, **kwargs)
        if isinstance(ret, requests.Response):
            self.latest_response.set_response(ret)
        return ret
    return inner


class BasePageObject():

    get_wilayah_url = "https://kkp2.atrbpn.go.id/peta/Wilayah/GetWilayah"

    def __init__(self, session: requests.Session):
        self._s = session
        self._s.headers.update(headers)
        self._data = defaultdict(dict)
        self.latest_response = latest_response
        self.init_page()

    def init_page(self):
        return True

    @staticmethod
    def make_soup(resp: requests.Response) -> BeautifulSoup:
        soup = BeautifulSoup(resp.content, "html.parser")
        return soup

    def get_wilayah(self, tipe: str, kode: str) -> list:
        params = {
            "tipe": tipe,
            "kode": kode,
            "inkantor": "True"
        }
        resp = self._s.get(self.get_wilayah_url, params=params)
        return resp.json()
