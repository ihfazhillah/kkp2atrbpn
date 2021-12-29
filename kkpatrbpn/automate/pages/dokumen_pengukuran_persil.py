from kkpatrbpn.automate.pages.base import BasePageObject, set_response


class LepasValidasiError(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        super(LepasValidasiError, self).__init__(message, *args, **kwargs)


class DokumenPengukuranPersil(BasePageObject):
    list_page = "https://kkp2.atrbpn.go.id/dokumen/DokumenPengukuran/Persil"
    list_table = "https://kkp2.atrbpn.go.id/dokumen/DokumenPengukuran/DaftarPersil"
    buka_validasi_url = "https://kkp2.atrbpn.go.id/dokumen/DokumenPengukuran/BukaValidasiPersil"

    @set_response
    def init_page(self):
        return self._s.get(self.list_page)

    def set_kecamatan_id(self, kecamatan_id: str):
        self._data["persil_query"]["inputwilayah.SelectedKecamatan"] = kecamatan_id

    def set_desa_id(self, desa_id: str):
        self._data["persil_query"]["inputwilayah.SelectedDesa"] = desa_id

    @property
    def soup(self):
        return self.make_soup(self.latest_response.resp)

    def _set_provinsi(self):
        option = self.soup.select_one("[name='inputwilayah.SelectedPropinsi'] option")
        self._data["persil_query"]["inputwilayah.SelectedPropinsi"] = option["value"]

    def _set_kabupaten(self):
        option = self.soup.select_one("[name='inputwilayah.SelectedKabupaten'] option")
        self._data["persil_query"]["inputwilayah.SelectedKabupaten"] = option["value"]

    def set_nib(self, nib: str):
        self._data["persil_query"]["NomorBidang"] = nib

    def set_status_validasi(self, validated: bool = True):
        self._data["persil_query"]["StatusValidasi"] = 1 if validated else 0

    def _lepas_validasi(self, persil_id: str):
        resp = self._s.post(self.buka_validasi_url, data={"pid": persil_id})
        resp_data = resp.json()
        if resp_data["Status"]:
            return

        print(resp_data["Message"])
        raise LepasValidasiError(resp_data["Message"])

    def buka_validasi(self):
        self._set_provinsi()
        self._set_kabupaten()
        self.set_status_validasi()

        page = 0
        while True:
            response = self._s.post(self.list_table, data=self._data["persil_query"])
            if response.text.strip() == "noresults":
                break

            print(f"page {page}")
            soup = self.make_soup(response)
            rows = soup.find_all("tr")
            for row in rows:
                print(row.get_text(strip=True))
                persil_id = row["data-persil"]
                print(f"dapat persil id: {persil_id}")
                self._lepas_validasi(persil_id)

            page += 1
            self._data["persil_query"]["pageNum"] = page

