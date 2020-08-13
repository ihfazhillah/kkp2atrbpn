import requests

from automate.pages import LoginPageObject, PilihKantorPageObject, DetilQueryPageObject


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

        while True:
            start = detail_query.start_result
            length = detail_query.num_result

            resp = detail_query.cari(start, length)

            print(*resp["data"], sep="\n")

            if start >= resp["recordsFiltered"]:
                break


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
                pass