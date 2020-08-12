import requests
from requests.sessions import Session

from automate.detil_query import DetilQueryPageObject
from automate.login_page import LoginPageObject
from automate.pilih_kantor import PilihKantorPageObject
from environs import Env


def main():
    env = Env()
    env.read_env()

    s: Session = requests.Session()

    login = LoginPageObject(s)
    login.set_username(env("KKP_USERNAME"))
    login.set_password(env("KKP_PASSWORD"))
    login.submit()

    pilih_kantor = PilihKantorPageObject(s)
    pilih_kantor.pilih(env("KKP_KANTOR"))
    pilih_kantor.submit()

    detil_query = DetilQueryPageObject(s)
    detil_query.set_kecamatan("tebo tengah")
    detil_query.set_desa("semabu")
    count = 1
    while True:
        print(f"pencarian page {count} dengan 20 hasil")
        start = detil_query.start_result
        length = detil_query.num_result
        resp = detil_query.cari(start, length)
        print(resp)
        if start >= resp["recordsFiltered"]:
            break
        count += 1
        print("")
        print("")
        print("")

    # print(pilih_kantor.latest_response.resp.content)


if __name__ == "__main__":
    main()