import json
import re
import threading
import time

import requests

from src import log
from src.alerts import get_alerts_by_type, TYPE_INSTA
from src.notifications import send_instagram_notification

__users_feeds = {}


class InstagramUserFeed:
    def __init__(self, feed):
        self.userid = feed.get('user_id', None)
        self.username = feed.get('user_username', None)
        self.followers = feed.get('follower', None)
        self.follows = feed.get('follows', None)
        self.media_count = feed.get('media_count', None)
        self.recent_media = feed.get('media', None)
        self.recent_media_ids = feed.get('media_ids', None)


def setup_periodic_scrape():
    for alert in get_alerts_by_type(TYPE_INSTA):
        t = threading.Thread(target=scrape, args=(alert,))
        t.start()


def scrape(alert):
    while True:
        log.info("Sleeping {} seconds to scrape {} instagram alert".format(alert.frequency, alert.name))
        time.sleep(alert.frequency)
        search_new_posts(alert)


def populate_feeds():
    log.info("Populating instagram user's feeds")
    for alert in get_alerts_by_type(TYPE_INSTA):
        for username in alert.users:
            feed = get_user_media(username)
            __users_feeds[feed.userid] = feed


def new_posts(feed):
    if feed.recent_media_ids is None or __users_feeds[feed.userid].recent_media_ids is None and \
            feed.recent_media_ids == __users_feeds[feed.userid].recent_media_ids:
        log.info("No changes detected for user {}".format(feed.username))
    else:
        log.info("Feed changes detected for user {}".format(feed.username))
        __users_feeds[feed.userid] = feed
        return True


def search_new_posts(alert):
    for username in alert.users:
        user_feed = get_user_media(username)
        if new_posts(user_feed):
            send_instagram_notification(user_feed, alert)


def get_user_media(username):
    result = {}
    r = requests.get('https://www.instagram.com/' + username)
    data_search = re.search('<script type="text/javascript">window._sharedData = (.*);</script>', r.text,
                            re.IGNORECASE)
    if data_search:
        tmp = data_search.group(1)
        data = json.loads(tmp)
        try:
            user = data['entry_data']['ProfilePage'][0]['graphql']['user']
            result['user_id'] = user['id']
            result['user_username'] = user['username']
            result['follower'] = user['edge_followed_by']['count']
            result['follows'] = user['edge_follow']['count']
            result['media_count'] = user['edge_owner_to_timeline_media']['count']
            result['media'] = []
            result['media_ids'] = set()

            for post in user['edge_owner_to_timeline_media']['edges']:
                post = {
                    'id': post['node']['id'],
                    'timestamp': post['node']['taken_at_timestamp'],
                    'is_video': post['node']['is_video'],
                    'caption': post['node']['edge_media_to_caption']['edges'][0]['node']['text'] if
                    post['node']['edge_media_to_caption']['edges'] else "Could not find caption",
                    'thumbnail': post['node']['thumbnail_src'],
                    'image': post['node']['display_url']
                }
                result['media'].append(post)
                result['media_ids'].add(post['id'])

        except KeyError as exception:
            log.error('Unexpected response retrieving {} info: {!r}\n\nData: {}'.format(username, exception, data))
            return InstagramUserFeed(result)

        log.info('Scraped ' + result['user_username'] + ' and ' + str(len(result['media'])) + ' posts')
    else:
        log.error('Failed to extract meta-information from HTML page')
    return InstagramUserFeed(result)
