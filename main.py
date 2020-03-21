from threading import Thread

import tweepy

from src import log
from src.alerts import get_alerts_by_type, TYPE_TWITTER, TYPE_INSTA
from src.instagram import populate_feeds, setup_periodic_scrape
from src.notifications import setup_periodic_notifications
from src.twitter import auth, get_user_ids, MyStreamListener


def instagram_thread():
    populate_feeds()
    setup_periodic_scrape()


def main():
    if get_alerts_by_type(TYPE_INSTA):
        log.info("*** STARTING INSTAGRAM MONITORING THREAD***")
        t = Thread(target=instagram_thread, daemon=True)
        t.start()
    if get_alerts_by_type(TYPE_TWITTER):
        log.info("*** STARTING TWITTER MONITORING ***")
        api = auth()
        stream_listener = MyStreamListener()
        stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
        stream.filter(follow=get_user_ids(api), is_async=True, stall_warnings=True)
        setup_periodic_notifications()


if __name__ == "__main__":
    main()
