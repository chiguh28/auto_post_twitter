from PySide6.QtCore import QThread, QMutexLocker, QMutex, Signal
from module.counter import Counter


class Tweet(QThread):
    """Twitterクラスの親クラス
    ツイート収集、ツイート投稿の親となるクラスを設定する
    サブスレッドで処理をする必要があるためQThreadを継承させる

    Args:
        QThread ([type]): [description]
    """

    # シグナルを設定する
    printThread = Signal(str)
    finish = Signal()

    def __init__(self, parent=None) -> None:
        QThread.__init__(self, parent)
        # スレッド制御用メンバ
        self.mutex = QMutex()
        self.stopped = False
        self.counter = Counter()

    def __del__(self):
        self.stop()
        self.wait()

    def set_api(self, api):
        """apiをセットする
        認証されたtweepyのAPIをクラスにセットする

        Args:
            api ([type]): [description]
        """
        self.api = api

    def run(self):
        pass

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
