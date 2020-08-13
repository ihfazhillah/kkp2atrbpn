import requests

from automate.pages import LoginPageObject, PilihKantorPageObject


class KKP:

    def __init__(self, username: str, password: str, kantor: str):
        self.session = requests.Session()

        self.username = username
        self.password = password
        self.kantor = kantor

        self.login()

    def login(self):
        login_page = LoginPageObject(self.session)
        login_page.set_username(username=self.username)
        login_page.set_password(self.password)
        login_page.submit()

        pilih_kantor = PilihKantorPageObject(self.session)
        pilih_kantor.pilih(self.kantor)
        pilih_kantor.submit()