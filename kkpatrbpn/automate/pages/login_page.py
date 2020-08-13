from kkpatrbpn.automate.pages.base import BasePageObject, set_response


class LoginPageObject(BasePageObject):
    login_url = "https://kkp2.atrbpn.go.id/Account/Login"

    def set_username(self, username: str):
        self._data["login"]["UserName"] = username

    def set_password(self, password: str):
        self._data["login"]["Password"] = password

    @set_response
    def submit(self):
        params = (
            ('returnUrl', '/'),
        )
        resp = self._s.post(self.login_url, self._data["login"], params=params)
        return resp
