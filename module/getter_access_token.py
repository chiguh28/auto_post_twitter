from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

from .TwitterOauth import TwitterOauth

LOAD_TIME = 5


class GetterAccessToken():
    def __init__(self, api_key, api_secret_key, login_id, login_pw) -> None:
        self.auth = TwitterOauth(api_key, api_secret_key)
        self.login_id = login_id
        self.login_pw = login_pw

    def get_access_token(self):
        # PINコード
        pin_code = self._get_pincode()

        try:
            # PINコードからアクセストークンを取得する
            access_token_content = self.auth.get_access_token_content(pin_code)
            access_token = access_token_content["oauth_token"][0]
            access_token_secret = access_token_content["oauth_token_secret"][0]
            return access_token, access_token_secret
        except Exception:
            return -1, -1

    def _get_pincode(self):

        # 認証ページのURLを取得する
        authenticate_url = self.auth.get_authenticate_url()

        # driver設定
        option = Options()
        option.add_argument('--headless')

        # 認証ページを生成
        driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=option)
        driver.get(authenticate_url)
        time.sleep(LOAD_TIME)

        # 画面に表示されたPINコードを取得する
        id_form = driver.find_element_by_id('username_or_email')
        id_form.send_keys(self.login_id)
        pass_form = driver.find_element_by_id('password')
        pass_form.send_keys(self.login_pw)

        login_button = driver.find_element_by_id('allow')
        login_button.click()

        time.sleep(LOAD_TIME)
        pin_code = int(driver.find_element_by_tag_name('code').text)

        # driverは閉じる
        driver.close()

        return pin_code
