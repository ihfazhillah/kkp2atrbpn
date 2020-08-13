import requests

from kkpatrbpn.automate.pages import LoginPageObject, PilihKantorPageObject, DetilQueryPageObject


class KKP:

    def __init__(self, username: str, password: str, kantor: str):
        self.session = requests.Session()

        self.username = username
        self.password = password
        self.kantor = kantor

        self.login()

    def login(self):
        print("login...")
        login_page = LoginPageObject(self.session)
        login_page.set_username(username=self.username)
        login_page.set_password(self.password)
        login_page.submit()

        pilih_kantor = PilihKantorPageObject(self.session)
        pilih_kantor.pilih(self.kantor)
        pilih_kantor.submit()

    def validasi_persil(self, kecamatan: str, desa: str) -> list:
        print("validasi...")
        """
        Return not valid bidang, with its info and reason why its not valid

        :param kecamatan:
        :param desa:
        :return:
        """
        not_valid_list = []

        detail_query = DetilQueryPageObject(self.session)
        detail_query.set_kecamatan(kecamatan)
        detail_query.set_desa(desa)

        count = 1
        while True:
            print(f"prosess page {count}")
            start = detail_query.start_result
            length = detail_query.num_result

            resp = detail_query.cari(start, length)

            for persil in resp["data"]:
                non_valid = self._validate_individual_persil(persil, detail_query)
                if non_valid:
                    not_valid_list.append(non_valid)

            if start >= resp["recordsFiltered"]:
                break

            count += 1

        return not_valid_list

    def _validate_individual_persil(self, persil: dict, detail_query: DetilQueryPageObject):
        pid = persil["PersilId"]
        gambar = persil["Gambar"] == "true"
        validasi_geom = persil["ValidasiGeom"] == "true"

        if gambar and not validasi_geom:
            # validate here
            resp = detail_query.validate_bidang(pid)
            valid = resp["Status"]
            message = resp["Message"]

            if not valid:
                detail_info = detail_query.get_detail_info(pid)
                detail_info["message"] = message
                return detail_info