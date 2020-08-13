import requests
from bs4 import BeautifulSoup

from automate.base import BasePageObject, set_response


class DetilQueryPageObject(BasePageObject):
    detil_query_url = "https://kkp2.atrbpn.go.id/peta/DataSpasial/DetilQuery"
    get_wilayah_url = "https://kkp2.atrbpn.go.id/peta/Wilayah/GetWilayah"
    url_query = "https://kkp2.atrbpn.go.id/peta/DataSpasial/QueryByNIB"
    detil_info_url = "https://kkp2.atrbpn.go.id/peta/DataSpasial/DetilInfoFromPP"

    @set_response
    def init_page(self) -> requests.Response:

        self.start_result = 0
        self.num_result = 20

        resp = self._s.get(self.detil_query_url)
        return resp

    @property
    def soup(self) -> BeautifulSoup:
        return self.make_soup(self.latest_response.resp)

    def _get_wilayah(self, tipe: str, kode: str) -> list:
        params = {
            "tipe": tipe,
            "kode": kode,
            "inkantor": "True"
        }
        resp = self._s.get(self.get_wilayah_url, params=params)
        return resp.json()

    def set_kecamatan(self, kecamatan: str):
        for option in self.soup.select("[name='inputwilayah.SelectedKecamatan'] option"):
            text = option.get_text().lower()
            if kecamatan.lower() == text:
                self._data["detil_query"]["inputwilayah.SelectedKecamatan"] = option["value"]
                return
        else:
            raise Exception(f"Kecamatan {kecamatan} tidak ditemukan.")

    def set_desa(self, desa: str):
        wilayah_list = self._get_wilayah("keca", self._data["detil_query"]["inputwilayah.SelectedKecamatan"])
        for wilayah in wilayah_list:
            nama = wilayah["nama"].lower()
            if desa.lower() == nama:
                self._data["detil_query"]["inputwilayah.SelectedDesa"] = wilayah["wilayahid"]
                return
        else:
            raise Exception(f"Desa {desa} tidak ditemukan.")

    def _set_provinsi(self):
        option = self.soup.select_one("[name='inputwilayah.SelectedPropinsi'] option")
        self._data["detil_query"]["inputwilayah.SelectedPropinsi"] = option["value"]

    def _set_kabupaten(self):
        option = self.soup.select_one("[name='inputwilayah.SelectedKabupaten'] option")
        self._data["detil_query"]["inputwilayah.SelectedKabupaten"] = option["value"]

    def cari(self, start=None, length=None):
        self._set_provinsi()
        self._set_kabupaten()

        if not start:
            start = self.start_result

        if not length:
            length = self.num_result

        self._data["detil_query"]["start"] = start
        self._data["detil_query"]["length"] = length

        resp = self._s.post(self.url_query, self._data["detil_query"])

        # update the start
        self.start_result += self.num_result
        return resp.json()

    def get_detail_info(self, pid: str):
        data = {
            "featureId": f"PersilBerdasarkanStatusPendaftaran.{pid}",
            "page": 1
        }
        resp = self._s.post(self.detil_info_url, data=data)
        return resp.json()