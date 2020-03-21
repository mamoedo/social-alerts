import re

import tweepy
from tweepy import TweepError

from src import alerts
from src.alerts import get_alerts_by_username
from src.notifications import *


def auth():
    authentication = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    authentication.set_access_token(config.access_token, config.access_token_secret)
    api = tweepy.API(authentication)
    log.info('API authentication completed')
    return api


def get_user_ids(api):
    users_ids = []
    missing_users = []
    log.info('Getting users info')
    for user in alerts.get_users_list(TYPE_TWITTER):
        log.debug('Getting {} user info'.format(user))
        try:
            users_ids.append(api.get_user(user).id_str)
        except TweepError as e:
            if e.api_code == 89:
                log.error("Credentials error... exiting")
                exit(-89)
            missing_users.append(user)
    if missing_users:
        log.warning("The following users {} do not exist.".format(missing_users))
    log.info('Users info retrieved')
    return users_ids


def _user_in_list(username, _list):
    for user in _list:
        if user.lower() == username:
            return True
    return False


class MyStreamListener(tweepy.StreamListener):

    def on_exception(self, exception):
        """Called when an unhandled exception occurs."""
        log.error("Exception occurred when searching for new posts: {!r}".format(exception))
        exit(-1)

    def on_status(self, tweet):
        tweet = Tweet(tweet)
        if _user_in_list(tweet.get_username().lower(), alerts.get_users_list(TYPE_TWITTER)):
            alert_list = get_alerts_by_username(tweet.get_username())
            log.debug("{}: {}".format(tweet.get_alias(), tweet.get_text()))
            for alert in alert_list:
                if alert.type == TYPE_TWITTER:
                    if all([alert.replies or not tweet.is_reply(),
                            alert.retweets or not tweet.is_retweet(),
                            not alert.whitelist or tweet.contains_word(alert.whitelist, alert.whitelist_regex),
                            not tweet.contains_word(alert.blacklist, alert.blacklist_regex)]):
                        if alert.frequency:
                            create_pending_notification(TwitterNotification(tweet, alert))
                        else:
                            send_twitter_notification(TwitterNotification(tweet, alert))


class Tweet:
    def __init__(self, status):
        self.__tweet = status

    def get_tweet_object(self):
        return self.__tweet

    def get_text(self):
        if hasattr(self.__tweet, 'extended_tweet'):
            return self.__tweet.extended_tweet["full_text"]
        else:
            return self.__tweet.text

    def contains_word(self, wordlist, regex):
        return [word for word in wordlist if
                re.findall(regex.format(word), self.get_text(), flags=re.IGNORECASE)]

    def is_retweet(self):
        return self.__tweet.text.startswith("RT @")

    def is_reply(self):
        return self.__tweet.text.startswith("@")

    def get_username(self):
        return self.__tweet.user.screen_name

    def get_alias(self):
        return self.__tweet.user.name

    def get_id(self):
        return self.__tweet.id_str

    def get_created_at(self):
        return self.__tweet.created_at
