from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

# MetaDataの機能や関連付けの機能を持つBaseオブジェクトを作成
Base = declarative_base()


class Tweet(Base):
    __tablename__ = 'tweets'

    tweet_id = Column(Integer, primary_key=True)
    reply_id = Column(Integer)
    content = Column(String)


class TweetModel():
    def __init__(self, dbname) -> None:
        self.engine = create_engine(
            'sqlite:///' + dbname, echo=True)

    def create_db(self):
        Base.metadata.create_all(self.engine)

    def insert(self, tweet_shelf):
        session_class = sessionmaker(bind=self.engine)
        session = session_class()

        # 取得したツイートの内、DBに既に格納してあるツイートは除く
        tweet_shelf = self._delete_duplicate(session, tweet_shelf)

        if tweet_shelf is not None:
            statement = Tweet.__table__.insert().values(tweet_shelf)
            session.execute(statement)
            session.commit()
        session.close()

    def _delete_duplicate(self, session, tweet_shelf):
        db_tweet_ids = session.query(Tweet.tweet_id).all()
        db_tweet_contents = session.query(Tweet.content).all()

        # modelオブジェクトからintのリストに変換する
        db_tweet_ids = [tweet_obj._data[0] for tweet_obj in db_tweet_ids]

        if tweet_shelf is not None:
            for i in reversed(range(len(tweet_shelf))):
                tweet_dict = tweet_shelf[i]
                # 同一ツイートをDBに保存しないための措置
                # tweet_idと内容の2パターンが存在する
                if tweet_dict['tweet_id'] in db_tweet_ids:
                    del tweet_shelf[i]

                if tweet_dict['content'] in db_tweet_contents:
                    del tweet_shelf[i]
            return tweet_shelf
        else:
            return None

    def out_tweet(self):
        session_class = sessionmaker(bind=self.engine)
        session = session_class()

        tweet_ids_obj = session.query(Tweet.tweet_id).all()
        reply_ids_obj = session.query(Tweet.reply_id).all()
        contents_obj = session.query(Tweet.content).all()

        # tweet classからint,stringに変換する
        tweet_ids = [tweet_id_obj._data[0] for tweet_id_obj in tweet_ids_obj]
        reply_ids = [reply_id_obj._data[0] for reply_id_obj in reply_ids_obj]
        contents = [content_obj._data[0] for content_obj in contents_obj]

        session.close()
        return tweet_ids, reply_ids, contents

    def update_tweet(self, old_tweet_id, new_tweet_id):
        session_class = sessionmaker(bind=self.engine)
        session = session_class()

        # ツイートしたことによってツイートIDは変更されるのでDBに登録してあるIDも更新する
        tweets = session.query(Tweet).filter(
            Tweet.tweet_id == old_tweet_id)
        for tweet in tweets:
            tweet.tweet_id = new_tweet_id
        session.commit() #いらないかも

        reply_tweets = session.query(Tweet).filter(
            Tweet.reply_id == old_tweet_id)
        for reply_tweet in reply_tweets:
            print(reply_tweet.reply_id)
            reply_tweet.reply_id = new_tweet_id
            print(reply_tweet.reply_id)

        session.commit()
        session.close()
