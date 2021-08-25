from PySide6.QtCore import Signal
from .tweet import Tweet
import tweepy


class PostTweet(Tweet):
    """ツイート投稿クラス

    Args:
        Tweet (Tweet): QThreadを継承したTwitterの親クラス
    """
    # ログ表示とDB更新をスレッド処理中に送信する必要がある
    progress_thread = Signal(int)
    tweet_update = Signal(str, str)

    def set_tweet(self, tweet_ids, reply_ids, contents):
        """ツイート内容をセットする
        runメソッドに引数を追加するとスレッド処理にできないためrun前にツイート内容をセットする

        Args:
            tweet_ids (list): ツイートID
            reply_ids (list): リプライ先ツイートID
            contents (list): ツイート内容
        """
        self.tweet_ids = tweet_ids
        self.reply_ids = reply_ids
        self.contents = contents

    def run(self):
        """スレッド処理
        """

        self.restart()
        self.post_tweet()
        self.stop()

    def post_tweet(self):
        """ツイート投稿
        """
        tweet_num = len(self.tweet_ids)
        index = self.counter.get_count()

        tweet_id = self.tweet_ids[index]
        content = self.contents[index]
        reply_id = self.reply_ids[index]

        # ツイート投稿している際にエラーが出る可能性があるため例外処理にしておく
        try:
            status = self.api.update_status(
                content, in_reply_to_status_id=reply_id)

        except tweepy.error.TweepError as e:
            if e.reason == "[{'code': 187, 'message': 'Status is a duplicate.'}]":
                self.printThread.emit('ツイート内容が重複していたのでスキップします')

        # ツイート投稿したことでツイートIDが更新されるので更新しておく
        self.tweet_update.emit(str(tweet_id), str(status.id))

        # 進捗率処理
        progress = int(((index + 1) / tweet_num) * 100)
        self.progress_thread.emit(progress)

        if self.counter.can_count_up(tweet_num - 1):
            # 次のツイートがあればカウントを進めて処理を終える
            self.counter.count_up()
        else:
            # 次のツイートがなければカウントをクリアして処理を終える
            self.printThread.emit('ツイートが終了しました!')
            self.counter.count_clear()
            self.finish.emit()
