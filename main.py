# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
import datetime

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QFile, Slot, QTimer
from PySide6.QtUiTools import QUiLoader


from module.collector_tweet import CollectorTweet
from module.models import TweetModel
from module.post_tweet import PostTweet
from module.api_issuer import ApiIssuer

DB_NAME = 'tweet.db'
MAX_LINE = 3


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui_dialog = self.load_ui()
        self.ui_dialog.log.setReadOnly(True)
        self.timer = QTimer()

        # イベントハンドラ
        self.ui_dialog.collect_tweet_button.clicked.connect(self.collect_tweet)
        self.ui_dialog.post_tweet_button.clicked.connect(self.post_tweet)
        self.ui_dialog.login_button.clicked.connect(self.login)
        self.ui_dialog.post_stop_button.clicked.connect(self.post_stop)

        # メンバ変数定義
        self.collector = CollectorTweet()
        self.poster = PostTweet()
        self.issuer = ApiIssuer()

        # シグナル
        self.issuer.printThread.connect(self.print_log)
        self.issuer.finished.connect(self.set_api)

        self.collector.printThread.connect(self.print_log)
        self.collector.tweet_shelf_signal.connect(self.insert_db)

        self.poster.printThread.connect(self.print_log)
        self.poster.progress_thread.connect(self.disp_progress)
        self.poster.finish.connect(self.clear_progress_bar)
        self.poster.finish.connect(self.post_stop)
        self.poster.tweet_update.connect(self.update)

        self.timer.timeout.connect(self.poster.start)

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        ui = loader.load(ui_file, self)
        ui_file.close()
        return ui

    def login(self):
        """ログイン処理
        アカウント情報を発行者に設定
        APIキーを発行
        ツイートクラスに発行したAPIを渡す
        """
        self.issuer.set_account(
            self.ui_dialog.form_id.text(),
            self.ui_dialog.form_pw.text())

        self.issuer.start()

    def collect_tweet(self):

        # ツイートを収集する
        self.collector.start()

    def post_tweet(self):
        tweet_ids, reply_ids, contents = self.tweet_db.out_tweet()
        self.poster.set_tweet(
            tweet_ids,
            reply_ids,
            contents)
        self._log_append('ツイート開始')
        self.timer.start(self.ui_dialog.tweet_time.value() * 1000 * 60)

    def post_stop(self):
        self.poster.stop()
        self.timer.stop()
        self._log_append('ツイートを停止しました')

    def _log_append(self, txt):
        dt_now = datetime.datetime.now()
        dt_now_str = dt_now.strftime('%Y-%m-%d %H:%M:%S')

        txt = dt_now_str + ': ' + txt

        if len(self.ui_dialog.log) > MAX_LINE:
            # 最大行より多くのログを表示させる場合は先頭のログを捨てる
            self.ui_dialog.log.pop(0)
        self.ui_dialog.log.append(txt)

    @Slot()
    def clear_progress_bar(self):
        self.ui_dialog.progressBar.setValue(0)

    @Slot(int)
    def disp_progress(self, progress):
        self.ui_dialog.progressBar.setValue(progress)

    @Slot(str)
    def print_log(self, log_str):
        self._log_append(log_str)

    @Slot()
    def set_api(self):
        self.collector.set_api(self.issuer.get_api())
        self.poster.set_api(self.issuer.get_api())

        # ツイートを格納するDBモデルを生成
        me = self.collector.api.me()
        db_name = me.screen_name + '_' + DB_NAME
        self.tweet_db = TweetModel(db_name)
        if not os.path.exists(db_name):
            self.tweet_db.create_db()

    @Slot(list)
    def insert_db(self, tweet_shelf):
        self.tweet_db.insert(tweet_shelf)

    @Slot(str, str)
    def update(self, old_tweet_id, new_tweet_id):
        self.tweet_db.update_tweet(int(old_tweet_id), int(new_tweet_id))

        # DBを更新したタイミングでDBに登録してあるツイートも更新する
        tweet_ids, reply_ids, contents = self.tweet_db.out_tweet()
        self.poster.set_tweet(
            tweet_ids,
            reply_ids,
            contents)


if __name__ == "__main__":
    app = QApplication([])
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec_())
