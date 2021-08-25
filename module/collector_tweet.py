from PySide6.QtCore import Signal
from .tweet import Tweet
import copy


class CollectorTweet(Tweet):
    """ツイート収集クラス

    Args:
        Tweet ([type]): [description]
    """

    # 取得したツイートを送信する必要があるためシグナルを用意
    tweet_shelf_signal = Signal(list)

    def run(self):
        self.restart()
        self.collect()
        self.stop()
        self.finished.emit()

    def collect(self):
        self.printThread.emit('ツイート収集開始!')
        # 最新のツイート200件を収集する
        tweets = self.api.user_timeline(count=200, page=1)

        # ツイートを辞書型リストにするためのテンプレート辞書
        tweet_dict = {
            'tweet_id': '',
            'reply_id': '',
            'content': '',
        }
        tweet_shelf = []

        for tweet in tweets:
            # RTとリプは除外する
            if ("RT @" not in tweet.text[0:4]) and ("@" not in tweet.text[0]):
                tweet_dict['tweet_id'] = tweet.id
                tweet_dict['reply_id'] = tweet.in_reply_to_status_id
                tweet_dict['content'] = tweet.text
                tweet_shelf.append(tweet_dict.copy())

        # リストをそのまま渡すと渡した先で編集した場合に内容が変更されるため
        self.tweet_shelf_signal.emit(copy.deepcopy(tweet_shelf))
        self.printThread.emit('ツイート収集が終了しました!')
