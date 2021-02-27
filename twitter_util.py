from __future__ import annotations

import random
import tweepy
from my_token import *
import pickle
import glob
from os import path

DUMPS_DIR = "./dumps"


class TwitterUtil:

    tweet_urls = []

    def __init__(self):
        auth = tweepy.OAuthHandler(TW_CONSUMER_TOKEN, TW_CONSUMER_SECRET)
        auth.set_access_token(TW_ACCESS_TOKEN, TW_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)

        self.api = api

    def load_dumps(self):

        accounts = set(
            path.basename(d).replace(".dmp", "")
            for d in glob.glob(f"{DUMPS_DIR}/*.dmp")
        )

        for account in accounts:
            self.load_dump(account, accounts)

        random.shuffle(self.tweet_urls)

    def load_dump(self, account: str, reply_white_set: set[str]):

        with open(f"{DUMPS_DIR}/{account}.dmp", "rb") as f:
            tweets = pickle.load(f)

        print(account, len(tweets))

        for t in tweets:
            user_mentions = t.entities["user_mentions"]
            mentions = set(m["screen_name"] for m in user_mentions)

            if not mentions or not (mentions - reply_white_set):
                self.tweet_urls.append(f"https://twitter.com/{account}/status/{t.id}")

    def load_random_embed_html(self) -> str:
        idx = random.randrange(len(self.tweet_urls))
        url = self.tweet_urls[idx]

        # embed = self.api.get_oembed(url, lang="ja-JP", theme="dark", omit_script=True)
        # return embed["html"]
        return f"""<blockquote class="twitter-tweet" data-lang="ja-JP" data-theme="dark"><a href="{url}"></a></blockquote>"""

    def timeline_to_dump(self, account: str):

        all_tweets = []

        for tweet in tweepy.Cursor(
            self.api.user_timeline,
            screen_name=account,
            trim_user=False,
            exclude_replies=False,
            include_rts=False,
        ).items():
            all_tweets.append(tweet)

        with open(f"{DUMPS_DIR}/{account}.dmp", "wb") as f:
            pickle.dump(all_tweets, f)


if __name__ == "__main__":

    util = TwitterUtil()

    # for account in [
    #     "aoshima_rokusen",
    #     "hikari_miyaman",
    #     "iwanaga_sizu",
    #     "kirakira_nanano",
    #     "strawberry_fore",
    #     "riya_hoshino",
    #     "reiko_blueislan",
    #     "retanihoshino",
    #     "actress_nanano",
    #     "castleseven_aya",
    #     "waruichigo",
    #     "iori_heartfield",
    # ]:
    #     util.timeline_to_dump(account)

    util.load_dumps()
    print(util.load_random_embed_html())
    print(util.load_random_embed_html())
    print(util.load_random_embed_html())
