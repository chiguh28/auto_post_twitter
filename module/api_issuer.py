import tweepy
from PySide6.QtCore import QThread, QMutexLocker, QMutex, Signal

from .getter_access_token import GetterAccessToken
from .config import CONFIG


class ApiIssuer(QThread):
    """APIを発行するクラス

    Args:
        QThread ([type]): [description]

    Raises:
        Exception: アクセストークン取得に失敗した場合に例外に飛ばしてエラー表示を促す

    Returns:
        [type]: [description]
    """
    printThread = Signal(str)

    def __init__(self, parent=None) -> None:
        QThread.__init__(self, parent)
        # スレッド制御用メンバ
        self.mutex = QMutex()
        self.stopped = False

    def run(self):
        """スレッド処理実行
        API発行をサブスレッドで実行する
        """
        self.restart()
        self.issue()
        self.stop()

    def stop(self):
        """スレッドを停止させる
        """
        if not self.stopped:
            with QMutexLocker(self.mutex):
                self.stopped = True

    def restart(self):
        """スレッドを利用する
        """
        if self.stopped:
            with QMutexLocker(self.mutex):
                self.stopped = False

    def set_account(self, id, pw):
        """アカウント情報を設定する
        APIキー発行申請をする前に先にアカウント情報を設定すること

        Args:
            id ([type]): [description]
            pw ([type]): [description]
        """
        self.id = id
        self.pw = pw

    def issue(self):
        self.printThread.emit('ログイン処理開始')
        # APIキーの取得
        api_key = CONFIG['API_KEY']
        api_secret_key = CONFIG['API_SECRET_KEY']

        try:
            # API認証用アクセストークン処理
            getter = GetterAccessToken(
                api_key, api_secret_key, self.id, self.pw)
            access_token, access_secret_token = getter.get_access_token()

            if access_token == -1:
                raise Exception

            auth = tweepy.OAuthHandler(api_key, api_secret_key)
            auth.set_access_token(access_token, access_secret_token)

            # API設定
            self.api = tweepy.API(auth)
            self.printThread.emit('ログインに成功しました。')

            # 後処理
            self.finished.emit()

        except Exception:
            self.printThread.emit('ログインエラー! 再度ログインしてください。')

    def get_api(self):
        return self.api
