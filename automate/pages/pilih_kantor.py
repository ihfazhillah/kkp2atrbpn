from automate.pages.base import BasePageObject, set_response


class PilihKantorPageObject(BasePageObject):
    set_kantor_url = "https://kkp2.atrbpn.go.id/Account/SetKantor"

    def init_page(self):
        if not "pilih kantor" in self.latest_response.resp.text.lower():
            raise Exception("Sekarang bukan page pilih kantor.")

    def pilih(self, kantor: str):
        soup = self.make_soup(self.latest_response.resp)
        kantor_list = soup.select("#selectKantor option")
        for kantor_opt in kantor_list:
            text = str(kantor_opt.get_text()).lower()
            print(text)
            if kantor in text:
                self._data["pilih_kantor"]["SelectedOffice"] = kantor_opt["value"]
                return
        else:
            raise Exception(f"Pilihan kantor {kantor} tidak ketemu...")

    @set_response
    def submit(self):
        soup = self.make_soup(self.latest_response.resp)
        inputs = soup.select("input[type='hidden']")
        data = {inp["name"]: inp.attrs.get("value") for inp in inputs}
        self._data["pilih_kantor"].update(data)
        resp = self._s.post(self.set_kantor_url, data=self._data["pilih_kantor"])
        return resp
