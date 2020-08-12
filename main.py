import requests

from automate.login_page import LoginPageObject
from automate.pilih_kantor import PilihKantorPageObject
from environs import Env


def main():
    env = Env()
    env.read_env()

    s = requests.Session()

    login = LoginPageObject(s)
    login.set_username(env("KKP_USERNAME"))
    login.set_password(env("KKP_PASSWORD"))
    login.submit()

    pilih_kantor = PilihKantorPageObject(s)
    pilih_kantor.pilih(env("KKP_KANTOR"))
    pilih_kantor.submit()

    print(pilih_kantor.latest_response.resp.content)


if __name__ == "__main__":
    main()