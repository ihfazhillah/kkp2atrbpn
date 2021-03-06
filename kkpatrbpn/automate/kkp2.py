from concurrent import futures
from collections import namedtuple
from functools import partial, reduce

import backoff as backoff
import requests
from requests.exceptions import ReadTimeout

from kkpatrbpn.automate.pages import LoginPageObject, PilihKantorPageObject, DetilQueryPageObject


ValidationResult = namedtuple(
    "ValidationResult",
    (
        "total_count",
        "validated_count",
        "unvalidated_count",
        "all_result",
    )
)


class KKP:

    def __init__(self, username: str, password: str, kantor: str, use_concurent=True):
        self.session = requests.Session()

        self.username = username
        self.password = password
        self.kantor = kantor

        self.use_concurrent = use_concurent

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

    def validasi_persil(self, kecamatan: str, desa: str) -> ValidationResult:
        print("validasi...")
        """
        Return not valid bidang, with its info and reason why its not valid

        :param kecamatan:
        :param desa:
        :return:
        """
        detail_query = DetilQueryPageObject(self.session)
        detail_query.set_kecamatan(kecamatan)
        detail_query.set_desa(desa)

        all_persil = []

        # ambil semua data
        count = 1
        while True:
            print(f"prosess page {count}")
            start = detail_query.start_result
            length = detail_query.num_result

            resp = detail_query.cari(start, length)
            all_persil += resp["data"]

            if start >= resp["recordsFiltered"]:
                break

            count += 1

        all_persil = tuple(all_persil)
        total_count = len(all_persil)

        valid_persil = tuple(persil for persil in all_persil if persil["ValidasiGeom"] == "true")
        unvalidated_persil = tuple(persil for persil in all_persil if persil["ValidasiGeom"] != "true")

        valid_persil_count = len(valid_persil)
        unvalidated_persil_count = len(unvalidated_persil)

        def get_info(persil, **kwargs):
            detail = detail_query.get_detail_info(persil["PersilId"])
            detail["Sudah Valid"] = "Valid" if persil["ValidasiGeom"] == "true" else "Tidak Valid"
            detail["Keterangan"] = ""
            return detail

        def get_gambar_belum_ada(persil, detail):
            if persil["Gambar"] != "true":
                detail["Keterangan"] = "Gambar belum ada."
            return detail

        def validasi_persil(persil, detail):
            pid = persil["PersilId"]
            gambar = persil["Gambar"] == "true"
            validasi_geom = persil["ValidasiGeom"] == "true"
            if gambar and not validasi_geom:
                resp = detail_query.validate_bidang(pid)
                valid = resp["Status"]
                message = resp["Message"]

                if valid:
                    detail["Sudah Valid"] = "Valid"
                else:
                    detail["Sudah Valid"] = "Tidak Valid"
                    detail["Keterangan"] = message
            return detail


        # for all persil, add these function with persil
        @backoff.on_exception(
            backoff.expo,
            ReadTimeout
        )
        def validate(persil):
            print(f"Validasi persil: {persil}")
            transform_functions = (
                get_info,
                get_gambar_belum_ada,
                validasi_persil
            )
            filled_with_persil = (
                partial(func, persil=persil)
                for func in transform_functions
            )
            return reduce(
                lambda detail, fun: fun(detail=detail),
                filled_with_persil,
                {}
            )

        if self.use_concurrent:
            print("gunakan concurrent")
            with futures.ProcessPoolExecutor() as executor:
                all_result = tuple(executor.map(validate, all_persil))
        else:
            all_result = tuple(map(validate, all_persil))

        return ValidationResult(
            total_count,
            valid_persil_count,
            unvalidated_persil_count,
            all_result
        )
